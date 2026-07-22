# Autopost SE7EN PAY · Solução Própria e 100% Gratuita

Sem mensalidade e sem servidor pago. Usa só ferramentas gratuitas:
- **API oficial da Meta (Instagram Graph API)** — publica feed/carrossel. Grátis.
- **GitHub Actions** — agendador que roda a cada 15 min e publica o que venceu. Grátis.
- **GitHub (repositório)** — hospeda as imagens em URL pública (a API exige URL pública). Grátis.

> Por que não o Postiz? O Postiz Cloud é **pago** (o "$0" é teste de 7 dias). O código aberto do Postiz é grátis, mas exige um servidor sempre ligado. Esta solução não precisa de servidor.

## Como o ciclo funciona
1. Você aprova o calendário do mês (revisando a galeria do lote).
2. Você sobe os arquivos para um repositório no GitHub e configura 3 segredos.
3. O GitHub Actions roda sozinho a cada 15 min, olha o calendário e **publica o que chegou na hora** — mesmo com seu computador desligado.
4. O estado (`state/published.json`) evita publicar a mesma peça duas vezes.

## O que publica automaticamente
- **15 peças de feed:** 10 carrosséis + 5 estáticos (imagens finais prontas).
- **Fora (por limite do Instagram):** 12 Stories interativos (stickers não vão pela API → manuais) e 6 Reels (precisam do arquivo de vídeo).

---

## Passo 1 · Pré-requisitos na Meta (grátis)
1. A conta **@se7enpay** já é Business/Creator vinculada a uma Página do Facebook (você confirmou). ✔
2. Crie um app em **developers.facebook.com** → "Criar app" → tipo "Business".
3. Adicione o produto **Instagram Graph API**.
4. Gere um **token de acesso** com as permissões: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`, `pages_show_list`.
   - Use o **Graph API Explorer** para gerar, depois troque por um **token de longa duração** (60 dias).
5. Pegue o **IG_USER_ID** (ID numérico da conta Instagram Business).

> O token de 60 dias precisa ser renovado. Dá para automatizar depois; no começo, renove manualmente a cada ~2 meses (aviso simples).

## Passo 2 · Criar o repositório no GitHub (grátis)
1. Crie um repositório (pode ser **público** — as imagens são de marketing, não têm nada sensível; isso deixa as URLs públicas de graça).
2. Suba nele:
   - a pasta `autopost-free/` (este kit);
   - a pasta `social-content-full-lot/` (o lote com as imagens e o calendário).
   - Alternativa: copie o calendário e as imagens para `autopost-free/content/` (o script procura lá também).
3. Confirme que a imagem abre pela URL crua, por exemplo:
   `https://raw.githubusercontent.com/<seu_usuario>/<seu_repo>/main/social-content-full-lot/src/PUB-001/assets/PUB-001_p01_v45.jpg`

## Passo 3 · Configurar os segredos (Settings → Secrets and variables → Actions)
Crie 3 segredos (nunca vão para o código):
- `IG_USER_ID` = ID numérico da conta Instagram Business
- `IG_ACCESS_TOKEN` = token de longa duração
- `MEDIA_BASE_URL` = `https://raw.githubusercontent.com/<seu_usuario>/<seu_repo>/main/social-content-full-lot`

## Passo 4 · Ativar o agendador
- O arquivo `.github/workflows/autopost.yml` já está pronto (cron a cada 15 min).
- Em **Actions**, habilite os workflows. Pode testar na hora com **Run workflow** (botão manual).
- A partir daí, o GitHub publica sozinho no horário de cada peça.

## Testar sem publicar (recomendado antes de ligar)
No seu computador (ou no próprio Actions em modo manual):
```bash
python3 autopost-free/publish.py --dry-run                       # mostra o que faria agora
python3 autopost-free/publish.py --dry-run --now 2026-07-22T15:35:00Z   # simula um instante
```
O dry-run não chama a API — só lista o que sairia, com as URLs e legendas.

## Segurança
- O script **não** guarda sua senha; a autenticação é o token da Meta, que fica em **GitHub Secrets**.
- Nada é publicado sem os segredos configurados e o workflow ativado por você.
- Idempotência + janela de 48h evitam duplicar posts ou "despejar o mês" se o agendador ficar off.

## Ajustar o calendário
Edite `05-editorial-calendar-30-days.csv` (data/horário em America/Sao_Paulo) e faça commit — o agendador passa a seguir os novos horários. Fuso é convertido para UTC automaticamente.

## Limites
- Instagram: até **25 publicações/24h** (nosso volume é ≤2/dia).
- Reels: quando tiver os vídeos, dá para estender o script para `media_type=REELS` (posso fazer).
- Stories interativos seguem manuais (limitação da API, não do script).
