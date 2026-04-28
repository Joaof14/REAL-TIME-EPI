# REAL-TIME-EPI — Detecção de Máscaras (MVP)

Projeto MVP para detecção em tempo real do uso de máscaras faciais (EPI) com comunicação WebSocket entre frontend (navegador) e backend (FastAPI + YOLOv8).

## Resumo rápido
- Backend: Python + FastAPI, endpoint WebSocket `/ws` para receber frames e retornar detecções JSON.
- Modelo: `backend/best.pt` (se presente) — caso contrário, o projeto faz fallback para `yolov8n.pt` incluído.
- Frontend: `frontend/index.html` — captura vídeo, envia frames via WebSocket e desenha bounding boxes em um `canvas`.

Detalhes técnicos e justificativas estão em `docs/tech-report.md` e `docs/project-report.md`.

## Execução (passo a passo)

1. Instalar dependências e criar ambiente

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Rodar o servidor

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Abrir a interface

Abra no navegador: http://localhost:8000

A interface solicitará permissão para usar a câmera. Clique em "Ligar Câmera".

## Parâmetros relevantes (onde ajustar)
- `ALERT_THRESHOLD_FRAMES` (em `backend/main.py`): número de frames consecutivos com violação para disparar um alerta (valor atual: 4).
- `conf` na inferência (linha que chama `model(frame, conf=0.50, ...)`): limiar de confiança do detector (valor atual: 0.50).
- `sendInterval` no frontend (`index.html`): intervalo entre envios de frames ao servidor (valor atual: 150 ms → ~6–7 FPS).
- Qualidade do JPEG no `captureCanvas.toDataURL('image/jpeg', 0.6)` controla compressão e banda (0.6 atual).

## Referência do modelo
O peso `best.pt` utilizado neste repositório tem origem em um trabalho disponível no Kaggle (usado como base pelo projeto). Referência: https://www.kaggle.com/code/cubeai/facemask-detection-with-yolov8/output

Considere consultar `docs/tech-report.md` para detalhes sobre versões de bibliotecas e implicações de licenciamento.

## Estrutura resumida do repositório

- backend/
	- `main.py` — servidor FastAPI + WebSocket + inferência YOLO
	- `requirements.txt` — dependências Python
	- `best.pt` — (opcional) pesos do modelo
- frontend/
	- `index.html` — interface web
- docs/
	- `tech-report.md`, `project-report.md` (novos)

## Notas rápidas de operação e segurança
- Para produção, rode o serviço em servidor com GPU (se disponível) ou configure aceleração por TensorRT/ONNX.
- Proteja o endpoint WebSocket com autenticação ou deploy via rede interna apenas.

---
Para detalhes completos sobre cada tecnologia, limiares e lógica de alertas, veja: [docs/tech-report.md](docs/tech-report.md) e [docs/project-report.md](docs/project-report.md).
