"""Moko_United/itiraz_server.py için birim + entegrasyon testleri.

Kapsam: rate limiting, multipart/form-data ayrıştırma, mükerrer itiraz (dedup)
kontrolü, doğrulama fonksiyonları ve HTTP uçları (attempt/create/status/advance).
Gerçek dosya sistemine yazma her testte geçici bir klasöre yönlendirilir; proje
kaynak dosyası hiçbir şekilde değiştirilmez. jira-klon entegrasyonu ve e-posta
gönderimi (SMTP yapılandırılmadığı sürece) ağa çıkmadan sessizce atlanır.
"""
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from helpers import load_module, LiveServer, http_json, http_multipart_post, MOKO_UNITED  # noqa: E402

MODULE_PATH = os.path.join(MOKO_UNITED, "itiraz_server.py")


def fresh_module():
    # Her çağrıda yeni modül nesnesi -> LOCK/_QUERY_HITS/_CREATE_HITS taze başlar.
    return load_module(f"itiraz_server_under_test_{time.time_ns()}", MODULE_PATH)


class TestPureHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = fresh_module()

    def test_clean_escapes_html_and_truncates(self):
        self.assertEqual(self.m.clean("<script>alert(1)</script>"),
                          "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertEqual(self.m.clean("x" * 10, maxlen=5), "xxxxx")

    def test_clean_handles_none_and_whitespace(self):
        self.assertEqual(self.m.clean(None), "")
        self.assertEqual(self.m.clean("  padded  "), "padded")

    def test_v_required_enforces_length_bounds(self):
        self.assertIsNone(self.m.v_required("abc", 2, 5, "Alan"))
        self.assertIsNotNone(self.m.v_required("a", 2, 5, "Alan"))
        self.assertIsNotNone(self.m.v_required("abcdefgh", 2, 5, "Alan"))
        self.assertIsNotNone(self.m.v_required(None, 2, 5, "Alan"))

    def test_phone_regex_accepts_turkish_mobile_formats(self):
        self.assertRegex("5551234567", self.m.PHONE_RE)
        self.assertRegex("05551234567", self.m.PHONE_RE)
        self.assertNotRegex("5551234", self.m.PHONE_RE)
        self.assertNotRegex("15551234567", self.m.PHONE_RE)

    def test_rate_check_allows_up_to_max_then_blocks(self):
        bucket = {}
        ip = "1.2.3.4"
        for _ in range(3):
            ok, retry = self.m.rate_check(bucket, ip, window_s=60, max_hits=3)
            self.assertTrue(ok)
        ok, retry = self.m.rate_check(bucket, ip, window_s=60, max_hits=3)
        self.assertFalse(ok)
        self.assertGreaterEqual(retry, 1)

    def test_rate_check_is_per_ip(self):
        bucket = {}
        for _ in range(3):
            self.m.rate_check(bucket, "1.1.1.1", window_s=60, max_hits=3)
        ok, _ = self.m.rate_check(bucket, "2.2.2.2", window_s=60, max_hits=3)
        self.assertTrue(ok)

    def test_rate_check_window_expiry_allows_retry(self):
        bucket = {"9.9.9.9": [time.time() - 1000]}  # çok eski bir vuruş
        ok, _ = self.m.rate_check(bucket, "9.9.9.9", window_s=60, max_hits=1)
        self.assertTrue(ok)


class TestFindOpenCaseByRef(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()

    def test_finds_open_case_within_dedup_window(self):
        now = datetime.now()
        data = {"cases": {"MU-1": {"caseId": "MU-1", "ref": "REF1", "stage": 1,
                                    "createdAt": now.isoformat()}}}
        found = self.m.find_open_case_by_ref(data, "REF1")
        self.assertIsNotNone(found)
        self.assertEqual(found["caseId"], "MU-1")

    def test_ignores_case_outside_dedup_window(self):
        old = datetime.now() - timedelta(seconds=self.m.DISPUTE_DEDUP_WINDOW_S + 60)
        data = {"cases": {"MU-1": {"caseId": "MU-1", "ref": "REF1", "stage": 1,
                                    "createdAt": old.isoformat()}}}
        self.assertIsNone(self.m.find_open_case_by_ref(data, "REF1"))

    def test_ignores_closed_stage_case(self):
        now = datetime.now()
        data = {"cases": {"MU-1": {"caseId": "MU-1", "ref": "REF1",
                                    "stage": self.m.CLOSED_STAGE, "createdAt": now.isoformat()}}}
        self.assertIsNone(self.m.find_open_case_by_ref(data, "REF1"))

    def test_ignores_different_ref(self):
        now = datetime.now()
        data = {"cases": {"MU-1": {"caseId": "MU-1", "ref": "OTHER", "stage": 1,
                                    "createdAt": now.isoformat()}}}
        self.assertIsNone(self.m.find_open_case_by_ref(data, "REF1"))


class TestMultipartParsing(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()

    def _build(self, fields, files=None):
        from helpers import build_multipart
        return build_multipart(fields, files)

    def test_parses_simple_text_fields(self):
        ctype, body = self._build({"Reason": "hirsizlik", "Ref": "REF123"})
        form = self.m.parse_multipart(body, ctype)
        self.assertEqual(form.getvalue("Reason"), "hirsizlik")
        self.assertEqual(form.getvalue("Ref"), "REF123")
        self.assertIn("Reason", form)
        self.assertNotIn("Missing", form)

    def test_parses_uploaded_file_and_preserves_content(self):
        ctype, body = self._build(
            {"Reason": "test"},
            files=[("Evidence", "kanit.pdf", "application/pdf", b"%PDF-1.4 fake content")])
        form = self.m.parse_multipart(body, ctype)
        f = form["Evidence"]
        self.assertEqual(f.filename, "kanit.pdf")
        self.assertEqual(f.type, "application/pdf")
        self.assertEqual(f.file.read(), b"%PDF-1.4 fake content")

    def test_multiple_files_with_same_field_name_become_list(self):
        ctype, body = self._build({}, files=[
            ("Evidence", "a.pdf", "application/pdf", b"AAA"),
            ("Evidence", "b.jpg", "image/jpeg", b"BBB"),
        ])
        form = self.m.parse_multipart(body, ctype)
        items = form["Evidence"]
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 2)

    def test_missing_boundary_raises(self):
        with self.assertRaises(ValueError):
            self.m.parse_multipart(b"irrelevant", "multipart/form-data")


class TestHttpIntegration(unittest.TestCase):
    def setUp(self):
        self.m = fresh_module()
        # jira-klon entegrasyonu ve e-posta ağa çıkmasın; testler hızlı ve izole kalsın.
        self.m.create_jira_issue_async = lambda *a, **k: None
        self.m.send_email_async = lambda *a, **k: None
        self.tmp = tempfile.mkdtemp()
        self.srv = LiveServer(self.m, self.tmp, "itiraz.json").start()

    def tearDown(self):
        self.srv.stop()

    def _create_valid_case(self, ref="TXN-REF-001", phone="5551234567", email=""):
        fields = {
            "Reason": "Kartimdan habersiz islem yapildi",
            "TxnType": "Yetkisiz İşlem",
            "Ref": ref,
            "Merchant": "Test Mağaza",
            "Amount": "199.90",
            "Note": "Bu islemi hic yapmadim, itiraz ediyorum lutfen inceleyin.",
            "Phone": phone,
            "Email": email,
        }
        return http_multipart_post(f"{self.srv.base_url}/api/itiraz/create", fields)

    def test_attempt_endpoint_returns_allowed_and_remaining(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/itiraz/attempt", {})
        self.assertEqual(status, 200)
        self.assertTrue(body["allowed"])
        self.assertEqual(body["remaining"], self.m.QUERY_MAX - 1)

    def test_attempt_rate_limits_after_max_hits(self):
        for _ in range(self.m.QUERY_MAX):
            http_json("POST", f"{self.srv.base_url}/api/itiraz/attempt", {})
        status, body = http_json("POST", f"{self.srv.base_url}/api/itiraz/attempt", {})
        self.assertEqual(status, 429)
        self.assertEqual(body["error"], "rate_limited")

    def test_create_rejects_non_multipart_content_type(self):
        status, body = http_json("POST", f"{self.srv.base_url}/api/itiraz/create", {"foo": "bar"})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_content_type")

    def test_create_success_returns_case_with_masked_phone(self):
        status, body = self._create_valid_case(phone="5551234567")
        self.assertEqual(status, 201)
        self.assertEqual(body["stage"], 1)
        self.assertTrue(body["caseId"].startswith("MU-ITZ-"))
        self.assertEqual(body["phone"], "5551 *** ** 67")

    def test_create_rejects_invalid_phone(self):
        status, body = self._create_valid_case(ref="TXN-BADPHONE", phone="123")
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "Phone")

    def test_create_rejects_invalid_email_when_provided(self):
        status, body = self._create_valid_case(ref="TXN-BADEMAIL", email="not-an-email")
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "Email")

    def test_create_rejects_too_short_note(self):
        fields = {
            "Reason": "kisa", "TxnType": "x", "Ref": "TXN-SHORTNOTE",
            "Merchant": "M", "Amount": "10", "Note": "kisa", "Phone": "5551234567", "Email": "",
        }
        status, body = http_multipart_post(f"{self.srv.base_url}/api/itiraz/create", fields)
        self.assertEqual(status, 400)
        self.assertEqual(body["field"], "form")

    def test_duplicate_ref_returns_409_with_existing_case_id(self):
        status1, body1 = self._create_valid_case(ref="TXN-DUP-001")
        self.assertEqual(status1, 201)
        status2, body2 = self._create_valid_case(ref="TXN-DUP-001")
        self.assertEqual(status2, 409)
        self.assertEqual(body2["error"], "already_open")
        self.assertEqual(body2["caseId"], body1["caseId"])

    def test_create_rate_limited_after_create_max(self):
        for i in range(self.m.CREATE_MAX):
            status, _ = self._create_valid_case(ref=f"TXN-RL-{i}")
            self.assertEqual(status, 201)
        status, body = self._create_valid_case(ref="TXN-RL-OVERFLOW")
        self.assertEqual(status, 429)
        self.assertEqual(body["error"], "rate_limited")

    def test_status_endpoint_returns_created_case(self):
        _, created = self._create_valid_case(ref="TXN-STATUS-001")
        status, body = http_json("GET", f"{self.srv.base_url}/api/itiraz/status/{created['caseId']}")
        self.assertEqual(status, 200)
        self.assertEqual(body["caseId"], created["caseId"])

    def test_status_endpoint_404_for_unknown_case(self):
        status, body = http_json("GET", f"{self.srv.base_url}/api/itiraz/status/UNKNOWN-CASE")
        self.assertEqual(status, 404)

    def test_advance_increments_stage_up_to_closed(self):
        _, created = self._create_valid_case(ref="TXN-ADV-001")
        case_id = created["caseId"]
        for expected_stage in (2, 3, 4):
            status, body = http_json("POST", f"{self.srv.base_url}/api/itiraz/{case_id}/advance", {})
            self.assertEqual(status, 200)
            self.assertEqual(body["stage"], expected_stage)
        # Kapalı aşamadan (4) sonra tekrar ilerletmeye çalışmak aşamayı değiştirmemeli.
        status, body = http_json("POST", f"{self.srv.base_url}/api/itiraz/{case_id}/advance", {})
        self.assertEqual(body["stage"], self.m.CLOSED_STAGE)

    def test_create_rejects_disallowed_file_extension(self):
        fields = {
            "Reason": "gecerli sebep", "TxnType": "x", "Ref": "TXN-BADEXT",
            "Merchant": "M", "Amount": "10",
            "Note": "yeterince uzun bir aciklama metni burada olmali evet",
            "Phone": "5551234567", "Email": "",
        }
        status, body = http_multipart_post(
            f"{self.srv.base_url}/api/itiraz/create", fields,
            files=[("Evidence", "malware.exe", "application/octet-stream", b"MZ")])
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
