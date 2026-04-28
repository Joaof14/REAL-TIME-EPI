 # Relatório Técnico: Tecnologias e Uso no EPI-Watch (versão aprofundada)

Este documento aprofunda as escolhas tecnológicas, integração entre componentes, parâmetros operacionais, e recomendações para auditoria técnica e produção.

## Sumário executivo (rápido)

- Backend: `FastAPI` + `Ultralytics YOLOv8` para inferência; ponto de entrada em [backend/main.py](backend/main.py#L1-L200). O peso do modelo integrado foi obtido de uma fonte pública no Kaggle — adicione URL e metadados em `docs/` para atribuição e rastreabilidade.
- Frontend: cliente web que captura a câmera e envia frames via WebSocket para `/ws`.
- Comunicação: WebSocket (baixa latência); formato: DataURL JPEG (base64) enviado do cliente, resposta JSON com `detections` e `alerts`.

## Arquitetura e fluxo de dados

1. O navegador captura frames via `getUserMedia` e converte o frame para DataURL JPEG com qualidade 0.6 (`captureCanvas.toDataURL('image/jpeg', 0.6)`). (ver [frontend/index.html](frontend/index.html#L1-L200)).
2. O cliente envia a string DataURL inteira pelo WebSocket para `ws://<host>/ws` a cada ~150ms (`setInterval(sendFrame, 150)`).
3. O backend decodifica o DataURL (split "," e base64 decode), reconstrói o frame com OpenCV e executa inferência via Ultralytics YOLO: `model(frame, conf=0.50)` (ver [backend/main.py](backend/main.py#L1-L200)).
4. O backend envia resposta JSON com chave `detections` (lista de boxes, confiança e nome de classe) e `alerts` (lista com mensagens de alerta quando aplicável).

Exemplo de payload enviado pelo cliente (abreviado):

```json
"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
```

Exemplo de resposta do servidor:

```json
{
	"detections": [
		{"x1": 12, "y1": 34, "x2": 120, "y2": 200, "confidence": 0.93, "class_name": "Pessoa com máscara"}
	],
	"alerts": []
}
```

## Código e parâmetros críticos

- Arquivo principal do servidor: [backend/main.py](backend/main.py#L1-L200). Pontos importantes:
	- `MODEL_PATH` e fallback para `yolov8n.pt` — substitua `backend/best.pt` para trocar o modelo. Mantenha um arquivo de metadados (ex.: `docs/kaggle_model_reference.md`) contendo: URL do Kaggle, versão, autor/owner, licença e o hash (sha256) do arquivo de pesos.
	- `ALERT_THRESHOLD_FRAMES` (default 10) — controla quantos frames consecutivos são necessários para acionar um alerta.
	- Inferência: `model(frame, conf=0.50, verbose=False)[0]` — o parâmetro `conf` define limiar de confiança mínima para considerar boxes.
	- Formato de saída: cada detecção contém coordenadas inteiras, `confidence` float e `class_name` string.

- Arquivo cliente: [frontend/index.html](frontend/index.html#L1-L200). Pontos importantes:
	- Intervalo de envio: 150ms por padrão (`setInterval(sendFrame, 150)`). Ajustar reduz/altera latência e carga.
	- Qualidade JPEG: `0.6` (trade-off entre tamanho e qualidade).

## Dependências e versões (ambiente)

- `requirements.txt` (backend): lista principal de dependências — ver [backend/requirements.txt](backend/requirements.txt#L1-L50).
	- fastapi==0.115.11
	- uvicorn[standard]==0.34.0
	- opencv-python==4.11.0.86
	- ultralytics==8.3.96
	- numpy>=1.23.0,<2.1.2

Recomendações: fixar versões de `ultralytics` e `opencv` em ambientes de produção e utilizar um `requirements.txt` gerado por ambiente virtual consistente.

## Treinamento do modelo (práticas e hiperparâmetros sugeridos)
-
- Observação: o modelo atualmente integrado foi obtido de um repositório/competição no Kaggle. Se for realizar fine-tune ou retrain, registre claramente a versão base, os dados usados e gere novos metadados para o artefato resultante.

- Base: Ultralytics YOLOv8 (PyTorch). Formato do modelo: `.pt` (PyTorch checkpoint).
- Exemplo de configurações iniciais de treino (sugestão):
	- Imagem: `img=640` ou `img=1280` se a câmera permitir.
	- Épocas: `epochs=50-200` dependendo do dataset.
	- Batch size: 16-32 (ajustar conforme GPU/VRAM disponível).
	- Learning rate: partir de `lr=0.01` com scheduler padrão do YOLOv8.
	- Augmentations: rotações leves, flip horizontal, variaçõe sde brilho/contraste, desfoque gaussiano, corte aleatório. Use `Albumentations` ou as opções internas do `ultralytics`.

Validação e métricas:

- Usar `mAP@0.5` e curvas PR por classe.
- Acompanhar matriz de confusão e exemplos de falsos positivos/negativos em cenários reais.

## Testes e Cenários de Avaliação

- Casos essenciais:
	- Pessoas com máscara corretamente posicionada.
	- Pessoas com máscara cobrindo só o queixo/nariz (máscara incorreta).
	- Pessoas sem máscara.
	- Variações de iluminação (externa, interna), múltiplas pessoas no mesmo frame e ângulos laterais.

- Métricas de aceitação: precisão mínima por classe (ex.: >85% em `Com Máscara`), recall aceitável em `Sem Máscara` para evitar falsos negativos.

## Performance e otimização de inferência

- Em CPU, YOLOv8 nano/pico oferecem latências aceitáveis, mas para throughput maior, usar GPU com PyTorch/CUDA.
- Para produção em CPU ou edge devices, converter o modelo para ONNX e usar TensorRT (NVIDIA) ou OpenVINO (Intel) conforme hardware.
- Perfil recomendado: medir fps de inferência, tempo total (rede + decodificação + inferência + serialização). Ajustar `sendInterval` e `conf` para balancear carga.

## Segurança, privacidade e conformidade

- Arquitetura por padrão não armazena frames; apenas metadados de detecção são trafegados. Documente essa decisão para auditoria de privacidade.
- Recomendação de produção:
	- Habilitar TLS para transportes (`wss://`) e usar certificado válido.
	- Autenticação/Autorização do endpoint WebSocket quando exposto em redes públicas.
	- Logging mínimo para auditoria (eventos, timestamps e hash anônimo do cliente) sem armazenar imagens pessoais.

## Observabilidade e monitoração

- Registre métricas essenciais: conexões WebSocket abertas/fechadas, taxa de frames recebidos por cliente, latência média de inferência, contagem de alertas gerados.
- Expor métricas via endpoint `/metrics` (Prometheus) ou logs estruturados para análise.

## Boas práticas operacionais

- Versionar modelos: mantenha histórico de `best_v1.pt`, `best_v2.pt` com changelog da base de dados usada.
- Testes A/B: ao atualizar modelo, rodar validação em paralelo e comparar métricas antes do switch.
- Backup dos pesos e scripts de treinamento em repositório privado ou storage com controle de acesso.

## Trocar configuração e tuning rápido

- Para alterar limiar de alerta (frames): edite `ALERT_THRESHOLD_FRAMES` em [backend/main.py](backend/main.py#L1-L200).
- Para ajustar o limiar de confiança da inferência, altere o argumento `conf` na chamada do modelo em [backend/main.py](backend/main.py#L1-L200).

## Deploy e recomendações finais

- Contêiner: criar `Dockerfile` com base `python:3.11-slim`, instalar `requirements.txt`, copiar `backend/` e expor porta 8000 com `uvicorn`.
- Escala: usar orquestrador (Kubernetes) com HPA baseado em CPU/GPU e rotas de health/readiness.
- Otimização de custos: rodar inferência em instâncias com GPU apenas quando necessário; para pequenos deployments, CPU com modelo otimizado (ONNX/TensorRT) pode ser suficiente.

---

Referências rápidas:

- Código do servidor: [backend/main.py](backend/main.py#L1-L200)
- Frontend: [frontend/index.html](frontend/index.html#L1-L200)
- Dependências: [backend/requirements.txt](backend/requirements.txt#L1-L50)

---

Para mais detalhes técnicos sobre treinamento e scripts, veja os notebooks em `notebooks/` e os documentos em `docs/`.
