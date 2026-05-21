# Vector Website — Docker setup

This folder deploys as a **Docker image** (Flask + gunicorn). Railway does **not** use Nixpacks anymore.

## Files that matter

| File | Role |
|------|------|
| `Dockerfile` | How the image is built |
| `.dockerignore` | What is excluded from the image |
| `docker-compose.yml` | Easy local run |
| `railway.json` | Tells Railway: `builder: DOCKERFILE` |
| `scripts/run-local-docker.sh` | Same as compose, one command |

There is **no** `nixpacks.toml` in this repo root (removed on purpose).

---

## 1. Code layout (already done)

- Python app entry: `app.py`
- Dependencies: `requirements.txt`
- Production server: gunicorn in `Dockerfile` `CMD`
- Port **8080** inside the container (`PORT` env; Railway public networking uses 8080)

---

## 2. Run locally with Docker Desktop

### Install (one time)

1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. Install and open **Docker Desktop**
3. Wait until the whale icon says **Running**

### Run the site

**Easiest — Docker Desktop + terminal**

```bash
cd /Users/drewwood/Desktop/Vector/Website
docker compose up --build
```

Or:

```bash
./scripts/run-local-docker.sh
```

Open in browser: **http://127.0.0.1:5005**

Stop: `Ctrl+C` in the terminal, or in Docker Desktop → **Containers** → stop `website-web-1`.

### Optional env vars

```bash
cp .env.example .env   # if you have secrets for Dash API etc.
# edit .env, then run compose again
```

### See the image in Docker Desktop

After `docker compose up --build`:

- **Images** → `website-web` or `vector-website:local`
- **Containers** → running container → logs / port `5005:8080`

---

## 3. GitHub → Railway (Docker deploy)

### Push code

```bash
cd /Users/drewwood/Desktop/Vector/Website
git status
git add -A
git commit -m "your message"
git push origin main
```

Railway (connected to `Vector-IT-Drew/Website`) builds from **`Dockerfile`** automatically when `railway.json` is on `main`.

### Railway dashboard — fix Nixpacks overrides

In Railway → **Website** service:

1. **Settings → Build**
   - Builder should be **Dockerfile** (from repo `railway.json`)
   - Dockerfile path: `Dockerfile`
2. **Settings → Deploy**
   - **Remove** any custom **Start Command** (leave empty so Docker `CMD` runs)
   - Do **not** set a Nixpacks start command like `gunicorn app:app` alone
3. **Settings → Networking**
   - Target port: **8080**

### Good build log (Docker)

You should see:

```
FROM python:3.11-slim
RUN pip install --no-cache-dir -r requirements.txt
```

You should **not** see:

```
Nixpacks v1.41.0
nodejs_18, npm-9_x
```

### Domains (GoDaddy)

| Domain | Fix |
|--------|-----|
| `www.vectorny.com` | DNS at GoDaddy → Railway records |
| `vectorny.com` | Apex DNS at GoDaddy (Railway “Show DNS records”) |

Docker does not configure GoDaddy — only DNS records there.

---

## Quick commands

```bash
# Build only
docker build -t vector-website:local .

# Run without compose
docker run --rm -p 5005:8080 -e PORT=8080 vector-website:local

# Shell inside container (debug)
docker run --rm -it -p 5005:8080 -e PORT=8080 vector-website:local sh
```
