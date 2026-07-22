"""Moka Müşteri Zeka Motoru (Moko_United/sikayetvar/analysis.py) için birim testleri.

Bu modül tamamen deterministik/stdlib-only olduğu için (yalnızca opsiyonel LLM
katmanı ağ çağrısı yapar) en yüksek test-değerine sahip dosyadır. Kaynak dosyaya
hiçbir değişiklik yapılmaz; yalnızca importlib ile yüklenip davranışı doğrulanır.
"""
import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from helpers import load_module, MOKO_UNITED  # noqa: E402

analysis = load_module("sikayetvar_analysis_under_test",
                        os.path.join(MOKO_UNITED, "sikayetvar", "analysis.py"))


def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def make_complaint(id_, title, body, status="yanit-bekliyor", created_at=None,
                    merchant=None, comments=None, supports=0, views=0):
    return {
        "id": id_, "title": title, "body": body, "status": status,
        "createdAt": created_at or iso(datetime.now()),
        "merchant": merchant, "comments": comments or [],
        "supports": supports, "views": views,
    }


class TestTextHelpers(unittest.TestCase):
    def test_tr_lower_handles_turkish_specific_letters(self):
        self.assertEqual(analysis.tr_lower("İSTANBUL"), "istanbul")
        self.assertEqual(analysis.tr_lower("IŞIK"), "ışık")
        self.assertEqual(analysis.tr_lower("ŞÇĞÜÖ"), "şçğüö")

    def test_norm_unescapes_html_entities(self):
        self.assertEqual(analysis.norm("Kar&#231;a &amp; test"), "Karça & test")
        self.assertEqual(analysis.norm(None), "")

    def test_tokens_filters_short_words_and_stopwords(self):
        toks = analysis.tokens("ve bu bir POS cihazım teslim edilmedi")
        self.assertNotIn("ve", toks)
        self.assertNotIn("bu", toks)
        self.assertNotIn("bir", toks)
        self.assertIn("cihazım", toks)
        self.assertIn("teslim", toks)
        self.assertIn("edilmedi", toks)


class TestCategorize(unittest.TestCase):
    def test_unauthorized_transaction_keywords(self):
        text = "Kartımdan onayım olmadan bir tahsilat yapılmış, tanımadığım bir işlem."
        self.assertEqual(analysis.categorize(text), "Yetkisiz İşlem")

    def test_refund_keywords(self):
        text = "İade ettiğim ürünün parası kartıma yansımadı, iade edilmedi."
        self.assertEqual(analysis.categorize(text), "Para İadesi")

    def test_falls_back_to_diger_when_no_keyword_matches(self):
        self.assertEqual(analysis.categorize("Merhaba nasılsınız iyi günler"), "Diğer")

    def test_pos_teslimat_keywords(self):
        text = "POS cihazım hâlâ kargo ile teslim edilmedi."
        self.assertEqual(analysis.categorize(text), "POS & Teslimat")


class TestUrgencyScore(unittest.TestCase):
    def test_baseline_score_is_three(self):
        self.assertEqual(analysis.urgency_score("basit bir konu", "detay yok burada", "yanit-bekliyor"), 3)

    def test_unauthorized_and_day_pattern_increase_urgency(self):
        score = analysis.urgency_score(
            "Yetkisiz işlem", "10 gündür bu tanımadığım işlemi bekliyorum", "yanit-bekliyor")
        # taban 3 + "yetkisiz"(3) + "tanımadığım"(3) + "gündür"(2) + "\d+ gün" bonus(2) + "iade" olmadan
        self.assertGreaterEqual(score, 9)
        self.assertLessEqual(score, 10)  # 10'da kırpılır

    def test_resolved_status_lowers_urgency(self):
        open_score = analysis.urgency_score("Acil bir konu", "mağdur oldum", "yanit-bekliyor")
        closed_score = analysis.urgency_score("Acil bir konu", "mağdur oldum", "cozuldu")
        self.assertEqual(closed_score, open_score - 2)

    def test_score_is_clamped_between_1_and_10(self):
        self.assertGreaterEqual(analysis.urgency_score("", "", "cozuldu"), 1)
        long_urgent = " ".join(analysis.URGENCY_SIGNALS.keys())
        self.assertLessEqual(analysis.urgency_score(long_urgent, long_urgent, "yanit-bekliyor"), 10)


