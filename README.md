# Vector Website

Flask site for [vectorny.com](https://www.vectorny.com). Deployed on **Railway** (Docker) from this repo.

## Daily development (fast — no Docker rebuild)

```bash
cd Website
./scripts/dev-local.sh
```

Open **http://127.0.0.1:5005** — saves reload automatically.

## Docker (production-like)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) running.

```bash
# First time or after requirements.txt / Dockerfile changes:
docker compose up --build

# Live code mount (no rebuild for most edits):
docker compose -f docker-compose.dev.yml up --build   # once
docker compose -f docker-compose.dev.yml up          # after that
```

## Deploy (GitHub → Railway)

```bash
git add -A && git commit -m "your message" && git push origin main
```

Railway builds from `Dockerfile` (`railway.json` → `DOCKERFILE`).  
**Settings:** no custom start command; target port **8080**.

## SMK React page (`/smk`)

Pre-built files live in `react-pages/smk/build/`. To rebuild after editing React source:

```bash
./scripts/build-smk.sh
git add react-pages/smk/build react-pages/smk/src
git commit -m "Rebuild SMK"
```

## Layout

```
app.py, database.py, forms.py   # Flask app
templates/, static/             # Site HTML/assets
react-pages/smk/                # SMK landing (React source + build/)
scripts/                        # dev-local.sh, build-smk.sh
Dockerfile, docker-compose*.yml # Container deploy
railway.json                    # Railway config
requirements.txt                # Python deps
```

## Domains

| Domain | Where to configure |
|--------|-------------------|
| Railway app URL | Railway networking |
| `www.vectorny.com` | GoDaddy DNS → Railway |
| `vectorny.com` | GoDaddy DNS (apex records from Railway) |
