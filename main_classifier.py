"""
Moka Asistan — sınıflandırıcı backend (test sürümü)
Eğittiğin ./moka-intent-model modelini yükler, /chat endpoint'i sunar
ve demo sayfasını (index.html) da kendi üstünden servis eder.

Çalıştırma:
    pip install fastapi "uvicorn[standard]"
    uvicorn main_classifier:app --port 8000
Sonra tarayıcıda aç:  http://localhost:8000
"""

import torch
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = "./moka-intent-model"

# --- Modeli bir kez belleğe al (CPU yeterli, tek cümle sınıflandırması hızlı) ---
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()
id2label = model.config.id2label   # {0: 'itiraz', 1: 'diger', 2: 'belirsiz'}

# --- Her niyet için şablon yanıt ---
REPLIES = {
    "itiraz": "Anladım. Tanımadığınız bir işlem veya itiraz konusunda size yardımcı olabilirim. "
              "İşleminizi sorgulamak ve gerekirse itirazınızı başlatmak için aşağıdaki portaldan devam edebilirsiniz.",
    "belirsiz": "Size doğru şekilde yardımcı olabilmem için biraz detay verebilir misiniz? "
                "Örneğin kart ekstrenizde tanımadığınız bir işlem mi var?",
    "diger": "Ben özellikle kart işlemleri ve itiraz konularında yardımcı oluyorum. "
             "İşleminizle ilgili bir sorun varsa memnuniyetle yardımcı olurum; "
             "diğer konular için Moka United destek ekibine ulaşabilirsiniz.",
}

app = FastAPI(title="Moka Asistan — Classifier")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


def classify(text: str) -> str:
    inputs = tok(text, return_tensors="pt", truncation=True, max_length=64)
    with torch.no_grad():
        logits = model(**inputs).logits
    return id2label[int(logits.argmax())]


@app.post("/chat")
def chat(req: ChatRequest):
    # son kullanıcı mesajını sınıflandır
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    intent = classify(last_user)
    print(f"[intent] '{last_user}' -> {intent}")   # terminalde görebilmen için
    return {
        "reply": REPLIES[intent],
        "redirect": intent == "itiraz",
        "intent": intent,
    }


@app.get("/")
def index():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {"ok": True}