class TestSentiment(unittest.TestCase):
    def test_neutral_when_no_lexicon_hits(self):
        label, net = analysis.sentiment("Bugün hava çok güzel")
        self.assertEqual(label, "Nötr")
        self.assertEqual(net, 0)

    def test_negative_words_push_to_ofkeli_or_olumsuz(self):
        label, net = analysis.sentiment("Bu rezalet bir durum, mağdur oldum, berbat")
        self.assertEqual(label, "Öfkeli")
        self.assertLess(net, -1)

    def test_positive_words_yield_olumlu(self):
        label, net = analysis.sentiment("Teşekkür ederiz, sorun hızlı çözüldü, çok yardımcı oldular")
        self.assertEqual(label, "Olumlu")
        self.assertGreater(net, 0)


class TestSegmentOf(unittest.TestCase):
    def test_esnaf_isletme_keywords(self):
        text = "İşyerimde POS cihazı ile müşterilerime tahsilat yapamıyorum"
        self.assertEqual(analysis.segment_of(text), "Esnaf / İşletme")

    def test_defaults_to_bireysel_kullanici(self):
        self.assertEqual(analysis.segment_of("herhangi bir metin"), "Bireysel Kullanıcı")


class TestClustering(unittest.TestCase):
    def test_find_clusters_groups_similar_complaints(self):
        complaints = [
            {"title": "POS cihazım teslim edilmedi", "body": "POS cihazım hala kargo ile teslim edilmedi bekliyorum"},
            {"title": "POS cihazım hala gelmedi", "body": "POS cihazım kargoda teslim edilmedi çok bekledim"},
            {"title": "Tamamen alakasız bir konu", "body": "Uygulama şifremi unuttum giriş yapamıyorum"},
        ]
        clusters = analysis.find_clusters(complaints, threshold=0.15)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 2)

    def test_no_clusters_when_all_distinct(self):
        complaints = [
            {"title": "Konu A tamamen farklı", "body": "Bambaşka bir içerik burada"},
            {"title": "Konu B alakasız", "body": "Hiç ilgisi olmayan başka bir metin"},
        ]
        self.assertEqual(analysis.find_clusters(complaints), [])


class TestFraudRingDetection(unittest.TestCase):
    def _enriched(self, merchant, hours_ago_list, cat="Yetkisiz İşlem"):
        now = datetime.now()
        out = []
        for i, h in enumerate(hours_ago_list):
            dt = now - timedelta(hours=h)
            out.append({"id": i + 1, "title": f"Şikayet {i}", "merchant": merchant,
                        "status": "yanit-bekliyor", "_cat": cat, "_urg": 8, "_dt": dt})
        return out

    def test_detects_ring_with_three_within_window(self):
        enriched = self._enriched("Hızlı Ödeme Bayii", [1, 10, 20])
        rings = analysis.detect_fraud_rings(enriched, window_hours=48, min_count=3)
        self.assertEqual(len(rings), 1)
        self.assertEqual(rings[0]["merchant"], "Hızlı Ödeme Bayii")
        self.assertEqual(rings[0]["count"], 3)

    def test_no_ring_when_below_min_count(self):
        enriched = self._enriched("Tekil İşyeri", [1, 10])
        self.assertEqual(analysis.detect_fraud_rings(enriched, min_count=3), [])

    def test_no_ring_when_outside_time_window(self):
        enriched = self._enriched("Yavaş Yayılan İşyeri", [1, 60, 120])
        self.assertEqual(analysis.detect_fraud_rings(enriched, window_hours=48, min_count=3), [])

    def test_ignores_non_matching_category(self):
        enriched = self._enriched("Başka Kategori", [1, 2, 3], cat="Para İadesi")
        self.assertEqual(analysis.detect_fraud_rings(enriched), [])

    def test_ignores_complaints_without_merchant(self):
        now = datetime.now()
        enriched = [{"id": i, "title": "t", "merchant": None, "status": "yanit-bekliyor",
                    "_cat": "Yetkisiz İşlem", "_urg": 8, "_dt": now} for i in range(3)]
        self.assertEqual(analysis.detect_fraud_rings(enriched), [])


