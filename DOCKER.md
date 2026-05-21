# Website — Docker (Railway + local)

The site runs as a **Python/Flask** container. Railway builds from `Dockerfile` (not Nixpacks).

## One-time: install Docker

- **Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- After install, open Docker Desktop and wait until it says “Running”.

## Run locally (pick one)

### Option A — script

```bash
cd Website
./scripts/run-local-docker.sh
```

Open **http://127.0.0.1:5005**

### Option B — docker compose

```bash
cd Website
docker compose up --build
```

### Option C — manual

```bash
cd Website
docker build -t vector-website:local .
docker run --rm -p 5005:8080 -e PORT=8080 vector-website:local
```

Optional: copy `.env` into `Website/` for API keys (loaded automatically by the script / compose).

## Deploy to Railway

Push to GitHub (`main`). Railway uses `railway.json` → `DOCKERFILE` → root `Dockerfile`.

Build logs should show `FROM python:3.11-slim` and `pip install`, **not** Nixpacks `nodejs_18` only.

## Stack reminder

| Piece | Role |
|-------|------|
| **GitHub** | Source; push triggers Railway |
| **Railway** | Builds Docker image, runs gunicorn on `$PORT` (8080) |
| **GoDaddy** | DNS only — point domains at Railway |
