FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m appuser
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
RUN chown -R appuser:appuser /app
USER appuser
ENV PORT=8001
EXPOSE 8001
CMD ["sh", "-c", "uvicorn apiserver:app --host 127.0.0.1 --port ${PORT:-8001} --workers 1"]
