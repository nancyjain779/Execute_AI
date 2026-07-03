FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgl1 && \
    mkdir -p /app/cache /app/models && chmod -R 777 /app/cache /app/models

ENV HF_HOME=/app/cache
ENV MODELS_DIR=/app/models

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bundled models: filter/models/toxic-bert + identity-hate-detector (~837 MB)
# model_loader.py falls back to Hugging Face hub if local files are missing

ENV PORT=7860
EXPOSE 7860

CMD ["python", "api.py"]
