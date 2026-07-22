"""Moko_United/next4biz-klon/server.py için birim + entegrasyon testleri.

jira-klon ile aynı state-machine/SLA desenini paylaşan, daha basit (issuetype/
labels/story_points olmayan) ticket modelidir. Bu dosyada AI <-> ticket köprüsü
kasıtlı olarak yoktur (bkz. modülün docstring'i); testler bunu varsayım olarak
almaz, yalnızca mevcut deterministik davranışı doğrular.
"""
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from helpers import load_module, LiveServer, http_json, MOKO_UNITED  # noqa: E402

MODULE_PATH = os.path.join(MOKO_UNITED, "next4biz-klon", "server.py")


def fresh_module():
    return load_module(f"next4biz_klon_server_under_test_{time.time_ns()}", MODULE_PATH)


class TestStateMachineAndSla(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_yeni_cannot_transition_directly_to_beklemede(self):
        self.assertNotIn("beklemede", self.m.ALLOWED_TRANSITIONS["yeni"])

    def test_sla_state_breach_when_past_due(self):
        now = datetime.now()
        ticket = {"status": "atandi", "sla_due_at": (now - timedelta(hours=1)).isoformat(),
                  "createdAt": (now - timedelta(hours=25)).isoformat()}
        self.assertEqual(self.m.sla_state_of(ticket, now), "breach")

    def test_sla_state_ok_for_closed_ticket(self):
        now = datetime.now()
        ticket = {"status": "kapandi", "sla_due_at": (now - timedelta(hours=50)).isoformat(),
                  "createdAt": (now - timedelta(hours=100)).isoformat()}
        self.assertEqual(self.m.sla_state_of(ticket, now), "ok")


class TestHttpIntegration(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()
        self.tmp = tempfile.mkdtemp()
        self.srv = LiveServer(self.m, self.tmp, "tickets.json").start()

    def tearDown(self):
        self.srv.stop()

    def _valid_payload(self, **overrides):
        payload = {
            "requester_name": "Ayşe Yılmaz",
            "title": "Ödeme linkim müşterilerimde açılmıyor bir türlü",
            "body": "Gönderdiğim ödeme linki bazı telefonlarda hata veriyor ve satış kaybediyorum.",
            "category": "Ödeme Linki",
            "priority": "orta",
            "source": "self-service",
        }
        payload.update(overrides)
        return payload

    def test_create_ticket_defaults_to_yeni(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/tickets", self._valid_payload())
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "yeni")

    def test_create_ticket_rejects_invalid_category(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/tickets",
                                  self._valid_payload(category="Uydurma Kategori"))
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "category")

    def test_update_ticket_invalid_transition_rejected(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/tickets", self._valid_payload())
        status, body = http_json("PATCH", f"{self.srv.base_url}/api/tickets/{created['id']}",
                                  {"status": "cozuldu"})
        self.assertEqual(status, 400)

    def test_update_ticket_valid_transition_succeeds(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/tickets", self._valid_payload())
        status, body = http_json("PATCH", f"{self.srv.base_url}/api/tickets/{created['id']}",
                                  {"status": "siniflandirildi"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "siniflandirildi")

    def test_dashboard_returns_kpis(self):
        http_json("POST", f"{self.srv.base_url}/api/tickets", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/dashboard")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(body["kpis"]["total"], 1)

    def test_add_note_and_attachment(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/tickets", self._valid_payload())
        status, _ = http_json("POST", f"{self.srv.base_url}/api/tickets/{created['id']}/notes",
                               {"note": "Takip edildi"})
        self.assertEqual(status, 201)
        status, _ = http_json("POST", f"{self.srv.base_url}/api/tickets/{created['id']}/attachments",
                               {"name": "ekran-goruntusu.png"})
        self.assertEqual(status, 201)


if __name__ == "__main__":
    unittest.main()
