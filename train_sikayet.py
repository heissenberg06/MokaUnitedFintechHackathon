# -*- coding: utf-8 -*-
"""
Şikayet sınıflandırıcı eğitimi (BERTurk, 7 sınıf).
Kurulum:  pip install transformers torch datasets scikit-learn pandas accelerate
Çalıştır: python train_sikayet.py
Çıktı:    ./moka-sikayet-model/
"""
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, TrainerCallback, DataCollatorWithPadding)

MODEL_NAME = "dbmdz/bert-base-turkish-cased"
LABELS = ["tanimadigi_islem_kart","dolandiricilik_suphesi","abonelik_tekrarlayan",
          "iade_gecikmesi","urun_hizmet_sorunu","cuzdan_hesap_sorunu","zaten_cozuldu_diger"]
label2id = {l:i for i,l in enumerate(LABELS)}; id2label = {i:l for l,i in label2id.items()}

class Bar(TrainerCallback):
    def on_step_end(self,a,s,c,**k):
        p=s.global_step/max(s.max_steps,1); f=int(30*p)
        print(f"\r  [{'█'*f}{'░'*(30-f)}] {p*100:5.1f}%  adım {s.global_step}/{s.max_steps}",end="",flush=True)
    def on_evaluate(self,a,s,c,metrics=None,**k):
        acc=(metrics or {}).get("eval_accuracy")
        print(f"\n  → epoch {s.epoch:.0f} | acc: {acc:.3f}" if acc else "")

df = pd.read_csv("moka_sikayet_dataset.csv"); df["labels"]=df["sinif"].map(label2id)
tr,te = train_test_split(df,test_size=0.2,stratify=df["labels"],random_state=42)
tok = AutoTokenizer.from_pretrained(MODEL_NAME)
def ds(fr): 
    d=Dataset.from_pandas(fr[["sikayet_metni","labels"]].rename(columns={"sikayet_metni":"text"}),preserve_index=False)
    return d.map(lambda b:tok(b["text"],truncation=True,max_length=96),batched=True)
train_ds,test_ds = ds(tr),ds(te)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME,num_labels=len(LABELS),id2label=id2label,label2id=label2id)
args = TrainingArguments(output_dir="./_ck",num_train_epochs=8,per_device_train_batch_size=16,
    per_device_eval_batch_size=16,learning_rate=2e-5,eval_strategy="epoch",save_strategy="no",
    logging_strategy="no",disable_tqdm=True,report_to="none")
def m(p): return {"accuracy":float((np.argmax(p.predictions,1)==p.label_ids).mean())}
tr_ = Trainer(model=model,args=args,train_dataset=train_ds,eval_dataset=test_ds,
    processing_class=tok,data_collator=DataCollatorWithPadding(tok),compute_metrics=m,callbacks=[Bar()])
tr_.train()
preds=np.argmax(tr_.predict(test_ds).predictions,1)
print("\n=== TEST RAPORU ==="); print(classification_report(test_ds["labels"],preds,target_names=LABELS,digits=3))
model.save_pretrained("./moka-sikayet-model"); tok.save_pretrained("./moka-sikayet-model")
print("Kaydedildi -> ./moka-sikayet-model")
