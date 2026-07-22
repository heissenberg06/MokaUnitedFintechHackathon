"""Moko_United/jira-klon/server.py için birim + entegrasyon testleri.

Kapsam: SLA hesaplama, durum makinesi (ALLOWED_TRANSITIONS), itiraz sisteminden
gelen "status" override'ı ('beklemede' ile doğrudan oluşturma — normalde 'yeni'
durumundan bu duruma doğrudan geçiş YASAK olduğu için bu override ayrı test
edilir), etiketleme/otomatik fraud-ring etiketi ve API uçları.
"""
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from helpers import load_module, LiveServer, http_json, MOKO_UNITED  # noqa: E402

MODULE_PATH = os.path.join(MOKO_UNITED, "jira-klon", "server.py")


def fresh_module():
    return load_module(f"jira_klon_server_under_test_{time.time_ns()}", MODULE_PATH)


class TestStateMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_yeni_cannot_transition_directly_to_beklemede(self):
        # itiraz entegrasyonunun neden create-time override kullandığını doğrular:
        # normal akışta "yeni" -> "beklemede" YASAK bir geçiştir.
        self.assertNotIn("beklemede", self.m.ALLOWED_TRANSITIONS["yeni"])

    def test_allowed_transitions_are_symmetRical_where_expected(self):
        self.assertIn("siniflandirildi", self.m.ALLOWED_TRANSITIONS["yeni"])
        self.assertIn("kapandi", self.m.ALLOWED_TRANSITIONS["yeni"])

    def test_terminal_states_can_reopen(self):
        self.assertEqual(self.m.ALLOWED_TRANSITIONS["kapandi"], {"yeniden-acildi"})
        self.assertIn("yeniden-acildi", self.m.ALLOWED_TRANSITIONS["cozuldu"])


class TestSlaHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_sla_state_ok_for_resolved_issue_even_if_overdue(self):
        now = datetime.now()
        issue = {"status": "cozuldu", "sla_due_at": (now - timedelta(hours=100)).isoformat(),
                  "createdAt": (now - timedelta(hours=200)).isoformat()}
        self.assertEqual(self.m.sla_state_of(issue, now), "ok")

    def test_sla_state_breach_when_past_due(self):
        now = datetime.now()
        issue = {"status": "islemde", "sla_due_at": (now - timedelta(hours=1)).isoformat(),
                  "createdAt": (now - timedelta(hours=25)).isoformat()}
        self.assertEqual(self.m.sla_state_of(issue, now), "breach")

    def test_sla_state_risk_when_close_to_due(self):
        now = datetime.now()
        created = now - timedelta(hours=23)
        due = created + timedelta(hours=24)  # 1 saat / 24 saat kaldı -> %4 <= %20
        issue = {"status": "islemde", "sla_due_at": due.isoformat(), "createdAt": created.isoformat()}
        self.assertEqual(self.m.sla_state_of(issue, now), "risk")

    def test_sla_state_ok_when_plenty_of_time_left(self):
        now = datetime.now()
        created = now - timedelta(hours=1)
        due = created + timedelta(hours=24)
        issue = {"status": "yeni", "sla_due_at": due.isoformat(), "createdAt": created.isoformat()}
        self.assertEqual(self.m.sla_state_of(issue, now), "ok")

    def test_sla_remaining_label_for_completed_issue(self):
        issue = {"status": "kapandi", "sla_due_at": datetime.now().isoformat()}
        self.assertEqual(self.m.sla_remaining_label(issue), "tamamlandı")

    def test_auto_labels_flags_fraud_ring_for_unauthorized_category_with_merchant(self):
        labels = self.m._auto_labels("Yetkisiz İşlem", "Hızlı Ödeme Bayii")
        self.assertIn("olasi-fraud-ring", labels)

    def test_auto_labels_empty_without_merchant(self):
        self.assertEqual(self.m._auto_labels("Yetkisiz İşlem", ""), [])

    def test_auto_labels_empty_for_other_categories(self):
        self.assertEqual(self.m._auto_labels("Para İadesi", "Herhangi Bir İşyeri"), [])


class TestNameHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_mask_and_initials(self):
        self.assertEqual(self.m.mask_name("Ahmet Kaya"), "A** K**")
        self.assertEqual(self.m.initials("Ahmet Kaya"), "AK")


class TestHttpIntegration(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()
        self.tmp = tempfile.mkdtemp()
        self.srv = LiveServer(self.m, self.tmp, "issues.json").start()

    def tearDown(self):
        self.srv.stop()

    def _valid_payload(self, **overrides):
        payload = {
            "reporter": "Kart Hamili",
            "summary": "İtiraz talebi test özeti burada",
            "description": "Bu itiraz talebinin açıklaması yeterince uzun olmalı ki doğrulamayı geçsin.",
            "category": "Yetkisiz İşlem",
            "priority": "yuksek",
            "source": "self-service",
        }
        payload.update(overrides)
        return payload

    def test_create_issue_defaults_to_yeni_status(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "yeni")

    def test_create_issue_with_status_override_from_itiraz_integration(self):
        # itiraz_server.py entegrasyonunun tam olarak yaptığı şey: doğrudan "beklemede"
        # durumuyla oluşturma (create-then-patch değil, çünkü yeni->beklemede yasak).
        status, body = http_json("POST", f"{self.srv.base_url}/api/issues",
                                  self._valid_payload(status="beklemede", merchant="Hızlı Ödeme Bayii"))
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "beklemede")
        self.assertIn("olasi-fraud-ring", body["labels"])

    def test_create_issue_invalid_status_falls_back_to_yeni(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/issues",
                                  self._valid_payload(status="not-a-real-status"))
        self.assertEqual(status, 201)
        self.assertEqual(body["status"], "yeni")

    def test_create_issue_rejects_short_summary(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/issues",
                                  self._valid_payload(summary="kisa"))
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "summary")

    def test_update_issue_valid_transition_succeeds(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        status, body = http_json("PATCH", f"{self.srv.base_url}/api/issues/{created['id']}",
                                  {"status": "siniflandirildi"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "siniflandirildi")

    def test_update_issue_invalid_transition_rejected(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        # "yeni" -> "islemde" doğrudan izinli değil.
        status, body = http_json("PATCH", f"{self.srv.base_url}/api/issues/{created['id']}",
                                  {"status": "islemde"})
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "status")

    def test_list_issues_filters_by_status(self):
        http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload(status="beklemede"))
        http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/issues?status=beklemede")
        self.assertEqual(status, 200)
        self.assertTrue(all(i["status"] == "beklemede" for i in body["items"]))
        self.assertGreaterEqual(body["total"], 1)

    def test_dashboard_endpoint_returns_kpis(self):
        http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        status, body = http_json("GET", f"{self.srv.base_url}/api/dashboard")
        self.assertEqual(status, 200)
        self.assertIn("kpis", body)
        self.assertGreaterEqual(body["kpis"]["total"], 1)

    def test_toggle_task_flips_done_state(self):
        _, created = http_json("POST", f"{self.srv.base_url}/api/issues", self._valid_payload())
        status, body = http_json("PATCH", f"{self.srv.base_url}/api/issues/{created['id']}/tasks/0",
                                  {"done": True})
        self.assertEqual(status, 200)
        self.assertTrue(body["tasks"][0]["done"])

    def test_meta_endpoint_exposes_allowed_transitions(self):
        status, body = http_json("GET", f"{self.srv.base_url}/api/meta")
        self.assertEqual(status, 200)
        self.assertNotIn("beklemede", body["allowed_transitions"]["yeni"])


if __name__ == "__main__":
    unittest.main()
