#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SE7EN PAY · Autopost próprio e gratuito (Instagram Graph API oficial da Meta).
Lê o calendário do lote, descobre o que está "vencido" (hora agendada já passou e ainda
não foi publicado) e publica via API. Sem mensalidade, sem servidor pago.

Agendador: GitHub Actions (cron a cada 15 min) chama este script — ver .github/workflows/autopost.yml
Idempotência: state/published.json guarda o que já saiu (evita repetir).

Segredos (via ambiente / GitHub Secrets — nunca no código):
  IG_USER_ID      = ID da conta Instagram Business (número)
  IG_ACCESS_TOKEN = token de acesso de longa duração
  MEDIA_BASE_URL  = URL pública base onde as imagens estão (ex.: raw.githubusercontent.com/<user>/<repo>/main)

Uso:
  python3 publish.py --dry-run            # mostra o que faria agora, sem chamar a API
  python3 publish.py --dry-run --now 2026-07-22T15:35:00Z   # simula um instante
  python3 publish.py                       # executa de verdade (usado pelo GitHub Actions)
"""
import os, csv, json, glob, argparse, datetime, zoneinfo, sys, time
try:
    import requests
except Exception:
    requests=None

BASE=os.path.dirname(os.path.abspath(__file__))
LOT_DIRS=[os.path.abspath(os.path.join(BASE,"..","social-content-full-lot")),
          os.path.abspath(os.path.join(BASE,"content"))]  # fallback: cópia dentro do repo
def lot():
    for d in LOT_DIRS:
        if os.path.exists(os.path.join(d,"05-editorial-calendar-30-days.csv")): return d
    return LOT_DIRS[0]
LOT=lot()
CAL=os.path.join(LOT,"05-editorial-calendar-30-days.csv")
STATE=os.path.join(BASE,"state","published.json")
SP=zoneinfo.ZoneInfo("America/Sao_Paulo"); UTC=zoneinfo.ZoneInfo("UTC")
GRAPH="https://graph.facebook.com/v21.0"

def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"published":{}}
def save_state(s):
    os.makedirs(os.path.dirname(STATE),exist_ok=True); json.dump(s,open(STATE,"w"),indent=2,ensure_ascii=False)

def meta(pid):
    p=os.path.join(LOT,"src",pid,"metadata.json")
    return json.load(open(p)) if os.path.exists(p) else {}
def kind_of(pid,m): return m.get("kind") or ("story" if pid.startswith("PUB-S") else ("reel" if pid.startswith("PUB-R") else "carousel"))
def media_files(pid,kind):
    ad=os.path.join(LOT,"src",pid,"assets")
    if kind=="carousel": return [f for f in sorted(glob.glob(os.path.join(ad,f"{pid}_p*_v45.jpg"))) if "_light" not in f]
    if kind=="static":   f=os.path.join(ad,f"{pid}_p01_v45.jpg"); return [f] if os.path.exists(f) else []
    f=os.path.join(ad,f"{pid}_p01_story.jpg"); return [f] if os.path.exists(f) else []
def media_url(base,pid,localfile):
    rel=os.path.relpath(localfile, LOT).replace(os.sep,"/")
    return f"{base.rstrip('/')}/{rel}"
def caption(pid,m):
    cp=m.get("copy",{}); c=cp.get("caption") or cp.get("description") or m.get("name",""); t=cp.get("hashtags","")
    return (c+("\n\n"+t if t else "")).strip()
def sp_utc(data,hora):
    return datetime.datetime.strptime(f"{data} {hora}","%d/%m/%Y %H:%M").replace(tzinfo=SP).astimezone(UTC)

def eligible_rows(now, state, include_stories=False, window_hours=48):
    rows=list(csv.DictReader(open(CAL,encoding="utf-8")))
    due=[]; skip=[]
    for r in rows:
        pid=r["ID"]; m=meta(pid); k=kind_of(pid,m)
        uid=f"{pid}@{r['Data']} {r['Horario']}"
        if uid in state["published"]: continue
        if k=="reel": skip.append((pid,"Reel precisa de vídeo (temos só capa)")); continue
        if k=="story" and not include_stories: skip.append((pid,"Story interativo → manual")); continue
        files=media_files(pid,k)
        if not files: skip.append((pid,"sem imagem")); continue
        when=sp_utc(r["Data"],r["Horario"])
        if when<=now and when>=now-datetime.timedelta(hours=window_hours):
            due.append((uid,r,m,k,files,when))
    return due, skip

def api_post(url, data):
    r=requests.post(url,data=data,timeout=60);
    try: j=r.json()
    except Exception: j={"error":{"message":r.text}}
    return r.status_code, j

def publish_one(igid, token, base, pid, m, kind, files, dry):
    urls=[media_url(base,pid,f) for f in files]
    cap=caption(pid,m)
    if dry:
        print(f"    would publish {kind} · {len(urls)} img · caption[{len(cap)} chars]")
        for u in urls: print(f"      image_url={u}")
        return "DRY-"+pid
    if kind=="carousel":
        children=[]
        for u in urls:
            sc,j=api_post(f"{GRAPH}/{igid}/media",{"image_url":u,"is_carousel_item":"true","access_token":token})
            if "id" not in j: raise RuntimeError(f"child fail: {j}")
            children.append(j["id"])
        sc,j=api_post(f"{GRAPH}/{igid}/media",{"media_type":"CAROUSEL","children":",".join(children),"caption":cap,"access_token":token})
    else:  # static feed image (ou story se include_stories)
        params={"image_url":urls[0],"caption":cap,"access_token":token}
        if kind=="story": params={"image_url":urls[0],"media_type":"STORIES","access_token":token}
        sc,j=api_post(f"{GRAPH}/{igid}/media",params)
    if "id" not in j: raise RuntimeError(f"container fail: {j}")
    creation=j["id"]
    time.sleep(3)  # dá tempo do container processar
    sc,j=api_post(f"{GRAPH}/{igid}/media_publish",{"creation_id":creation,"access_token":token})
    if "id" not in j: raise RuntimeError(f"publish fail: {j}")
    return j["id"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dry-run",action="store_true")
    ap.add_argument("--now",default="")
    ap.add_argument("--include-stories",action="store_true")
    a=ap.parse_args()
    now=datetime.datetime.strptime(a.now,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC) if a.now else datetime.datetime.now(UTC)
    state=load_state()
    igid=os.environ.get("IG_USER_ID",""); token=os.environ.get("IG_ACCESS_TOKEN","")
    base=os.environ.get("MEDIA_BASE_URL","https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main")
    print(f"=== AUTOPOST GRATUITO (Meta Graph API) ===")
    print(f"Agora (UTC): {now.strftime('%Y-%m-%dT%H:%M:%SZ')} · Calendário: {os.path.basename(CAL)}")
    print(f"Base de mídia: {base}")
    due,skip=eligible_rows(now,state,a.include_stories)
    print(f"Vencidas para publicar agora: {len(due)}")
    if not a.dry_run:
        if requests is None: print("ERRO: 'requests' não instalado."); sys.exit(1)
        if not igid or not token: print("ERRO: defina IG_USER_ID e IG_ACCESS_TOKEN."); sys.exit(1)
    ok=0
    for uid,r,m,k,files,when in due:
        print(f"  [{r['Data']} {r['Horario']} SP] {r['ID']} ({k}) · {r['Titulo']}")
        try:
            res=publish_one(igid,token,base,r["ID"],m,k,files,a.dry_run)
            if not a.dry_run:
                state["published"][uid]={"ig_media_id":res,"published_at":now.strftime('%Y-%m-%dT%H:%M:%SZ')}
                save_state(state)
            ok+=1
        except Exception as e:
            print(f"    ERRO: {e}")
    print(f"\n{ok}/{len(due)} publicadas" + (" (DRY-RUN, nada enviado)" if a.dry_run else "") + ".")
    if a.dry_run and due:
        print("\nDica: teste um instante específico com --now 2026-07-22T15:35:00Z")

if __name__=="__main__": main()
