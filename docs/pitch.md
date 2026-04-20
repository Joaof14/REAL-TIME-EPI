# 😷 EPI-Watch: Monitoramento Inteligente do Uso de Máscaras em Tempo Real

**Status:** Protótipo Acadêmico / MVP  
**Objetivo:** Garantir a conformidade do uso de máscaras de proteção em ambientes críticos através de uma solução acessível, privada e de fácil implantação.

---

## 🌟 Proposta de Valor e Diferencial Competitivo

Enquanto sistemas convencionais de monitoramento por vídeo exigem câmeras IP caras, softwares proprietários e complexa infraestrutura de rede, o **EPI-Watch** rompe essas barreiras ao oferecer uma solução baseada em três pilares:

1.  **Democratização e Mobilidade (BYOD):**  
    O sistema roda diretamente no navegador de qualquer smartphone, tablet ou notebook com câmera. Não há necessidade de instalar aplicativos ou adquirir hardware dedicado. Basta apontar a câmera para a área de interesse e o monitoramento começa — ideal para clínicas, laboratórios, pequenas indústrias e obras.

2.  **Privacidade por Design:**  
    O processamento das imagens é feito em tempo real no próprio dispositivo do usuário. Apenas metadados anônimos das detecções (coordenadas das caixas e classes) trafegam pela rede via WebSocket. Nenhuma imagem ou vídeo é armazenado no servidor, garantindo total conformidade com a LGPD e privacidade dos colaboradores.

3.  **Baixa Latência e Arquitetura Leve:**  
    Utilizando o modelo YOLOv8 na versão Nano e comunicação WebSocket assíncrona, o sistema entrega alertas visuais em frações de segundo, mesmo em conexões de internet modestas.

---

## 🛠️ Arquitetura Técnica

| Camada | Tecnologias | Descrição |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript, Canvas API | Captura o feed da câmera local e renderiza as detecções em overlay de forma fluida. |
| **Comunicação** | WebSockets (FastAPI) | Protocolo bidirecional que garante transmissão instantânea de frames e resultados da IA. |
| **Backend / IA** | Python, FastAPI, Ultralytics YOLOv8 | Servidor assíncrono responsável pela inferência do modelo de Visão Computacional. |
| **Modelo de Detecção** | YOLOv8 (Customizado) | Treinado para identificar três estados críticos: `Com Máscara`, `Sem Máscara` e `Máscara Incorreta`. |

---

## 📊 Metodologia de Dados e Treinamento

Para garantir alta acurácia em cenários reais, o modelo foi treinado com um pipeline robusto de dados:

- **Fonte de Dados:** Dataset público *Face Mask Detection* (Kaggle/Hugging Face), contendo milhares de imagens anotadas nos três estados de uso da máscara.
- **Pipeline de Conversão:** Scripts automatizados em Python convertem as anotações do formato PASCAL VOC (XML) para o formato YOLO (TXT), normalizando coordenadas e organizando a estrutura de treino/validação.
- **Data Augmentation (Opcional):** Aplicação de técnicas de aumento de dados com a biblioteca `Albumentations` para simular condições adversas comuns em ambientes reais:
    - Variação de iluminação (luz intensa, sombras).
    - Desfoque de movimento (pessoas caminhando rapidamente).
    - Ruído visual (simulando poeira ou baixa qualidade da câmera).

---

## 🔄 Flexibilidade para Outros Cenários

A arquitetura modular do **EPI-Watch** permite que o mesmo sistema seja rapidamente adaptado para detectar outros Equipamentos de Proteção Individual (EPIs), como:

- Capacetes de segurança.
- Coletes refletivos.
- Luvas e óculos de proteção.

Basta substituir o arquivo do modelo (`best.pt`) e atualizar as classes no backend — o restante da infraestrutura permanece idêntica.

---

## 📍 Roadmap e Próximos Passos

- [x] Desenvolvimento do MVP com comunicação WebSocket e detecção em tempo real.
- [ ] Treinamento/Escolha do modelo especializado em máscaras faciais.
- [ ] Implementação de alertas sonoros e visuais para não conformidade.
- [ ] Geração de relatórios periódicos de conformidade (JSON/CSV).
- [ ] Deploy do protótipo em um serviço de nuvem gratuita (Render/Railway) para testes públicos.