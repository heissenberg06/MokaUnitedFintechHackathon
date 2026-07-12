# -*- coding: utf-8 -*-
"""
Şikayet otomatik cevap servisi.
Şikayetvar klonun bir şikayet POST eder -> model sınıflandırır -> sabit cevap döner.

Kurulum:  pip install fastapi "uvicorn[standard]" transformers torch
Çalıştır: uvicorn sikayet_api:app --port 8020
Endpoint: POST /cevapla   { "sikayet_metni": "..." }
          -> { "sinif": "...", "guven": 0.97, "cevap": "..." }
"""
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sablonlar import CEVAPLAR

MODEL_DIR = "./moka-sikayet-model"
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR); model.eval()
id2label = model.config.id2label

app = FastAPI(title="Moka Şikayet Cevap Servisi")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"], allow_headers=["*"])

class Sikayet(BaseModel):
    sikayet_metni: str

@app.post("/cevapla")
def cevapla(s: Sikayet):
    inputs = tok(s.sikayet_metni, return_tensors="pt", truncation=True, max_length=96)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    idx = int(probs.argmax())
    sinif = id2label[idx]
    print(f"[sinif] {sinif} ({float(probs[idx]):.2f}) <- {s.sikayet_metni[:60]}")
    return {
        "sinif": sinif,
        "guven": round(float(probs[idx]), 3),
        "cevap": CEVAPLAR[sinif],   # sabit metin, generation yok
    }

@app.get("/health")
def health(): return {"ok": True}
