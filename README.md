# 😷 EPI-Watch: Detecção de Máscaras de Proteção em Tempo Real

**Status:** MVP Funcional (Modelo em Treinamento)  
**Objetivo:** Monitoramento inteligente e de baixo custo do uso correto de máscaras faciais (EPI) utilizando Visão Computacional.

---

## 🚀 Visão Geral

O **EPI-Watch** é um sistema de monitoramento em tempo real que utiliza uma câmera comum (webcam ou smartphone) para detectar a conformidade no uso de máscaras de proteção. A arquitetura é baseada em comunicação WebSocket de baixa latência e inferência com modelos YOLOv8.

**Estado Atual (MVP):** O sistema está **totalmente funcional** com um modelo provisório (`yolov8n.pt`) e uma lógica de alerta simulada para fins de demonstração e validação da infraestrutura. O modelo definitivo, especializado na detecção de máscaras faciais, está sendo treinado pela equipe e será integrado em breve.

---

## 🎯 Funcionalidades Atuais

- **Captura de vídeo em tempo real** diretamente do navegador (desktop ou mobile).
- **Comunicação WebSocket** para envio de frames e recebimento de resultados de IA.
- **Detecção de objetos genérica** (modelo YOLOv8n pré-treinado no COCO).
- **Lógica de alerta simulada** para teste do fluxo:
  - A presença de um **celular** no frame é interpretada como "uso de máscara".
  - A ausência do celular (com uma pessoa visível) dispara um alerta após 10 frames consecutivos.
- **Visualização clara** com bounding boxes e labels sobrepostas ao vídeo.
- **Painel de histórico** dos últimos alertas.

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologias |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn, OpenCV, Ultralytics YOLOv8 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6), WebSocket API, Canvas API |
| **Comunicação** | WebSockets |
| **Modelo de IA (atual)** | YOLOv8n (COCO) – fallback provisório |
| **Modelo de IA (em treinamento)** | YOLOv8n customizado para máscaras (via Google Colab) |

---

## 📂 Estrutura do Projeto

REAL-TIME-EPI/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── best.pt                     # Modelo treinado (a ser adicionado após treinamento)
├── frontend/
│   └── index.html
├── notebooks/
│   └── modelo.ipynb     # Notebook do Google Colab
├── docs/
│   ├── to-do_ConstruirModelo.md
│   └── step-by-step_ConstruirModelo.md
│   └── alternativa-uso_de_modelo_pronto.md
│   └── pitch.md
├── README.md
└── .gitignore
---

## ▶️ Como Executar o MVP

### 1. Backend (Servidor Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # (Linux/macOS)
# ou .\venv\Scripts\activate  # (Windows)

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

``` 

### 2. Frontend (Interface Web)

Com o servidor rodando, abra o navegador e acesse http://localhost:8000.

Para acessar de um celular na mesma rede Wi-Fi, use o IP local do computador (ex: http://192.168.1.100:8000).


### Como Testar o Funcionamento Atual (Simulação com Celular)

- Clique em "Ligar Câmera" e permita o acesso.

- Enquadre uma pessoa no vídeo. Uma caixa azul com o label person aparecerá.

- Segure um celular visível no frame. Uma caixa com o label cell phone será desenhada.

- Remova o celular do frame. Após cerca de 1,5 segundo, o alerta "🚨 ALERTA: Pessoa sem máscara detectada!" será exibido no painel.

- Retorne o celular ao frame. O alerta deixará de ser emitido.

- Interpretação: Nesta simulação, a detecção do celular funciona como um proxy para o uso correto da máscara. Isso permite validar toda a pipeline de comunicação, lógica de buffer e exibição de alertas sem depender do modelo final.

### Próximos Passos: 
Ler as opções descrita na pasta docs.
