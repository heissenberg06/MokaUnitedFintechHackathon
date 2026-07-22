"""Moko_United/sikayetvar/server.py için birim + entegrasyon testleri.

Kapsam: doğrulama fonksiyonları, isim maskeleme, `_public()` ile 'contact'
alanının asla dışarı sızmaması (KVKK/gizlilik sınırı), KVKK onayı zorunluluğu,
oto-yanıt entegrasyonu (sikayet_api kapalıyken sessiz düşme) ve temel API uçları.
"""
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from helpers import load_module, LiveServer, http_json, MOKO_UNITED  # noqa: E402

MODULE_PATH = os.path.join(MOKO_UNITED, "sikayetvar", "server.py")
SIKAYETVAR_DIR = os.path.join(MOKO_UNITED, "sikayetvar")


def fresh_module():
    return load_module(f"sikayetvar_server_under_test_{time.time_ns()}", MODULE_PATH,
                        extra_syspath=SIKAYETVAR_DIR)


class TestValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_v_name_rejects_too_short_and_non_letters(self):
        self.assertIsNone(self.m.v_name("Ahmet Kaya"))
        self.assertIsNotNone(self.m.v_name("A"))
        self.assertIsNotNone(self.m.v_name("Ahmet123"))

    def test_v_phone_normalizes_and_validates(self):
        self.assertIsNone(self.m.v_phone("0555 123 45 67"))
        self.assertIsNone(self.m.v_phone("5551234567"))
        self.assertIsNotNone(self.m.v_phone("123"))

    def test_v_email_optional_but_validated_when_present(self):
        self.assertIsNone(self.m.v_email(""))
        self.assertIsNone(self.m.v_email("user@example.com"))
        self.assertIsNotNone(self.m.v_email("not-an-email"))

    def test_mask_name_produces_initials_pattern(self):
        self.assertEqual(self.m.mask_name("Ahmet Kaya"), "A** K**")
        self.assertEqual(self.m.mask_name(""), "A**")

    def test_initials_handles_single_and_multi_word_names(self):
        self.assertEqual(self.m.initials("Ahmet Kaya"), "AK")
        self.assertEqual(self.m.initials("Ahmet"), "A")
        self.assertEqual(self.m.initials(""), "?")

    def test_clean_escapes_html(self):
        self.assertEqual(self.m.clean("<b>x</b>"), "&lt;b&gt;x&lt;/b&gt;")


class TestPublicProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_public_strips_contact_field(self):
        rec = {"id": 1, "title": "t", "contact": {"phone": "5551234567", "email": "a@b.com"}}
        pub = self.m._public(rec)
        self.assertNotIn("contact", pub)
        self.assertEqual(pub["id"], 1)

    def test_public_is_noop_when_no_contact_key(self):
        rec = {"id": 2, "title": "t"}
        self.assertEqual(self.m._public(rec), rec)


class TestAutoReply(unittest.TestCase):
    def test_get_auto_reply_returns_none_when_service_unreachable(self):
        m = fresh_module()
        # sikayet_api (port 8020) test ortamında kapalı olmalı; bağlantı reddi ->
        # fonksiyon istisnaları yutup None döndürmeli (akış asla kesilmemeli).
        self.assertIsNone(m.get_auto_reply("herhangi bir şikayet metni"))


class TestHttpIntegration(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()
        self.tmp = tempfile.mkdtemp()
        self.srv = LiveServer(self.m, self.tmp, "complaints.json").start()

    def tearDown(self):
        self.srv.stop()

    def _valid_payload(self, **overrides):
        payload = {
            "name": "Ahmet Kaya",
            "title": "POS cihazım hâlâ teslim edilmedi ne yapmalıyım",
            "body": "Sanal POS başvurumun onayından sonra fiziki POS cihazımın teslim edileceği söylenmişti ama gelmedi.",
            "phone": "5551234567",
            "email": "",
            "kvkkConsent": True,
        }
        payload.update(overrides)
        return payload

    def test_create_complaint_requires_kvkk_consent(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/complaints",
                                  self._valid_payload(kvkkConsent=False))
        self.assertEqual(status, 400)
        self.assertIn("KVKK", body["error"])

    def test_create_complaint_success_hides_contact(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        self.assertEqual(status, 201)
        self.assertNotIn("contact", body)
        self.assertEqual(body["name"], "A** K**")

    def test_create_complaint_rejects_invalid_phone(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/complaints",
                                  self._valid_payload(phone="123"))
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "phone")

    def test_list_complaints_never_exposes_contact(self):
        http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/complaints")
        self.assertEqual(status, 200)
        for item in body["items"]:
            self.assertNotIn("contact", item)

    def test_get_single_complaint_by_id(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/complaints/{created['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(body["id"], created["id"])
        self.assertNotIn("contact", body)

    def test_support_counter_increments(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        status, body = http_json("POST", f"{self.srv.base_url}/api/complaints/{created['id']}/support", {})
        self.assertEqual(status, 200)
        self.assertEqual(body["supports"], 1)

    def test_create_comment_requires_valid_name_and_body(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        status, body = http_json(
            "POST", f"{self.srv.base_url}/api/complaints/{created['id']}/comments",
            {"name": "Elif Su", "body": "Bu konuda bilgi rica ederim"})
        self.assertEqual(status, 201)
        self.assertEqual(body["isBrand"], False)

    def test_admin_insights_endpoint_returns_kpis(self):
        http_json("POST", f"{self.srv.base_url}/api/complaints", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/admin/insights")
        self.assertEqual(status, 200)
        self.assertIn("kpis", body)


if __name__ == "__main__":
    unittest.main()
