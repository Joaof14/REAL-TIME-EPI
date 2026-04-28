import base64
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from ultralytics import YOLO
from pathlib import Path
import json
import time

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "best.pt"
HTML_PATH = BASE_DIR.parent / "frontend" / "index.html"


CLASS_NAMES = {
    0: "Uso incorreto de máscara",
    1: "Pessoa com máscara"
}


# Carrega o modelo treinado. Se não achar, usa o nano para não quebrar.
if MODEL_PATH.exists():
    model = YOLO(str(MODEL_PATH))
    print(f"✅ Modelo customizado carregado: {MODEL_PATH}")
else:
    model = YOLO("yolov8n.pt")
    print("⚠️ best.pt não encontrado no backend/. Usando yolov8n.pt")

# Configurações de Alerta (Buffer de  frames para evitar falsos positivos)
 


@app.get("/")
async def get():
    if HTML_PATH.exists():
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Erro: index.html não encontrado no frontend/</h1>", status_code=404)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ALERT_THRESHOLD_FRAMES = 4 
    violation_counter = 0
    last_alert_time = 0
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                encoded_data = data.split(",")[1]
                nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                continue

    
            results = model(frame, conf=0.50, verbose=False)[0]
            
            detections = []
            alerta_ativado = False 

            for box in results.boxes:
                coords = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                
            
                label = CLASS_NAMES.get(class_id, model.names.get(class_id, "Desconhecido"))
    
                detections.append({
                    "x1": int(coords[0]), "y1": int(coords[1]),
                    "x2": int(coords[2]), "y2": int(coords[3]),
                    "confidence": conf,
                    "class_name": label
                })
                
                # --- LÓGICA DE ALERTA CORRIGIDA ---
                if label == "Pessoa com máscara":
                    alerta_ativado = False
                else:
                    alerta_ativado = True
                # ----------------------------------

            # Lógica de Alerta Consecutivo
            alerts = []
            current_time = time.time()
            if alerta_ativado:
                violation_counter += 1
                if violation_counter >= ALERT_THRESHOLD_FRAMES:
                    if current_time - last_alert_time >= 1.0:
                        timestamp_str = time.strftime('%H:%M:%S', time.localtime(current_time))
                        alerts.append({
                            "message": "🚨 ALERTA: Pessoa sem máscara detectada!",
                            "timestamp": timestamp_str  # <--- Enviando a hora do backend!
                        })
                        last_alert_time = current_time # Atualiza o tempo do último alerta
                    
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
