FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT at runtime (public networking uses 8080)
CMD sh -c "gunicorn --bind 0.0.0.0:${PORT:-8080} app:app"
