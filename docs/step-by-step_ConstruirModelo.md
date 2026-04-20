# 📘 Guia Passo a Passo: Treinamento do Modelo de Detecção de Máscaras

Este guia foi escrito para você executar o treinamento do início ao fim no Google Colab. O dataset escolhido contém **853 imagens** e **3 classes** (`with_mask`, `without_mask`, `mask_weared_incorrect`), com anotações no formato PASCAL VOC.

## 🗂️ 1. Configuração Inicial no Google Colab

1.  **Crie um novo notebook** no [Google Colab](https://colab.research.google.com/).
2.  **Habilite a GPU**: Vá em `Ambiente de execução` > `Alterar tipo de ambiente de execução` e selecione `T4 GPU` como acelerador de hardware.
3.  **Instale as dependências** na primeira célula e execute-a:
    ```python
    !pip install -q ultralytics kagglehub opencv-python tqdm
    ```
4.  **Importe as bibliotecas** e configure os diretórios:
    ```python
    import os
    import shutil
    import yaml
    import xml.etree.ElementTree as ET
    from pathlib import Path
    import kagglehub
    from tqdm import tqdm
    import cv2
    from ultralytics import YOLO
    ```

## 📥 2. Download e Preparação do Dataset

### 2.1. Baixar o Dataset
O download é feito diretamente do Kaggle com a biblioteca `kagglehub`. Execute a célula:

```python
# Baixa o dataset do Kaggle
dataset_path = kagglehub.dataset_download("andrewmvd/face-mask-detection")
print(f"✅ Dataset baixado para: {dataset_path}")

# Define os diretórios de trabalho
RAW_DATA_DIR = Path('/content/face_mask_raw')
YOLO_DATA_DIR = Path('/content/face_mask_yolo')

# Copia o dataset para nosso diretório de trabalho
if RAW_DATA_DIR.exists():
    shutil.rmtree(RAW_DATA_DIR)
shutil.copytree(dataset_path, RAW_DATA_DIR)
print(f"✅ Dataset copiado para: {RAW_DATA_DIR}")
```

### 2.2. Converter Anotações de PASCAL VOC para YOLO
O dataset usa anotações no formato PASCAL VOC (arquivos `.xml`). A célula abaixo as converte para o formato YOLO (`.txt`), que é o que o modelo espera.

```python
# Define as classes do dataset (ordem importante!)
CLASS_NAMES = ["with_mask", "without_mask", "mask_weared_incorrect"]

def convert_voc_to_yolo(xml_path, img_width, img_height):
    """
    Converte um único arquivo XML do formato PASCAL VOC para o formato YOLO.
    Retorna uma lista de strings no formato: class_id x_center y_center width height
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    yolo_lines = []
    for obj in root.findall("object"):
        class_name = obj.find("name").text
        if class_name not in CLASS_NAMES:
            continue
        class_id = CLASS_NAMES.index(class_name)
        
        bbox = obj.find("bndbox")
        xmin = int(bbox.find("xmin").text)
        ymin = int(bbox.find("ymin").text)
        xmax = int(bbox.find("xmax").text)
        ymax = int(bbox.find("ymax").text)
        
        # Converte para formato YOLO (valores normalizados entre 0 e 1)
        x_center = (xmin + xmax) / (2.0 * img_width)
        y_center = (ymin + ymax) / (2.0 * img_height)
        bbox_width = (xmax - xmin) / img_width
        bbox_height = (ymax - ymin) / img_height
        
        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}")
    
    return yolo_lines

def prepare_yolo_dataset(raw_dir, yolo_dir, train_ratio=0.8):
    """
    Organiza o dataset no formato YOLO, dividindo em treino e validação.
    """
    raw_dir = Path(raw_dir)
    yolo_dir = Path(yolo_dir)
    
    # Remove diretório YOLO se já existir
    if yolo_dir.exists():
        shutil.rmtree(yolo_dir)
    
    # Cria estrutura de pastas
    for split in ["train", "val"]:
        (yolo_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (yolo_dir / split / "labels").mkdir(parents=True, exist_ok=True)
    
    # Lista todas as imagens
    image_extensions = ["*.jpg", "*.jpeg", "*.png"]
    all_images = []
    for ext in image_extensions:
        all_images.extend(list((raw_dir / "images").glob(ext)))
    
    print(f"📸 Total de imagens encontradas: {len(all_images)}")
    
    # Embaralha e divide em treino/validação
    import random
    random.seed(42)
    random.shuffle(all_images)
    
    split_idx = int(len(all_images) * train_ratio)
    train_images = all_images[:split_idx]
    val_images = all_images[split_idx:]
    
    print(f"📊 Divisão: {len(train_images)} treino / {len(val_images)} validação")
    
    # Processa cada split
    for split, images in [("train", train_images), ("val", val_images)]:
        print(f"\n🔄 Processando {split}...")
        
        for img_path in tqdm(images, desc=f"Convertendo {split}"):
            # Copia a imagem
            dest_img_path = yolo_dir / split / "images" / img_path.name
            shutil.copy2(img_path, dest_img_path)
            
            # Procura o arquivo XML correspondente
            xml_path = raw_dir / "annotations" / (img_path.stem + ".xml")
            if not xml_path.exists():
                continue
            
            # Obtém as dimensões da imagem
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img_height, img_width = img.shape[:2]
            
            # Converte as anotações
            yolo_lines = convert_voc_to_yolo(xml_path, img_width, img_height)
            
            # Salva o arquivo TXT
            txt_path = yolo_dir / split / "labels" / (img_path.stem + ".txt")
            if yolo_lines:
                with open(txt_path, "w") as f:
                    f.write("\n".join(yolo_lines))
    
    print("\n✅ Conversão concluída!")

# Executa a conversão do dataset
print("🔄 Iniciando conversão do dataset para o formato YOLO...")
prepare_yolo_dataset(RAW_DATA_DIR, YOLO_DATA_DIR, train_ratio=0.8)
```

## 📄 3. Criação do Arquivo de Configuração (`data.yaml`)

O arquivo `data.yaml` informa ao YOLOv8 onde estão as imagens e quais são as classes. Execute a célula:

```python
data_yaml_content = {
    'train': str(YOLO_DATA_DIR / 'train' / 'images'),
    'val': str(YOLO_DATA_DIR / 'val' / 'images'),
    'nc': len(CLASS_NAMES),
    'names': CLASS_NAMES
}

yaml_path = YOLO_DATA_DIR / 'data.yaml'
with open(yaml_path, 'w') as f:
    yaml.dump(data_yaml_content, f, default_flow_style=False)

print(f"✅ Arquivo data.yaml criado em: {yaml_path}")
print("\n📋 Conteúdo do arquivo:")
with open(yaml_path, 'r') as f:
    print(f.read())
```

## 🧠 4. Treinamento do Modelo YOLOv8

Agora que os dados estão prontos, vamos treinar o modelo. A célula abaixo usa o **YOLOv8n** (nano), que é rápido e ideal para um MVP.

```python
# Carrega o modelo pré-treinado
model = YOLO('yolov8n.pt')  # Você pode trocar para 'yolov8s.pt' para mais precisão

# Treina o modelo
results = model.train(
    data=str(yaml_path),
    epochs=100,
    imgsz=640,
    batch=16,
    device=0,          # Usa GPU (0 para primeira GPU, 'cpu' para CPU)
    workers=2,
    patience=50,       # Early stopping (interrompe se não melhorar por 50 épocas)
    save=True,
    save_period=10,
    project='/content/runs/detect',
    name='face_mask_detection',
    exist_ok=True
)

print("✅ Treinamento concluído!")
```

> 💡 **Data Augmentation (Opcional):** O YOLOv8 já aplica augmentations padrão (mosaic, mixup, etc.) automaticamente, o que ajuda a melhorar a generalização do modelo mesmo com um dataset pequeno como este.

## 📊 5. Validação e Download do Modelo

Após o treinamento, avalie o desempenho do modelo e faça o download do arquivo `best.pt`.

```python
# Carrega o melhor modelo salvo durante o treinamento
best_model_path = '/content/runs/detect/face_mask_detection/weights/best.pt'
model = YOLO(best_model_path)

# Valida o modelo no conjunto de validação
metrics = model.val()
print(f"\n📊 Métricas de Validação:")
print(f"mAP@0.5: {metrics.box.map50:.4f}")
print(f"mAP@0.5:0.95: {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.p[0]:.4f}")
print(f"Recall: {metrics.box.r[0]:.4f}")

# Faz o download do arquivo best.pt
from google.colab import files
files.download(best_model_path)
```

## 🔗 6. Integração com o Projeto Principal

Com o modelo treinado em mãos, a integração é muito simples:

1.  **Substitua o modelo antigo**: Mova o arquivo `best.pt` baixado para a pasta `backend/` do seu projeto principal, sobrescrevendo o modelo anterior.
2.  **Atualize o dicionário de classes** no arquivo `backend/main.py`:
    ```python
    CLASS_NAMES = {
        0: "Com Máscara",
        1: "Sem Máscara",
        2: "Máscara Incorreta"
    }
    ```
3.  **Reinicie o servidor** e acesse o frontend. Seu sistema agora estará detectando máscaras faciais em tempo real!
```

