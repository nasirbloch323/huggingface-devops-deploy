FROM python:3.11-slim

WORKDIR /app

# System dependencies (torch ke liye zaroori)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pehle sirf requirements copy karo -- Docker layer caching se rebuild fast hoga
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ab poora code copy karo
COPY . .

# Model ko build time pe hi download kar lo, taake container start hote hi ready ho
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
