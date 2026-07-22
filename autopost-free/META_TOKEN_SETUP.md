# Setup do Token da Meta · @se7enpay (para o autopost gratuito)

Objetivo: obter **2 valores** que vão nos GitHub Secrets:
- `IG_USER_ID` — o ID numérico da conta Instagram Business @se7enpay
- `IG_ACCESS_TOKEN` — um token que **não expira** (System User token)

Pré-requisitos que você já tem: conta @se7enpay Business/Creator, vinculada a uma Página do Facebook, dentro de um Business Manager.

---

## Parte A · Criar o app (uma vez)
1. Acesse **developers.facebook.com** → logado com o Facebook que administra a Página.
2. **My Apps → Create App → tipo "Business" → Next.**
3. Dê um nome (ex.: "SE7EN Autopost") e crie.
4. No painel do app, em **Add products**, adicione **Instagram Graph API** (ou "Instagram" → "Instagram API setup").
5. Anote o **App ID** e o **App Secret** (Settings → Basic). Guarde com cuidado.

## Parte B · System User token (não expira) — recomendado
1. Vá para **business.facebook.com/settings** (Business Settings).
2. Menu **Usuários → Usuários do sistema → Adicionar** → nome "autopost" → função **Admin**.
3. Clique no system user criado → **Adicionar ativos** → selecione a **Página do Facebook** (a que está ligada ao @se7enpay) → dê acesso total.
4. Ainda no system user → **Gerar novo token** → escolha o **app** criado na Parte A.
5. Marque as permissões:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`
6. **Token expira:** escolha **Nunca** (é a vantagem do system user).
7. Copie o token gerado — esse é o seu `IG_ACCESS_TOKEN`. **Não cole aqui no chat**; guarde num gerenciador seguro.

> Alternativa rápida (mas expira em 60 dias): Graph API Explorer → gerar token de usuário com as mesmas permissões → trocar por long-lived. Só use se não quiser mexer em System User agora.

## Parte C · Descobrir o IG_USER_ID
Com o token em mãos, rode no seu terminal (troque TOKEN):
```bash
# 1) achar a Página e o Instagram vinculado
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token=TOKEN"
# pegue o "id" da Página SE7EN, depois:
curl -s "https://graph.facebook.com/v21.0/PAGE_ID?fields=instagram_business_account&access_token=TOKEN"
# o "instagram_business_account.id" é o seu IG_USER_ID
```
Ou, se preferir, eu rodo isso pra você **se** você definir o token só no seu ambiente (não no chat).

## Parte D · Testar de verdade (1 chamada segura, sem publicar)
```bash
curl -s "https://graph.facebook.com/v21.0/IG_USER_ID?fields=username,followers_count&access_token=TOKEN"
# deve retornar "username":"se7enpay" e o número de seguidores → prova que o token funciona
```

## Parte E · Plugar no autopost
Nos **GitHub Secrets** do repositório (Settings → Secrets and variables → Actions):
- `IG_USER_ID` = valor da Parte C
- `IG_ACCESS_TOKEN` = token da Parte B
- `MEDIA_BASE_URL` = URL crua do repositório com o lote (ver `SETUP_FREE.md`)

Depois: `Actions → Run workflow` para testar, ou deixe o cron de 15 min agir.

---

## Segurança (importante)
- **Nunca** cole o token/segredos no chat, em commit ou em arquivo do repositório. Só nos GitHub Secrets.
- O System User token é poderoso: dá acesso de publicação. Trate como senha.
- Se vazar, revogue em Business Settings → Usuários do sistema → o token.
- Eu não insiro sua senha nem autorizo OAuth por você — esses cliques são seus.
