# Comparativo · Autopost Instagram (custo real)

| Opção | Custo | Automático (lê calendário) | Precisa servidor? | Observação |
|---|---|---|---|---|
| **Nossa solução (Meta API + GitHub Actions)** | **Grátis** | Sim | Não (GitHub roda) | Recomendada. Token Meta renova a cada 60 dias. |
| Meta Business Suite (nativo) | Grátis | Não (manual, 1 a 1) | Não | Bom para postar à mão; não lê nosso CSV. |
| Postiz Cloud | Pago (teste 7 dias) | Sim | Não | O "$0" do site é trial, não é grátis. |
| Postiz self-hosted | Software grátis | Sim | Sim (sempre ligado) | Custo vira a hospedagem do servidor. |
| Buffer/Later/Metricool (free tier) | Grátis limitado | Parcial | Não | Poucos posts/canais no plano free; sem import do nosso CSV. |

Conclusão: para **grátis + automático + sem servidor**, a solução própria (Meta API + GitHub Actions) é a melhor.
