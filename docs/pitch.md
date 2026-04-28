# 😷 EPI-Watch: Monitoramento de Uso de Máscaras — Pitch

**Status:** MVP funcional com modelo de detecção obtido no Kaggle (inserir referência).  
**Proposta:** Solução leve, privada e de baixo custo para identificar uso correto de máscaras em tempo real, com ênfase em comunicação WebSocket de baixa latência entre cliente e servidor.

Principais argumentos para adotantes (resumo):

- **Deploy simples:** roda em um servidor leve (`uvicorn`) e usa browser como cliente (BYOD).
- **Privacidade:** apenas metadados de detecção trafegam; nenhuma imagem é persistida no servidor.
- **Baixa latência — WebSocket:** comunicação contínua via WebSocket (`/ws`) para envio de frames e recebimento de detecções em JSON garante feedback em tempo real e simplicidade de integração.
- **Extensível:** trocar o arquivo de modelo permite detectar outros EPIs (capacetes, coletes, etc.).

Público-alvo: clínicas, laboratórios, pequenas indústrias, canteiros de obra e escolas que necessitam auditoria simples e econômica do uso de EPIs.

Valor entregue:

- Redução de risco por meio de alertas em tempo real.
- Privacidade e conformidade com legislações locais (nenhum vídeo é armazenado).
- Implementação rápida com baixo custo de infraestrutura.

Roadmap curto prazo:

- Registrar metadados e referência do modelo do Kaggle no repositório para atribuição.
- Validar e melhorar acurácia do modelo com coleta de casos reais e retraining quando apropriado.
- Adicionar alertas sonoros e integrações (e.g., webhook, Slack) via eventos gerados pelo backend ao detectar não conformidade.
- Gerar relatórios periódicos de conformidade em CSV/JSON.