class TestHourlyDistribution(unittest.TestCase):
    def test_empty_input_returns_zeroed_structure(self):
        result = analysis.hourly_distribution([])
        self.assertEqual(result["buckets"], [0] * 24)
        self.assertEqual(result["peak_hour"], 0)
        self.assertEqual(result["business_hours_pct"], 0)

    def test_peak_hour_and_business_hours_pct(self):
        base = datetime(2026, 1, 5, 0, 0, 0)  # sabit referans, gün kayması riskini önler
        entries = []
        for _ in range(3):
            entries.append({"_dt": base.replace(hour=10)})  # mesai içi, tekrar eden tepe saat
        entries.append({"_dt": base.replace(hour=23)})       # mesai dışı
        result = analysis.hourly_distribution(entries)
        self.assertEqual(result["peak_hour"], 10)
        self.assertEqual(result["peak_count"], 3)
        self.assertEqual(result["business_hours_pct"], 75)
        self.assertEqual(result["off_hours_pct"], 25)


class TestMerchantRiskRanking(unittest.TestCase):
    def test_ranks_by_count_times_avg_urgency(self):
        enriched = [
            {"merchant": "A İşyeri", "status": "yanit-bekliyor", "_urg": 10},
            {"merchant": "A İşyeri", "status": "yanit-bekliyor", "_urg": 6},
            {"merchant": "B İşyeri", "status": "cozuldu", "_urg": 9},
        ]
        rows = analysis.merchant_risk_ranking(enriched)
        self.assertEqual(rows[0]["merchant"], "A İşyeri")
        self.assertEqual(rows[0]["count"], 2)
        self.assertEqual(rows[0]["avg_urgency"], 8.0)
        self.assertEqual(rows[0]["risk_score"], 16.0)
        self.assertEqual(rows[1]["pending"], 0)  # B çözülmüş, bekleyen yok

    def test_is_ring_flag_uses_lowercased_merchant_key(self):
        enriched = [{"merchant": "Hızlı Ödeme Bayii", "status": "yanit-bekliyor", "_urg": 5}]
        rows = analysis.merchant_risk_ranking(enriched, ring_keys={analysis.tr_lower("Hızlı Ödeme Bayii")})
        self.assertTrue(rows[0]["is_ring"])

    def test_excludes_complaints_without_merchant(self):
        enriched = [{"merchant": None, "status": "yanit-bekliyor", "_urg": 5},
                    {"merchant": "", "status": "yanit-bekliyor", "_urg": 5}]
        self.assertEqual(analysis.merchant_risk_ranking(enriched), [])


class TestRouteToTeams(unittest.TestCase):
    def test_groups_by_team_and_ranks_by_pending_times_urgency(self):
        enriched = [
            {"_cat": "Yetkisiz İşlem", "status": "yanit-bekliyor", "_urg": 9, "title": "a"},
            {"_cat": "Yetkisiz İşlem", "status": "yanit-bekliyor", "_urg": 7, "title": "b"},
            {"_cat": "Para İadesi", "status": "cozuldu", "_urg": 2, "title": "c"},
        ]
        rows = analysis.route_to_teams(enriched)
        self.assertEqual(rows[0]["team"], "Güvenlik & Fraud Ekibi")
        self.assertEqual(rows[0]["count"], 2)
        self.assertEqual(rows[0]["pending"], 2)
        self.assertEqual(rows[0]["top_category"], "Yetkisiz İşlem")

    def test_unknown_category_routes_to_diger_team(self):
        enriched = [{"_cat": "Bilinmeyen Kategori", "status": "yanit-bekliyor", "_urg": 5, "title": "x"}]
        rows = analysis.route_to_teams(enriched)
        self.assertEqual(rows[0]["team"], analysis.TEAM_ROUTING["Diğer"])


