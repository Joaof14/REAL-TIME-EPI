# Relatório Técnico Unificado — Tecnologias e Uso no EPI-Watch

Este documento unifica os relatórios técnicos existentes e descreve escolhas tecnológicas, integração entre componentes, parâmetros operacionais, práticas de treinamento, testes, segurança e recomendações para produção.

## Sumário executivo

- Backend: `FastAPI` + `Uvicorn` servindo a interface e o endpoint WebSocket `/ws` (veja `backend/main.py`).
- Inferência: Ultralytics YOLOv8 (`ultralytics`) — carrega `backend/best.pt` quando presente, com fallback para `yolov8n.pt`.
- Frontend: cliente web em `frontend/index.html` captura câmera, envia frames via WebSocket em DataURL JPEG e desenha bounding boxes com `canvas`.

Referência do modelo base usado neste repositório (origem do `best.pt`): https://www.kaggle.com/code/cubeai/facemask-detection-with-yolov8/output

> Observação: verifique a licença e metadados do modelo no Kaggle antes de redistribuir o peso.

## Arquitetura e fluxo de dados

1. O navegador captura frames via `getUserMedia` e converte o frame para DataURL JPEG com qualidade 0.6 (`captureCanvas.toDataURL('image/jpeg', 0.6)`) — ver `frontend/index.html`.
2. O cliente envia a string DataURL pelo WebSocket para `ws://<host>/ws` a cada ~150 ms (`setInterval(sendFrame, 150)`).
3. O backend decodifica o DataURL (split "," + `base64.b64decode`), reconstrói o frame com `cv2.imdecode` e executa inferência: `model(frame, conf=0.50, verbose=False)[0]`.
4. O backend extrai boxes, confiança e classe, aplica a lógica de alerta e responde com JSON contendo `detections` e `alerts`.

Exemplo de resposta:

```json
{
  "detections": [
    {"x1": 12, "y1": 34, "x2": 120, "y2": 200, "confidence": 0.93, "class_name": "Pessoa com máscara"}
  ],
  "alerts": []
}
```

## Dependências e versões

Dependências atuais listadas em `backend/requirements.txt`:

- `fastapi==0.115.11`
- `uvicorn[standard]==0.34.0`
- `opencv-python==4.11.0.86`
- `ultralytics==8.3.96`
- `numpy>=1.23.0,<2.1.2`
- `python-multipart==0.0.20`

Recomendações: fixe versões em produção e gere um `requirements.txt` reproduzível a partir do ambiente virtual.

## Papel de cada componente

- FastAPI + Uvicorn: serve a UI e o WebSocket `/ws` para comunicação em tempo real.
- Ultralytics YOLO: carrega o checkpoint `.pt` e realiza a inferência por frame.
- OpenCV: decodifica o JPEG enviado (base64 → bytes → np.uint8 → `cv2.imdecode`) e manipula frames.
- Frontend (JS): captura, codifica e envia frames; também desenha boxes e apresenta histórico de alertas.

## Parâmetros operacionais e onde ajustá-los

- `ALERT_THRESHOLD_FRAMES` (em `backend/main.py`): número de frames consecutivos com violação para gerar um alerta (atual: 4 na versão do projeto).
- `conf` na chamada ao modelo (`model(frame, conf=0.50, ...)`): limiar de confiança para considerar boxes (atual: 0.50).
- `sendInterval` no frontend (`index.html`): intervalo entre envios de frames em ms (atual: 150 ms).
- Compressão JPEG em `captureCanvas.toDataURL('image/jpeg', 0.6)`: controla qualidade/tamanho do payload (0.6 atual).

Ajustes finos:
- Diminuir `conf` aumenta sensibilidade (menos falsos negativos) mas aumenta falsos positivos.
- Aumentar `ALERT_THRESHOLD_FRAMES` reduz falsos positivos pontuais e aumenta a robustez a detecções temporárias.

## Treinamento e práticas sugeridas

- Modelo base: Ultralytics YOLOv8 (PyTorch `.pt`).
- Sugestões de treino (se for retrain/fine-tune): `img=640` ou `1280`, `epochs=50-200`, `batch_size=16-32`, `lr` inicial ~0.01, augmentations controlados (Albumentations ou internas do `ultralytics`).
- Métricas: `mAP@0.5`, curvas PR, matriz de confusão por classe.

Registre metadados do artefato (`sha256` do peso, dataset usado, splits, hiperparâmetros, versões de bibliotecas) para reprodutibilidade.

## Testes e cenários de avaliação

- Cenários essenciais: máscara correta, máscara incorreta (nariz/cobertura parcial), sem máscara, múltiplas pessoas, iluminação variada e ângulos.
- Métricas de aceitação sugeridas: precisão >85% em `Com Máscara` e recall alto em `Sem Máscara` (evitar falsos negativos).

## Performance e otimização

- Em CPU, prefira modelos menores (YOLOv8n) ou conversões para ONNX/quantização.
- Em GPUs, utilize PyTorch/CUDA com `ultralytics` para throughput superior.
- Otimizações: reduzir resolução de envio, enviar ROIs do cliente, usar worker pool para inferência assíncrona.

## WebSocket — criação, robustez e recomendações

- Rota: `@app.websocket("/ws")` no `backend/main.py`.
- Ao aceitar conexões, validar origem/autenticação antes de processar frames.
- Recomendações: heartbeat/ping-pong, limite de tamanho de payload, e separar recepção de frames da inferência via filas para não bloquear o servidor.

## Segurança, privacidade e conformidade

- Use `wss://` em produção e autentique clientes (tokens/JWT) quando exposto publicamente.
- Evite persistir frames sem consentimento; se necessário, armazene apenas hashes/anotações e mantenha controles de acesso.

## Observabilidade e monitoração

- Registre métricas: latência de inferência, fps por cliente, contagem de alertas, conexões ativas.
- Exponha métricas para Prometheus e registre logs estruturados para auditoria.

## Deploy e operações

- Dockerfile sugerido: `python:3.11-slim`, instalar `requirements.txt`, copiar `backend/` e expor porta 8000 executando `uvicorn`.
- Para escala: orquestrar com Kubernetes, HPA por CPU/GPU, e separar inferência em workers com filas (Redis/RabbitMQ) se necessário.

## Observações finais sobre o modelo utilizado

- O `best.pt` usado foi obtido a partir do link no Kaggle citado acima; confirme licença e atribuições antes do reuso.
- Mantenha versionamento claro para modelos (`best_v1.pt`, `best_v2.pt`) e changelog associado.

---

Referências e arquivos úteis:

- Código do servidor: `backend/main.py`
- Frontend: `frontend/index.html`
- Dependências: `backend/requirements.txt`

---

Se desejar, posso:
- Adicionar benchmarks (CPU vs GPU) automatizados;
- Gerar um `Dockerfile` e `docker-compose.yml` de exemplo;
- Incluir um `docs/kaggle_model_reference.md` com metadados do `best.pt`.
