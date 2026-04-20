import base64
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from ultralytics import YOLO
from pathlib import Path
import json

app = FastAPI()

# Caminhos baseados na sua estrutura
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "best.pt"
HTML_PATH = BASE_DIR.parent / "frontend" / "index.html"

# Carrega o seu modelo treinado. Se não achar, usa o nano para não quebrar.
if MODEL_PATH.exists():
    model = YOLO(str(MODEL_PATH))
    print(f"✅ Modelo customizado carregado: {MODEL_PATH}")
else:
    model = YOLO("yolov8n.pt")
    print("⚠️ best.pt não encontrado no backend/. Usando yolov8n.pt")

# Configurações de Alerta (Buffer de 10 frames para evitar falsos positivos)
ALERT_THRESHOLD_FRAMES = 10  
violation_counter = 0

@app.get("/")
async def get():
    if HTML_PATH.exists():
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Erro: index.html não encontrado no frontend/</h1>", status_code=404)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global violation_counter
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Decodificação da imagem vinda do navegador
            try:
                encoded_data = data.split(",")[1]
                nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                continue

            # Inferência (Ajuste o 'conf' conforme necessário para sua precisão)
            results = model(frame, conf=0.5, verbose=False)[0]
            
            detections = []
            has_person = False
            has_mask = False

            for box in results.boxes:
                coords = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                label = model.names[class_id]
                
                detections.append({
                    "x1": int(coords[0]), "y1": int(coords[1]),
                    "x2": int(coords[2]), "y2": int(coords[3]),
                    "confidence": conf,
                    "class_name": label
                })
                
                # Lógica de detecção para o alerta (ajuste os nomes das classes se forem diferentes)
                if label == 'person': has_person = True
                if label == 'cell phone': has_mask = True # O celular vai "fingir" que é uma mascara
            # Lógica de Alerta Consecutivo
            alerts = []
            if has_person and not has_mask:
                violation_counter += 1
                if violation_counter >= ALERT_THRESHOLD_FRAMES:
                    alerts.append({"message": "🚨 ALERTA: Pessoa sem máscara detectada!"})
            else:
                # Diminui o contador gradualmente se a situação se normalizar
                violation_counter = max(0, violation_counter - 1)

            await websocket.send_json({
                "detections": detections,
                "alerts": alerts
            })

    except WebSocketDisconnect:
        violation_counter = 0
    except Exception as e:
        print(f"Erro no WebSocket: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)