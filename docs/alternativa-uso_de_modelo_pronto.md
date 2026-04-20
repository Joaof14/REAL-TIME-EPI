# 🚀 Rota Alternativa: Usando um Modelo Pronto do Kaggle para Detecção de Máscaras

Este guia é para você que quer colocar a detecção de máscaras no ar o mais rápido possível, sem se preocupar com a etapa de treinamento do zero. A ideia é simples: usar um notebook já existente no Kaggle para gerar o arquivo de modelo treinado (`best.pt`) e integrá-lo ao nosso sistema.

## ⚖️ 1. Ponto Crítico: Verificando as Licenças de Uso (LEIA COM ATENÇÃO)

Antes de começar, é fundamental entender as permissões de uso do modelo e do dataset para garantir que seu projeto está dentro da legalidade, especialmente se houver intenção de uso comercial.

*   **O Dataset**: O dataset que usaremos (`andrewmvd/face-mask-detection`) está sob a licença **CC0: Public Domain**. Isso significa que você tem total liberdade para usá-lo, inclusive para fins comerciais, sem precisar dar crédito ao autor (embora seja sempre uma boa prática citar a fonte). Esse é o cenário ideal.
*   **O Notebook**: O notebook que vamos usar (`cubeai/facemask-detection-with-yolov8`) está sob a licença **Apache 2.0**. Essa é uma licença de software permissiva, que também permite uso comercial. Ótimo!
*   **O Modelo Base (YOLOv8)**: O modelo que usaremos como ponto de partida (`yolov8n.pt`) é da Ultralytics e está sob a licença **AGPL-3.0**. Esse é o ponto mais delicado. O AGPL exige que qualquer software que utilize o modelo e seja disponibilizado publicamente (inclusive como um serviço online) tenha seu código-fonte aberto sob a mesma licença.
    *   **Para um MVP ou projeto pessoal/educacional:** Não há problema.
    *   **Para um produto comercial:** É altamente recomendável adquirir uma licença comercial (Enterprise License) diretamente da Ultralytics, o que te isenta da obrigação de abrir o código-fonte.

## ✅ 2. To-Do: Criando o `best.pt` e Integrando ao Projeto

- [ ] **Fase 1: No Kaggle (Copiar e Executar Notebook)**
    - [ ] Acessar o notebook "Facemask detection with YOLOv8" no Kaggle.
    - [ ] Fazer uma cópia (`Copy & Edit`) do notebook para sua própria conta.
    - [ ] Executar todas as células do notebook (aproximadamente 22 minutos com GPU P100).
    - [ ] Verificar se o arquivo `best.pt` foi gerado na pasta de saída.
    - [ ] Baixar o arquivo `best.pt` para seu computador local.
- [ ] **Fase 2: No Projeto (Local)**
    - [ ] Substituir o arquivo `best.pt` antigo na pasta `backend/` pelo novo modelo de máscaras.
    - [ ] Atualizar o dicionário `CLASS_NAMES` no arquivo `backend/main.py`.
    - [ ] Testar a detecção de máscaras em tempo real no frontend.

## 📘 3. Passo a Passo Detalhado (Step-by-Step)

### Fase 1: Gerando o Modelo no Kaggle

1.  **Acesse o Notebook**: Clique neste link: [Facemask detection with YOLOv8](https://www.kaggle.com/code/cubeai/facemask-detection-with-yolov8).
2.  **Faça uma Cópia**: No canto superior direito, clique em **"Copy & Edit"**. Isso criará uma versão privada do notebook na sua conta do Kaggle.
3.  **Configure a Aceleração de Hardware**: No novo notebook, vá em `Settings` > `Accelerator` e selecione **`GPU P100`**. Isso é crucial para que o treinamento termine em cerca de 20 minutos.
4.  **Execute as Células**:
    *   **Instalação**: A primeira célula instala a biblioteca `ultralytics`. Execute-a.
    *   **Treinamento**: A próxima célula contém o comando de treinamento.
        ```python
        !yolo task=detect mode=train model=yolov8n.pt data=/kaggle/input/facemask-detection-for-yolov8/data.yaml epochs=100 imgsz=640 batch=16
        ```
        *   Este comando usa o modelo `yolov8n.pt` (nano) como base e o treina por 100 épocas com o dataset do Kaggle. Execute esta célula e aguarde a conclusão do processo.
    *   **Validação (Opcional)**: Se houver uma célula de validação, execute-a para ver as métricas de desempenho.
5.  **Baixe o Modelo**: Ao final do treinamento, o arquivo `best.pt` estará salvo em `/kaggle/working/runs/detect/train/weights/best.pt`.
    *   No painel lateral direito do Kaggle, vá na aba **"Output"**.
    *   Navegue pelas pastas `runs/detect/train/weights/`.
    *   Localize o arquivo `best.pt`, clique nos três pontinhos ao lado do nome e selecione **"Download"** para salvá-lo em seu computador.

### Fase 2: Integrando o Modelo ao Seu Projeto

Com o `best.pt` em mãos, a integração é muito simples.

1.  **Substitua o Modelo Antigo**: Mova o arquivo `best.pt` que você baixou para a pasta `backend/` do seu projeto principal, sobrescrevendo o modelo de EPI anterior.
2.  **Atualize o Código do Servidor**:
    *   Abra o arquivo `backend/main.py`.
    *   Localize a variável `CLASS_NAMES`. Substitua o dicionário antigo por este novo, que reflete as classes do dataset usado no Kaggle:
        ```python
        CLASS_NAMES = {
            0: "Com Máscara",
            1: "Sem Máscara",
            2: "Máscara Incorreta"
        }
        ```
3.  **Teste a Integração Final**:
    *   Certifique-se de que seu ambiente virtual Python para o backend está ativo.
    *   Inicie o servidor com `uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
    *   Abra o frontend no navegador e inicie a câmera. Você deverá ver as detecções do seu novo modelo, agora identificando máscaras faciais em tempo real!
```
