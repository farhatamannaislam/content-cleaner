# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Change if your app module is different (e.g., src.main:app)
ENV APP_MODULE="main:app" \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000
CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT}"]
