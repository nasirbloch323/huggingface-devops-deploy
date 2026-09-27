from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="AI Model Deployment API", version="1.0")

# Model ek dafa load hoga jab app start ho (startup pe), har request pe nahi.
# Ye "sentiment-analysis" task hai -- text positive hai ya negative, ye batata hai.
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label: str
    score: float


@app.get("/")
def home():
    return {"message": "AI Model Deployment API is running", "docs": "/docs"}


@app.get("/health")
def health():
    # Kubernetes liveness/readiness probes ke liye zaroori endpoint
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    result = classifier(request.text)[0]
    return PredictResponse(label=result["label"], score=round(result["score"], 4))
