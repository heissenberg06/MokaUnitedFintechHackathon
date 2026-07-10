"""
BERTurk tabanlı niyet sınıflandırıcı — Moka Asistan
3 sınıf: itiraz / diger / belirsiz

Kurulum:
    pip install transformers torch datasets scikit-learn pandas accelerate

Çalıştırma:
    python train_classifier.py

Çıktı:
    ./moka-intent-model/    (eğitilmiş model + tokenizer)
    ekranda test seti raporu (özellikle 'itiraz' recall'una bak)
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    TrainerCallback,
    DataCollatorWithPadding,
)

MODEL_NAME = "dbmdz/bert-base-turkish-cased"
LABELS = ["itiraz", "diger", "belirsiz"]
label2id = {l: i for i, l in enumerate(LABELS)}
id2label = {i: l for l, i in label2id.items()}


# --- Canlı yüzde çubuğu ---
class ProgressBar(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        print("\nEğitim başlıyor...\n")

    def on_step_end(self, args, state, control, **kwargs):
        pct = state.global_step / max(state.max_steps, 1)
        length = 30
        filled = int(length * pct)
        bar = "█" * filled + "░" * (length - filled)
        print(
            f"\r  [{bar}] {pct * 100:5.1f}%  |  adım {state.global_step}/{state.max_steps}"
            f"  |  epoch {state.epoch:.2f}",
            end="",
            flush=True,
        )

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        acc = (metrics or {}).get("eval_accuracy")
        msg = f"\n  → epoch {state.epoch:.0f} bitti"
        if acc is not None:
            msg += f"  |  doğrulama accuracy: {acc:.3f}"
        print(msg)

    def on_train_end(self, args, state, control, **kwargs):
        print("\n\nEğitim tamamlandı ✓\n")


# 1) Veriyi yükle ve böl (stratified: sınıf dağılımı korunur)
df = pd.read_csv("moka_intent_dataset.csv")
df["labels"] = df["label"].map(label2id)

train_df, test_df = train_test_split(
    df, test_size=0.2, stratify=df["labels"], random_state=42
)

tok = AutoTokenizer.from_pretrained(MODEL_NAME)


def to_dataset(frame):
    ds = Dataset.from_pandas(frame[["text", "labels"]], preserve_index=False)
    return ds.map(
        lambda b: tok(b["text"], truncation=True, max_length=64), batched=True
    )


train_ds = to_dataset(train_df)
test_ds = to_dataset(test_df)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=len(LABELS), id2label=id2label, label2id=label2id
)

# NOT: eski transformers sürümlerinde 'eval_strategy' yerine 'evaluation_strategy' kullan
args = TrainingArguments(
    output_dir="./_ckpt",
    num_train_epochs=6,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    eval_strategy="epoch",
    save_strategy="no",
    logging_strategy="no",   # kendi çubuğumuz olduğu için varsayılan log satırlarını kapat
    disable_tqdm=True,       # çift çubuk olmasın
    report_to="none",
)


def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return {"accuracy": float((preds == p.label_ids).mean())}


trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    processing_class=tok,
    data_collator=DataCollatorWithPadding(tok),
    compute_metrics=compute_metrics,
    callbacks=[ProgressBar()],
)

trainer.train()

# 2) Ayrıntılı test raporu — 'itiraz' recall en kritik metrik
preds = np.argmax(trainer.predict(test_ds).predictions, axis=1)
print("=== TEST SETİ RAPORU ===")
print(classification_report(test_df["labels"], preds, target_names=LABELS, digits=3))

# 3) Modeli kaydet
model.save_pretrained("./moka-intent-model")
tok.save_pretrained("./moka-intent-model")
print("\nModel kaydedildi -> ./moka-intent-model")


# 4) Hızlı deneme (isteğe bağlı)
def predict(text: str) -> str:
    import torch

    inputs = tok(text, return_tensors="pt", truncation=True, max_length=64)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
    return id2label[int(logits.argmax())]


for ornek in [
    "ekstremde moka diye bir çekim var tanımıyorum",
    "üye işyeri olmak istiyorum",
    "merhaba yardım lazım",
]:
    print(f"  '{ornek}' -> {predict(ornek)}")