"""sablonlar.py için birim testleri: her sınıf için sabit cevap şablonlarının
bütünlüğü ve itiraz sayfasına yönlendirme cümlesinin tutarlılığı."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sablonlar  # noqa: E402

EXPECTED_CLASSES = {
    "tanimadigi_islem_kart", "abonelik_tekrarlayan", "iade_gecikmesi",
    "urun_hizmet_sorunu", "dolandiricilik_suphesi", "cuzdan_hesap_sorunu",
    "zaten_cozuldu_diger",
}


class TestCevaplar(unittest.TestCase):
    def test_all_expected_classes_present(self):
        self.assertEqual(set(sablonlar.CEVAPLAR.keys()), EXPECTED_CLASSES)

    def test_every_reply_is_non_empty_string(self):
        for cls, text in sablonlar.CEVAPLAR.items():
            self.assertIsInstance(text, str)
            self.assertGreater(len(text.strip()), 20, msg=f"{cls} çok kısa")

    def test_every_reply_contains_redirect_link(self):
        for cls, text in sablonlar.CEVAPLAR.items():
            self.assertIn(sablonlar.ITIRAZ_LINK, text, msg=f"{cls} yönlendirme linki içermiyor")

    def test_itiraz_link_is_https(self):
        self.assertTrue(sablonlar.ITIRAZ_LINK.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
