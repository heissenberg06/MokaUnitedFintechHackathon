#!/usr/bin/env bash
# Şikayetvar klonu + otomatik sınıflandırma/cevap servisini tek komutla başlatır.
#   sikayet_api  -> http://localhost:8020  (model, /cevapla)
#   sikayetvar   -> http://localhost:8756  (klon site + API)
set -e
cd "$(dirname "$0")"
source venv/bin/activate

uvicorn sikayet_api:app --port 8020 &
API_PID=$!
python3 Moko_United/sikayetvar/server.py &
SV_PID=$!

trap 'kill "$API_PID" "$SV_PID" 2>/dev/null' EXIT INT TERM
wait
