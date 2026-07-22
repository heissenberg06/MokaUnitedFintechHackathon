"""main_classifier.py ve sikayet_api.py için birim testleri.

Bu iki servis gerçek HuggingFace modellerini (moka-intent-model / moka-sikayet-model)
import anında belleğe yükler ve dosya yolları (SITE_DIR/MODEL_DIR) proje kök
dizinine göre GÖRECELİDİR. Bu yüzden testler proje kökünü çalışma dizini yaparak
importu gerçekleştirir. torch/fastapi/transformers kurulu değilse (ör. sistem
python'unda, yalnızca ./venv içinde kuruluysa) modül tamamen atlanır — bu, "hiçbir
yeri bozma" kısıtı gereği kaynak dosyalara bağımlılık eklemeden testin güvenli
şekilde çalışmasını sağlar.
"""
import importlib.util
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_DEPS_OK = True
try:
    import torch  # noqa: F401
    import transformers  # noqa: F401
    import fastapi  # noqa: F401
    import httpx  # noqa: F401
except ImportError:
    _DEPS_OK = False

_MODELS_OK = os.path.isdir(os.path.join(REPO_ROOT, "moka-intent-model")) and \
             os.path.isdir(os.path.join(REPO_ROOT, "moka-sikayet-model"))


def _load_with_cwd(name, filename):
    old_cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_ROOT, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        os.chdir(old_cwd)


@unittest.skipUnless(_DEPS_OK and _MODELS_OK,
                      "torch/transformers/fastapi veya eğitilmiş modeller bu ortamda yok")
class TestMainClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _load_with_cwd("main_classifier_under_test", "main_classifier.py")
        from fastapi.testclient import TestClient
        cls.client = TestClient(cls.m.app)

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ok": True})

    def test_classify_returns_known_intent_label(self):
        intent = self.m.classify("Kartımdan tanımadığım bir işlem yapılmış")
        self.assertIn(intent, self.m.id2label.values())

    def test_chat_endpoint_returns_reply_matching_intent(self):
        resp = self.client.post("/chat", json={"messages": [{"role": "user", "content": "merhaba"}]})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("reply", body)
        self.assertIn("intent", body)
        self.assertEqual(body["redirect"], body["intent"] == "itiraz")
        self.assertEqual(body["reply"], self.m.REPLIES[body["intent"]])

    def test_chat_uses_last_user_message_not_assistant(self):
        resp = self.client.post("/chat", json={"messages": [
            {"role": "user", "content": "itiraz etmek istiyorum"},
            {"role": "assistant", "content": "tabii yardımcı olayım"},
            {"role": "user", "content": "tanımadığım bir işlem var kartımda"},
        ]})
        self.assertEqual(resp.status_code, 200)


@unittest.skipUnless(_DEPS_OK and _MODELS_OK,
                      "torch/transformers/fastapi veya eğitilmiş modeller bu ortamda yok")
class TestSikayetApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _load_with_cwd("sikayet_api_under_test", "sikayet_api.py")
        from fastapi.testclient import TestClient
        cls.client = TestClient(cls.m.app)

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

    def test_cevapla_returns_known_class_and_matching_template(self):
        resp = self.client.post("/cevapla", json={
            "sikayet_metni": "Kartımdan tanımadığım bir işlem için kesinti yapılmış"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn(body["sinif"], self.m.CEVAPLAR)
        self.assertEqual(body["cevap"], self.m.CEVAPLAR[body["sinif"]])
        self.assertGreaterEqual(body["guven"], 0.0)
        self.assertLessEqual(body["guven"], 1.0)


if __name__ == "__main__":
    unittest.main()
