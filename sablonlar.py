# -*- coding: utf-8 -*-
"""
Her sınıf için sabit cevap şablonları.
Model sınıflandırır, buradan ilgili metin seçilir (generation YOK).
Her cevap, itiraz sayfasına yönlendiren bir bilgilendirme cümlesiyle biter.
"""

ITIRAZ_LINK = "https://www.mokaunited.com/itiraz"

# yönlendirme cümlesi — sorgu sayfasına uygun sınıflarda
_YONLENDIRME = (
    f"\n\nİşleminizi doğrulamak ve tanımadığınız bir durumda itiraz sürecini başlatmak için "
    f"{ITIRAZ_LINK} adresindeki İşlem Sorgulama ve İtiraz sayfamızı kullanabilirsiniz."
)

CEVAPLAR = {
    "tanimadigi_islem_kart": (
        "Merhaba,\n\nEkstrenizde tanımadığınız bir işlem gördüğünüzü anlıyoruz. "
        "\"MOKA\" ibaresi, bir üye işyerinde kartınızla yapılan gerçek bir işlemi temsil eder. "
        "İşlemin hangi işyerinde gerçekleştiğini kendiniz sorgulayabilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "abonelik_tekrarlayan": (
        "Merhaba,\n\nKartınızdan düzenli olarak yapıldığını belirttiğiniz çekimle ilgili, "
        "işlemin hangi işyeri/hizmet üzerinden gerçekleştiğini sorgulayarak görebilirsiniz. "
        "Tekrarlayan bir üyelik söz konusuysa iptal ve itiraz talebinizi de buradan iletebilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "iade_gecikmesi": (
        "Merhaba,\n\nİade sürecinizle ilgili yaşadığınız gecikme için üzgünüz. "
        "İşleminizin ve itiraz kaydınızın güncel durumunu sorgulayabilir, gerekirse "
        "talebinizi buradan takip edebilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "urun_hizmet_sorunu": (
        "Merhaba,\n\nÖdemesini yaptığınız ürün/hizmete ilişkin sorun, işlemin gerçekleştiği "
        "üye işyeriyle ilgilidir. İşleminizi sorgulayarak ilgili işyeri bilgisini görebilir ve "
        "itiraz sürecinizi başlatabilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "dolandiricilik_suphesi": (
        "Merhaba,\n\nYaşadığınız durumdan dolayı üzgünüz. Yetkisiz veya dolandırıcılık şüphesi taşıyan "
        "bir işlem söz konusuysa, güvenliğiniz için öncelikle bankanızla iletişime geçerek kartınızı "
        "kullanıma kapatmanızı ve bankanıza harcama itirazı talebinizi iletmenizi öneririz. "
        "Bilginiz dışında yapılan işlemler için savcılığa suç duyurusunda da bulunabilirsiniz. "
        "Talebiniz ayrıca incelenmek üzere ilgili ekibimize iletilecektir."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "cuzdan_hesap_sorunu": (
        "Merhaba,\n\nCüzdan/hesap işlemlerinize ilişkin talebiniz incelenmek üzere ilgili ekibimize "
        "iletilmiştir. Bakiye, hesap veya kart erişiminizle ilgili detaylar için sizinle iletişime geçilecektir. "
        "Kart işlemlerinize dair bir sorunuz olması halinde ise aşağıdaki sayfamızdan işleminizi sorgulayabilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
    "zaten_cozuldu_diger": (
        "Merhaba,\n\nBizimle iletişime geçtiğiniz için teşekkür ederiz. Konunuzun çözüldüğünü görüyoruz. "
        "İleride kartınızla ilgili tanımadığınız bir işlem olursa, işleminizi kendiniz sorgulayabilir ve "
        "gerekirse itiraz sürecini başlatabilirsiniz."
        + _YONLENDIRME +
        "\n\nSaygılarımızla."
    ),
}

if __name__ == "__main__":
    for k, v in CEVAPLAR.items():
        print("="*70); print(k); print("-"*70); print(v); print()
