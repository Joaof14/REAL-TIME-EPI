# ✅ To-Do: Treinamento do Modelo de Detecção de Máscaras (Face Mask)

## 1. Preparação do Ambiente e Dados (Executado no Google Colab)
- [ ] Configurar o notebook no Google Colab com GPU.
- [x] Instalar as dependências (`ultralytics`, `kagglehub`, `opencv-python`, `tqdm`).
- [x] Baixar o dataset `andrewmvd/face-mask-detection` usando `kagglehub`.
- [ ] Executar a conversão das anotações do formato PASCAL VOC (`.xml`) para o formato YOLO (`.txt`).
- [ ] Organizar os arquivos na estrutura de pastas exigida pelo YOLOv8 (`train/` e `val/`).
- [ ] Criar o arquivo de configuração `data.yaml`.
- [ ] (Opcional) Aplicar Data Augmentation offline.

## 2. Treinamento do Modelo YOLOv8 (Executado no Google Colab)
- [ ] Carregar o modelo base pré-treinado (`yolov8n.pt`).
- [ ] Executar o treinamento monitorando as métricas (mAP, Precision, Recall).
- [ ] Avaliar o modelo no conjunto de validação.
- [ ] Testar a inferência em uma imagem ou vídeo de exemplo.

## 3. Integração com o Projeto Principal
- [ ] Baixar o arquivo `best.pt` do Colab.
- [ ] Copiar `best.pt` para a pasta `backend/`, substituindo o modelo antigo.
- [ ] Atualizar o dicionário `CLASS_NAMES` no arquivo `main.py`.
- [ ] Testar a detecção de máscaras em tempo real no frontend.