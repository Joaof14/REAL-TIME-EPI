import base64
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from ultralytics import YOLO
import asyncio
import json
from pathlib import Path

app = FastAPI()

# Monta a pasta do frontend para servir o index.html
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Carrega o modelo YOLO (pode ser o nano para teste, ou seu modelo customizado)
# Se você tem um modelo treinado para EPI, substitua pelo caminho do best.pt
MODEL_PATH = "best.pt" if Path("best.pt").exists() else "yolov8n.pt"
model = YOLO(MODEL_PATH)
print(f"✅ Modelo carregado: {MODEL_PATH}")

# Mapeamento de classes (ajuste conforme seu dataset)
# Exemplo para modelo COCO (yolov8n): pessoa é classe 0
# Para modelo de EPI, as classes podem ser: 0=capacete, 1=colete, 2=pessoa, etc.
CLASS_NAMES = {
    0: "pessoa",
    1: "capacete",
    2: "colete",
    3: "luva"
}
# Se estiver usando o modelo padrão COCO, vamos focar em detectar pessoa
# e simular a lógica de EPI (você pode substituir por seu modelo treinado)

@app.get("/")
async def get():
    """Serve a página HTML do frontend"""
    html_file = frontend_path / "index.html"
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Cliente conectado")
    
    try:
        while True:
            # Recebe o frame como base64 (enviado pelo frontend)
            data = await websocket.receive_text()
            
            # Decodifica a imagem
            # O frontend envia no formato "data:image/jpeg;base64,...."
            header, encoded = data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue
            
            # Executa a detecção
            results = model(frame, conf=0.5, verbose=False)[0]
            
            # Prepara dados para enviar ao frontend
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = CLASS_NAMES.get(class_id, f"classe_{class_id}")
                
                detections.append({
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "confidence": confidence,
                    "class_id": class_id,
                    "class_name": class_name
                })
            
            # Lógica simples de alerta: se detectar pessoa mas não capacete na mesma região
            # (ajuste conforme sua necessidade)
            persons = [d for d in detections if d["class_name"] == "pessoa"]
            helmets = [d for d in detections if d["class_name"] == "capacete"]
            
            alerts = []
            for person in persons:
                # Verifica se há algum capacete com sobreposição significativa
                has_helmet = False
                for helmet in helmets:
                    # Calcula interseção simples (pode melhorar com IoU)
                    if (helmet["x1"] < person["x2"] and helmet["x2"] > person["x1"] and
                        helmet["y1"] < person["y2"] and helmet["y2"] > person["y1"]):
                        has_helmet = True
                        break
                if not has_helmet:
                    alerts.append({
                        "person_box": person,
                        "message": "⚠️ Pessoa sem capacete detectada!"
                    })
            
            # Envia resposta JSON com detecções e alertas
            await websocket.send_json({
                "detections": detections,
                "alerts": alerts,
                "total_persons": len(persons),
                "total_helmets": len(helmets)
            })
            
    except WebSocketDisconnect:
        print("🔴 Cliente desconectado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)