class TestAnalyzeEndToEnd(unittest.TestCase):
    def test_empty_complaints_returns_zeroed_shape(self):
        result = analysis.analyze({"complaints": []})
        self.assertEqual(result["kpis"], {})
        self.assertEqual(result["fraud_rings"], [])
        self.assertEqual(result["hourly"]["buckets"], [0] * 24)

    def test_kpis_and_resolution_rate(self):
        now = datetime.now()
        complaints = [
            make_complaint(1, "Kartımdan onayım olmadan tahsilat", "yetkisiz bir işlem oldu",
                            status="cozuldu", created_at=iso(now - timedelta(days=1))),
            make_complaint(2, "Para iadem yansımadı", "10 gündür iade bekliyorum",
                            status="yanit-bekliyor", created_at=iso(now)),
        ]
        result = analysis.analyze({"complaints": complaints}, now=now)
        self.assertEqual(result["kpis"]["total"], 2)
        self.assertEqual(result["kpis"]["solved"], 1)
        self.assertEqual(result["kpis"]["pending"], 1)
        self.assertEqual(result["kpis"]["resolution_rate"], 50)
        self.assertIn(result["kpis"]["trust_score"], range(0, 101))

    def test_avg_response_hours_uses_first_brand_comment(self):
        now = datetime.now()
        created = now - timedelta(hours=5)
        complaint = make_complaint(
            1, "Konu", "İçerik burada yeterince uzun bir açıklama metni",
            created_at=iso(created),
            comments=[{"isBrand": True, "createdAt": iso(created + timedelta(hours=2))}],
        )
        result = analysis.analyze({"complaints": [complaint]}, now=now)
        self.assertEqual(result["kpis"]["avg_response_hours"], 2.0)

    def test_recommendations_reference_known_categories(self):
        complaints = [make_complaint(1, "Kartımdan onayım olmadan tahsilat", "yetkisiz işlem oldu")]
        result = analysis.analyze({"complaints": complaints})
        self.assertTrue(result["recommendations"])
        for rec in result["recommendations"]:
            self.assertIn(rec["category"], analysis.RECOMMENDATIONS)

    def test_categories_share_sums_do_not_exceed_100(self):
        complaints = [
            make_complaint(1, "Yetkisiz işlem oldu", "onayım olmadan tahsilat yapıldı"),
            make_complaint(2, "Para iadem gecikti", "iade edilmedi hala"),
            make_complaint(3, "Başka konu", "tamamen alakasız bir mesaj"),
        ]
        result = analysis.analyze({"complaints": complaints})
        self.assertLessEqual(sum(c["share"] for c in result["categories"]), 100)


class TestTemplateSummary(unittest.TestCase):
    def test_falls_back_to_deterministic_template(self):
        ins = {"kpis": {"total": 5, "resolution_rate": 60},
               "critical_issues": [{"issue": "Yetkisiz İşlem"}],
               "emerging": [{"name": "Para İadesi", "pct": 20}]}
        text = analysis._template_summary(ins)
        self.assertIn("5", text)
        self.assertIn("Yetkisiz İşlem", text)

    def test_llm_summary_falls_back_when_ollama_unreachable(self):
        # localhost:11434 test ortamında büyük ihtimalle kapalı; kısa timeout ile
        # gerçek ağ çağrısı denenir ama hata durumunda şablon özete düşülmelidir.
        ins = {"kpis": {"total": 1, "resolution_rate": 100},
               "critical_issues": [], "emerging": []}
        result = analysis.llm_summary(ins, timeout=1)
        self.assertIn("source", result)
        self.assertIn("text", result)


if __name__ == "__main__":
    unittest.main()
