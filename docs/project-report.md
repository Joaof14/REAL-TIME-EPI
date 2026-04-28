# Project Report — Detalhes do Projeto

Este documento descreve o funcionamento interno do MVP, fluxo de dados, parâmetros críticos (limiares), criação e funcionamento do WebSocket, e recomendações para ajustes.

## 1. Arquitetura geral

- Frontend (navegador): captura vídeo via `getUserMedia`, converte frame em JPEG e envia via WebSocket.
- Backend (FastAPI): endpoint WebSocket `/ws` recebe frames, decodifica com OpenCV, passa para o modelo YOLOv8 para inferência e envia resultados JSON de volta ao cliente.

Fluxo simplificado:

1. Usuario clica "Ligar Câmera" no frontend.
2. Frontend começa a enviar frames como base64 JPEG a cada 150 ms.
3. Backend recebe texto do WebSocket, extrai o payload base64, decodifica para `numpy` e reconstrói o frame com `cv2.imdecode`.
4. O frame é passado ao `model(frame, conf=0.50, verbose=False)[0]` para obter `results`.
5. Backend extrai `boxes`, `conf` e `cls`, converte em estruturas (x1,y1,x2,y2, confidence, class_name) e aplica a lógica de alerta.
6. Backend envia JSON: `{ "detections": [...], "alerts": [...] }`.
7. Frontend desenha bounding boxes no `canvas` e adiciona alertas no painel.

## 2. Código relevante (explicação)

- Carregamento do modelo (em `backend/main.py`):

  - Se `backend/best.pt` existe, carrega com `YOLO(str(MODEL_PATH))`.
  - Caso contrário faz fallback para `yolov8n.pt`.

- Inferência por frame:

  - `results = model(frame, conf=0.50, verbose=False)[0]`
  - `conf=0.50` é o limiar de confiança mínimo para caixas retornadas.

- Conversão de frame (no backend):

  - Recebe string base64 (formato `data:image/jpeg;base64,...`).
  - Converte com `base64.b64decode`, `np.frombuffer(..., np.uint8)`, `cv2.imdecode`.

## 3. Lógica de alerta (detalhada)

- Parâmetros principais:
  - `ALERT_THRESHOLD_FRAMES = 4` — número de frames consecutivos com detecção de violação para gerar alerta.
  - `violation_counter` — contador que incrementa quando há detecção de violação; decresce gradualmente quando normalizado.
  - `last_alert_time` e cooldown de ~1 segundo para evitar spams de alertas repetidos.

- Como funciona na prática:
  - Para cada frame, se existir pelo menos uma detecção cujo `class_name` não seja `"Pessoa com máscara"`, a variável `alerta_ativado` é marcada como `True`.
  - Se `alerta_ativado` for `True`, `violation_counter += 1`.
  - Quando `violation_counter >= ALERT_THRESHOLD_FRAMES` e passou tempo suficiente desde o último alerta (`current_time - last_alert_time >= 1.0`), um alerta é gerado e enviado.
  - Quando `alerta_ativado` é `False`, o contador é reduzido com `violation_counter = max(0, violation_counter - 1)`.

Observação: essa estratégia de buffer reduz falsos positivos ocasionais (movimentos, detecções momentâneas), enquanto mantém sensibilidade a violações persistentes.

## 4. WebSocket — criação e comportamento

- Rota definida: `@app.websocket("/ws")`
- Fluxo no servidor:
  1. `await websocket.accept()` — aceita a conexão.
  2. Loop `while True`: `data = await websocket.receive_text()` lê a string enviada pelo cliente.
  3. Processa o payload e chama o modelo.
  4. `await websocket.send_json({...})` envia resposta estruturada.
  5. Tratamento de desconexão com `WebSocketDisconnect` e captura genérica de exceções para log.

Recomendações para robustez do WebSocket:

- Validar origem (CORS / header) e autenticação antes de aceitar a conexão.
- Implementar heartbeat/ping-pong se for necessário detectar conexões mortas.
- Colocar limite máximo de tamanho de payload por mensagem (para proteger contra DoS via frames gigantes).

## 5. Performance e latência

- Envio de frames a cada 150 ms com qualidade JPEG 0.6 dá aproximadamente 6–7 FPS de inferência por conexão. A latência total depende do hardware e da carga de inferência.
- Em CPU, a inferência YOLOv8 pode ser lenta; usar GPU reduz latência significativamente.

Possíveis otimizações:

- Reduzir resolução de envio (por exemplo, enviar 320x240 em vez de 640x480).
- Fazer pré-processamento no cliente (crop de faces via face-detection leve) e enviar apenas ROIs.
- Usar modelos menores ou quantizados (YOLOv8n, ONNX quantizado) para inferência em CPU.

## 6. Ajustes finos e testes sugeridos

- Para reduzir falsos negativos (não detectar sem máscara): diminuir `conf` (ex.: 0.40) — aumenta falsos positivos.
- Para reduzir falsos positivos: aumentar `conf` (ex.: 0.60) e/ou aumentar `ALERT_THRESHOLD_FRAMES`.
- Testar em diferentes condições de iluminação, ângulos, múltiplas pessoas e com/sem acessórios (óculos, lenços).

## 7. Escala e arquitetura recomendada para produção

- Separar recepção de frames do pipeline de inferência (fila ou tópico): o WebSocket apenas coloca tarefas na fila; workers consomem e executam inferência.
- Usar pool de processos ou serviços dedicados com GPUs.
- Persistir alertas em um banco de dados (ex.: PostgreSQL) se for necessário histórico e auditoria.

## 8. Logs e monitoração

- Registrar métricas de latência, taxa de frames por cliente, e número de alertas por intervalo para avaliar comportamento em produção.
- Expor métricas via Prometheus se necessário.


