# 😷 EPI-Watch: Detecção de Máscaras de Proteção em Tempo Real

**Status:** MVP funcional — integração de modelo disponível no Kaggle (referência a ser adicionada)  
**Objetivo:** Monitoramento inteligente e de baixo custo do uso correto de máscaras faciais (EPI) utilizando Visão Computacional, com foco em comunicação WebSocket de baixa latência.

---

## 🚀 Visão Geral

O **EPI-Watch** é um sistema de monitoramento em tempo real que utiliza uma câmera comum (webcam ou smartphone) para detectar a conformidade no uso de máscaras de proteção. A arquitetura é baseada em comunicação WebSocket de baixa latência e inferência com modelos YOLOv8.

**Estado Atual (MVP):** O sistema opera com um modelo pré-treinado obtido no Kaggle; a equipe integra e valida o modelo, mas não reivindica autoria. O backend carrega o peso (`best.pt`) e realiza inferência em tempo real, classificando estados como `Com Máscara`, `Sem Máscara` e `Máscara Incorreta`. Insira a referência do Kaggle em `docs/` ou neste README para fins de atribuição.

---

## 🎯 Funcionalidades Atuais

- **Captura de vídeo em tempo real** diretamente do navegador (desktop ou mobile).
- **Comunicação WebSocket** para envio de frames e recebimento de resultados de IA.
- **Detecção de máscaras**: inferência realizada com modelo obtido no Kaggle (arquivo de pesos em `backend/`).
- **Lógica de alerta baseada em detecções reais**: quando o sistema identifica `Sem Máscara` por N frames consecutivos, um alerta é registrado e exibido no painel. O pipeline é desenhado para minimizar falsos positivos por buffer de frames.
- **Visualização clara** com bounding boxes e labels sobrepostas ao vídeo.
- **Painel de histórico** dos últimos alertas.

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologias |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn, OpenCV, Ultralytics YOLOv8 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6), WebSocket API, Canvas API |
| **Comunicação** | WebSockets |
| **Modelo de IA (origem)** | Modelo pré-treinado obtido no Kaggle — inserir referência em `docs/` |
| **Modelo de IA (observação)** | A equipe integra e valida o modelo; autoria do modelo não é do projeto. |

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


### Como Testar o Funcionamento Atual

- Clique em "Ligar Câmera" e permita o acesso.

- Enquadre uma pessoa no vídeo; as detecções (bounding boxes) aparecerão sobre o feed com labels claros.

- Experimente três cenários principais: `Com Máscara`, `Sem Máscara` e `Máscara Incorreta`.

- Quando o modelo classificar `Sem Máscara` por vários frames consecutivos (parâmetro configurável no backend), um alerta será registrado e exibido no painel de histórico.

- Para ajuste fino, edite o parâmetro de tolerância de frames no arquivo `backend/main.py` e reinicie o servidor.

**Comandos rápidos para rodar localmente:**

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Abra o navegador em http://localhost:8000 e permita o uso da câmera. Teste com variações de iluminação e ângulo para validar robustez do modelo.

**Atribuição do modelo:** por favor adicione no repositório (ex.: `docs/kaggle_model_reference.md`) o link e metadados do modelo/dataset usado do Kaggle para cumprir requisitos de licença e reprodução.

### Próximos Passos: 
Ler as opções descrita na pasta docs.
