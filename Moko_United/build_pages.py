#!/usr/bin/env python3
"""Moka United klonu için alt sayfa üreticisi.
Ortak iskelet (head + mount noktaları) + sayfaya özel <main> içeriği birleştirir.
İçerik metinleri özgün/parafraze — telif içerik kopyalanmamıştır."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- Çizgi ikon seti (currentColor ile temaya uyum sağlar) ----------
ICONS = {
  'global': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 2.5 15.3 0 18M12 3c-2.5 2.7-2.5 15.3 0 18"/></svg>',
  'exchange': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13l-3-3M20 16H7l3 3"/></svg>',
  'people': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><path d="M16 5.2A3.2 3.2 0 0 1 16 11m5 9c0-2.6-1.5-4.6-3.8-5.2"/></svg>',
  'money': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="6" width="19" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.6"/><path d="M6 12h.01M18 12h.01"/></svg>',
  'shield': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.4-3 8-7 10-4-2-7-5.6-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg>',
  'card': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 9.5h19M6 15h4"/></svg>',
  'wallet': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h13a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H6a2 2 0 0 1-2-2z"/><path d="M4 7V6a2 2 0 0 1 2-2h9"/><circle cx="16.5" cy="13" r="1.3"/></svg>',
  'transfer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h13l-3-3M21 17H8l3 3"/><circle cx="12" cy="12" r="9" opacity=".25"/></svg>',
  'safe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="11" cy="12" r="3.2"/><path d="M11 9v-.5M16.5 8v8"/></svg>',
  'kiosk': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="3" width="12" height="15" rx="2"/><path d="M8.5 6h7M8.5 9h7M10 20h4"/></svg>',
  'bolt': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h6l-1 8 9-12h-6z"/></svg>',
  'chart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V4M4 20h16M8 16v-4M12 16V8M16 16v-7"/></svg>',
  'link': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a4 4 0 0 0 5.6 0l2.4-2.4a4 4 0 0 0-5.6-5.6L11 6.4"/><path d="M14 11a4 4 0 0 0-5.6 0L6 13.4a4 4 0 0 0 5.6 5.6L13 17.6"/></svg>',
  'code': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13 5l-2 14"/></svg>',
  'gift': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v8h14v-8M12 8v12"/><path d="M12 8S10.5 4 8.5 4 6 6.5 12 8zM12 8s1.5-4 3.5-4S18 6.5 12 8z"/></svg>',
  'building': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1M10 21v-3h4v3"/></svg>',
  'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>',
  'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 6.5"/></svg>',
  'plane': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 4.5c.8-.8 1.7-.5 2 .5l1.5 5.5 5.5 1.5c1 .3 1.3 1.2.5 2l-3 1.5-1 4-1.5 1.5-1.5-4.5-3 3v2l-1.5-1-.5-2-2-.5-1-1.5h2l3-3-4.5-1.5L7 15.5l1.5-1 4-1z"/></svg>',
  'heart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.3-9.2-8.4C1.3 9 2.4 5.8 5.5 5c2-.5 3.7.6 4.5 2 .8-1.4 2.5-2.5 4.5-2 3.1.8 4.2 4 2.7 6.6C19 15.7 12 20 12 20z"/></svg>',
  'store': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10v9h16v-9M3 6l1-2h16l1 2-1.5 3.5a2.5 2.5 0 0 1-4.5 0 2.5 2.5 0 0 1-5 0 2.5 2.5 0 0 1-4.5 0z"/></svg>',
  'file': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
}

def icon(name):
    return f'<span class="ic">{ICONS.get(name, ICONS["check"])}</span>'

def shell(title, desc, body_class, active, main_html):
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Moka United</title>
  <meta name="description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Moka United">
  <meta property="og:title" content="{title} | Moka United">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="assets/images/favicon.svg">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css?v=3">
</head>
<body class="{body_class}" data-active="{active}">
  <div class="overlay-loader" id="loader"><div class="spinner"></div></div>
  <div id="header-mount"></div>
  <main>
{main_html}
  </main>
  <div id="cta-mount"></div>
  <div id="footer-mount"></div>
  <script src="assets/js/components.js?v=3"></script>
  <script src="assets/js/main.js?v=3"></script>
  <script src="assets/js/moka-chat-widget.js?v=1"></script>
</body>
</html>
"""

def breadcrumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if href:
            parts.append(f'<a href="{href}">{label}</a>')
        else:
            parts.append(f'<span>{label}</span>')
        if i < len(items) - 1:
            parts.append('<span class="sep">/</span>')
    return '<nav class="breadcrumb">' + ''.join(parts) + '</nav>'

def page_title(t):
    return f'<section class="page-title"><h1 class="multicolors">{t}</h1></section>'

def cards(items, special=False):
    """items: list of (title, href, img_path_or_None)"""
    c = []
    for title, href, img in items:
        cls = 'card-comp special' if special else 'card-comp'
        img_html = f'<img class="card-img" src="{img}" alt="{title.title()}">' if img else ''
        c.append(f'''<div class="{cls} reveal"><a class="card" href="{href}">
          <div class="card-body"><h2 class="card-title">{title}</h2></div>{img_html}</a></div>''')
    return '<section class="landing-grid container"><div class="card-grid">' + ''.join(c) + '</div></section>'

PROD_IMG = {
  'kart-cozumleri.html': 'assets/images/prod-kart.svg',
  'cuzdan-cozumleri.html': 'assets/images/prod-cuzdan.svg',
  'para-transferi.html': 'assets/images/prod-transfer.svg',
  'akilli-kasa.html': 'assets/images/prod-kasa.svg',
  'kiosk.html': 'assets/images/prod-kiosk.svg',
}

def faq(title, qa, visible=5):
    items = []
    for i, (q, a) in enumerate(qa):
        hidden = ' hidden-item' if i >= visible else ''
        active = ' active' if i == 0 else ''
        aps = ''.join(f'<p>{p}</p>' for p in a)
        items.append(f'''<div class="accordion-item{hidden}{active}">
          <button class="accordion-header">{q}<span class="chev">⌄</span></button>
          <div class="accordion-body"><div class="accordion-body-inner">{aps}</div></div></div>''')
    more = ''
    if len(qa) > visible:
        more = '<div class="show-more-wrap"><button class="button button-primary show-more"><span>DAHA FAZLA GÖSTER</span></button></div>'
    return f'''<section class="faq container"><h2>{title}</h2><div class="accordion accordion-wrap">{''.join(items)}</div>{more}</section>'''

def info_boxes(items, cols=3):
    """items: list of (icon_name, h5, paragraph)  — geriye dönük: (h5, paragraph) de kabul edilir"""
    b = []
    for it in items:
        if len(it) == 3:
            ic, h5, p = it
        else:
            h5, p = it; ic = 'check'
        b.append(f'''<div class="info-box reveal"><div class="ib-icon">{icon(ic)}</div>
          <h5>{h5}</h5><p>{p}</p></div>''')
    cls = f'info-grid cols-{cols}'
    return f'<section class="info-boxes container"><div class="{cls}">' + ''.join(b) + '</div></section>'

def split(left_img, title, body, buttons=None, reverse=False, img=None, theme_img=None):
    btns = ''
    if buttons:
        btns = '<div class="col-buttons">' + ''.join(
            f'<a class="button {c}" href="{h}"><span>{t}</span></a>' for t, h, c in buttons) + '</div>'
    src = img or 'assets/images/placeholder.svg'
    img_html = f'<div class="col narrow reveal"><img src="{src}" alt=""></div>'
    body_html = body if body.strip().startswith('<') else f'<h4>{body}</h4>'
    txt = f'<div class="col reveal"><h2>{title}</h2>{body_html}{btns}</div>'
    inner = (img_html + txt) if not reverse else (txt + img_html)
    return f'<section class="split container"><div class="row">{inner}</div></section>'

def bullets(title, intro, items):
    lis = ''.join(f'<li>{icon("check")}<span>{x}</span></li>' for x in items)
    return f'''<section class="split container"><div class="col reveal" style="flex:1 1 100%">
      <h2>{title}</h2><p style="margin:16px 0">{intro}</p><ul class="feature-list">{lis}</ul></div></section>'''

def feature_split(title, intro, items, reverse=False, img=None):
    """Sol/sağ: bir tarafta başlık+madde listesi (ikonlu), diğer tarafta görsel."""
    lis = ''.join(f'<li>{icon("check")}<span>{x}</span></li>' for x in items)
    src = img or 'assets/images/placeholder.svg'
    txt = f'<div class="col reveal"><h2>{title}</h2><p style="margin:14px 0 20px">{intro}</p><ul class="feature-list">{lis}</ul></div>'
    im = f'<div class="col narrow reveal"><img src="{src}" alt=""></div>'
    inner = (txt + im) if not reverse else (im + txt)
    return f'<section class="split container"><div class="row">{inner}</div></section>'

# Ürün sayfaları için sayfa içi (açık zeminli) talep formu bileşeni
def inline_form(heading, sub, extra_field=None):
    ef = ''
    if extra_field:
        ef = f'<div class="form-group full"><input class="form-control" type="text" name="Subject" placeholder="{extra_field}"></div>'
    return f'''<section class="inline-form-section container">
  <div class="inline-form-card reveal">
    <div class="if-head"><h2>{heading}</h2><p>{sub}</p></div>
    <form class="contact-form inline-contact" novalidate>
      <div class="form-fields">
        <div class="form-row">
          <div class="form-group"><input class="form-control only-letter" type="text" name="FullName" placeholder="Ad Soyad" required></div>
          <div class="form-group"><input class="form-control" type="email" name="Email" placeholder="E-Posta" required></div>
        </div>
        <div class="form-row">
          <div class="form-group"><input class="form-control only-number" type="tel" name="Phone" placeholder="Telefon" required></div>
          <div class="form-group"><input class="form-control" type="text" name="Company" placeholder="Şirket Adı"></div>
        </div>
        {ef}
        <label class="form-check dark-check"><input type="checkbox" required> Kişisel verilerimin <a href="kvkk-aydinlatma-metni.html">Aydınlatma Metni</a>'nde belirtilen amaçlarla işleneceğini okudum, anladım.</label>
        <div style="text-align:right"><button type="submit" class="button button-primary"><span>GÖNDER</span></button></div>
      </div>
      <div class="form-success">
        <div class="ok-badge">{icon('check')}</div>
        <h3>MESAJINIZ BAŞARIYLA GÖNDERİLMİŞTİR.</h3>
        <p>Ekibimiz, ihtiyacınızla ilgili olarak 48 saat içinde e-posta veya telefon yoluyla dönüş yapacaktır.</p>
      </div>
    </form>
  </div>
</section>'''

# Ana sayfadaki sayaç bloğunun yeniden kullanılabilir hali (hikayemiz vb.)
def numbers_block(heading, paragraphs):
    ps = ''.join(f'<p>{p}</p>' for p in paragraphs)
    return f'''<section class="stats container"><div class="row">
    <div class="stats-boxes reveal">
      <div class="count-box"><div class="icon">{icon('global')}</div><span class="number" data-target="6">0</span><p>Ülke</p></div>
      <div class="count-box"><div class="icon">{icon('exchange')}</div><span class="number" data-target="120" data-suffix="M+">0</span><p>İşlem Sayısı</p></div>
      <div class="count-box"><div class="icon">{icon('people')}</div><span class="number" data-target="250" data-suffix="+">0</span><p>Çalışan</p></div>
      <div class="count-box"><div class="icon">{icon('money')}</div><span class="number" data-target="10">0</span><p>Milyar USD İşlem Hacmi</p></div>
    </div>
    <div class="stats-text reveal"><h2>{heading}</h2>{ps}</div>
  </div></section>'''

def strip_section(title, body, cls='strip-black'):
    return f'''<section class="strip {cls} container reveal" style="text-align:center">
      <h2>{title}</h2><p style="max-width:760px;margin:18px auto 0">{body}</p></section>'''

# Zaman çizelgesi bileşeni
def timeline(title, items):
    """items: list of (year, text)"""
    rows = ''.join(f'''<div class="tl-item reveal"><div class="tl-year">{y}</div>
      <div class="tl-dot"></div><div class="tl-body"><p>{t}</p></div></div>''' for y, t in items)
    return f'<section class="timeline-section container"><h2 class="text-center">{title}</h2><div class="timeline">{rows}</div></section>'

PAGES = {}

# ---------- LANDING GRID SAYFALARI ----------
PAGES['hakkimizda.html'] = shell(
  'Hakkımızda', 'Moka United hakkında: hikayemiz, kurumsal yönetim, kariyer ve iştirakler.',
  '', 'hakkimizda',
  breadcrumb([('Moka United','index.html'),('Hakkımızda',None)]) + page_title('HAKKIMIZDA') +
  cards([('HİKAYEMİZ','hikayemiz.html',None),('KURUMSAL YÖNETİM','kurumsal-yonetim.html',None),
         ("MOKA UNITED'TA KARİYER",'kariyer.html',None),('İŞTİRAKLER','istirakler.html',None)]))

PAGES['urunler.html'] = shell(
  'Ürünler', 'Kart çözümleri, cüzdan çözümleri, para transferi, akıllı kasa ve kiosk çözümleri.',
  '', 'urunler',
  breadcrumb([('Moka United','index.html'),('Ürünler',None)]) + page_title('ÜRÜNLER') +
  cards([('KART ÇÖZÜMLERİ','kart-cozumleri.html',PROD_IMG['kart-cozumleri.html']),
         ('CÜZDAN ÇÖZÜMLERİ','cuzdan-cozumleri.html',PROD_IMG['cuzdan-cozumleri.html']),
         ('PARA TRANSFERİ','para-transferi.html',PROD_IMG['para-transferi.html']),
         ('AKILLI KASA','akilli-kasa.html',PROD_IMG['akilli-kasa.html']),
         ('KİOSK','kiosk.html',PROD_IMG['kiosk.html'])]))

PAGES['pos-cozumleri.html'] = shell(
  'POS Çözümleri', 'Sanal POS, fiziki POS ve linkle tahsilat çözümleri.',
  '', 'pos',
  breadcrumb([('Moka United','index.html'),('POS Çözümleri',None)]) + page_title('POS ÇÖZÜMLERİ') +
  cards([('SANAL POS','sanal-pos.html',None),('FİZİKİ POS','fiziki-pos.html',None),
         ('LİNKLE TAHSİLAT','linkle-tahsilat.html',None)]))

# ---------- İÇERİK + SSS SAYFALARI ----------
def content_faq_page(fname, title, active, lead_title, lead_p, boxes, adv_title, adv_intro, adv_items,
                     caps_title, caps_items, who_title, who_items, faq_title, qa):
    caps_lis = ''.join(f'<li>{icon("bolt")}<span>{x}</span></li>' for x in caps_items)
    caps = f'''<section class="split container caps-section"><div class="col reveal" style="flex:1 1 100%">
      <h2>{caps_title}</h2><ul class="feature-list caps-grid">{caps_lis}</ul></div></section>'''
    body = (breadcrumb([('Moka United','index.html'),('POS Çözümleri','pos-cozumleri.html'),(title.title(),None)]) +
            page_title(title) +
            split(None, lead_title, lead_p, reverse=True) +
            info_boxes(boxes) +
            feature_split(adv_title, adv_intro, adv_items) +
            caps +
            feature_split(who_title, 'Aşağıdaki işletme tipleri için idealdir:', who_items, reverse=True) +
            inline_form('POS ÇÖZÜMÜNÜZ İÇİN TEKLİF ALIN', 'Formu doldurun; komisyon ve kurulum detayları için ekibimiz sizi arasın.') +
            faq(faq_title, qa))
    return shell(title, lead_p[:150], 'product-detail', active, body)

PAGES['sanal-pos.html'] = content_faq_page(
  'sanal-pos.html', 'SANAL POS', 'pos',
  'Online Ödeme Almanın En Kolay Yolu: Moka United Sanal POS',
  'Sanal POS ile e-ticaret sitenizden ve mobil uygulamanızdan hızlı, güvenli ve kesintisiz ödeme alın. Siz işinize odaklanın, ödeme almayı bize bırakın.',
  [('Sanal POS Nedir?','İşletmelerin internet üzerinden banka ve kredi kartıyla ödeme almasını sağlayan dijital ödeme sistemidir. Bir web sitesi veya mobil uygulamaya entegre çalışır.'),
   ('Sanal POS Nasıl Alınır?','Bir banka veya ödeme kuruluşuna başvurmanız yeterlidir. Başvuru formunu doldurup işletme bilgilerinizi ilettiğinizde süreç başlar.'),
   ('Moka United Sanal POS Nedir?','Tek entegrasyonla birden fazla bankadan ödeme almanızı sağlayan gelişmiş bir altyapıdır. E-ticaret ve online satış işletmeleri için hızlı ve güvenlidir.')],
  'Moka United Sanal POS Avantajları', 'Sanal POS altyapımızın işletmenize sunduğu başlıca avantajlar:',
  ['Tek entegrasyonla birden fazla bankadan ödeme alma','Yüksek onay oranıyla sepet terkini azaltma',
   'Gelişmiş raporlama paneliyle tüm hareketleri tek yerden takip','Hızlı kurulum ve kolay entegrasyon',
   'Çok katmanlı güvenli ödeme altyapısı','Küçük işletmeden büyük markaya ölçeklenebilir yapı'],
  'Sanal POS ile Neler Yapabilirsiniz?',
  ['Peşin ve taksitli satış','Dövizli ödeme alma','3D Secure ve Non-3D işlemler','Banka kampanya entegrasyonları',
   'Kart saklama ve tekrarlı (abonelik) ödeme','Tek tıkla ödeme ve hızlı checkout'],
  'Kimler Sanal POS Kullanabilir?', ['E-ticaret siteleri','Mobil uygulamalar','Dijital platformlar','Pazaryerleri','Abonelik ve B2C satış yapan işletmeler'],
  'Sanal POS Hakkında Sıkça Sorulan Sorular',
  [('Sanal POS güvenli midir?',['Evet. 3D Secure doğrulaması, şifreleme teknolojileri ve gerçek zamanlı fraud izleme ile korunur.']),
   ('Komisyon oranları nasıl belirlenir?',['Satış hacmi, sektör, taksit seçenekleri ve anlaşma yapısına göre belirlenir.']),
   ('Taksitli satış yapabilir miyim?',['Evet. Banka veya ödeme sağlayıcıyla taksit anlaşması yapıldığında taksitli satış mümkündür.']),
   ('Başvurum ne kadar sürede sonuçlanır?',['Genellikle birkaç iş günü içinde sonuçlanır.']),
   ('Yurt dışından ödeme alabilir miyim?',['Evet. Dövizli ödeme özelliğiyle farklı para birimlerinde işlem yapabilirsiniz.']),
   ('Hangi kartları destekler?',['Visa, Mastercard ve Troy başta olmak üzere yaygın kart şemalarını destekler.']),
   ('3D Secure nedir?',['Online ödemede kart sahibinin kimliğini doğrulayan ek güvenlik adımıdır.']),
   ('Birden fazla banka ile çalışabilir miyim?',['Evet. Tek entegrasyonla birden fazla bankanın sanal POS’unu aynı anda kullanabilirsiniz.']),
   ('Raporlama paneli sunuyor musunuz?',['Evet. Tüm işlemleri, iadeleri ve mutabakatı tek panelden takip edebilirsiniz.']),
   ('Entegrasyon için yazılım bilgisi şart mı?',['Hazır eklentiler ve dokümante API’lerimizle entegrasyon oldukça kolaydır; teknik ekibimiz destek verir.'])])

PAGES['fiziki-pos.html'] = content_faq_page(
  'fiziki-pos.html', 'FİZİKİ POS', 'pos',
  'Moka United Fiziki POS ile İşletmenizi Güçlendirin',
  'Mağaza içi satışlarınızda hızlı, güvenli ve kesintisiz tahsilat için fiziki POS cihazlarımızla tanışın.',
  [('Fiziki POS Nedir?','Mağaza, restoran ve fiziksel satış noktalarında kart ile ödeme almayı sağlayan cihazdır.'),
   ('Moka United Fiziki POS Avantajları','Tek panelde raporlama, hızlı hesaba geçiş ve tüm bankalarla uyumlu çalışma sunar.'),
   ('Kimler Fiziki POS Kullanabilir?','Perakende, restoran, kafe ve hizmet sektöründeki tüm işletmeler kullanabilir.')],
  'Moka United Fiziki POS Avantajları','Fiziki POS çözümümüzün başlıca avantajları:',
  ['Hızlı ve güvenli mağaza içi tahsilat','Tüm bankalarla uyumlu çalışma','Tek panelde merkezi raporlama',
   'Temassız ve taksitli ödeme desteği','7/24 teknik destek'],
  'Fiziki POS ile Neler Yapabilirsiniz?',
  ['Peşin, taksitli ve temassız ödeme alma','Tüm bankalarla tek cihazda çalışma','Anlık satış ve gün sonu raporları',
   'Uç birim üzerinden iade işlemleri','Kampanya ve puan entegrasyonları'],
  'Kimler Fiziki POS Kullanabilir?', ['Perakende mağazaları','Restoran ve kafeler','Hizmet işletmeleri','Zincir mağazalar'],
  'Fiziki POS Hakkında Sıkça Sorulan Sorular',
  [('POS cihazı başvurusu nasıl yapılır?',['Başvuru formunu doldurarak veya satış ekibimizle iletişime geçerek başvurabilirsiniz.']),
   ('Cihaz ne kadar sürede teslim edilir?',['Başvurunuz onaylandıktan sonra kısa sürede kurulum yapılır.']),
   ('Taksitli satış destekleniyor mu?',['Evet, banka anlaşmalarıyla taksitli satış yapılabilir.']),
   ('Temassız ödeme var mı?',['Evet, tüm cihazlarımız temassız ödemeyi destekler.']),
   ('Komisyon oranları nasıl belirlenir?',['İşlem hacminiz, sektörünüz ve taksit seçeneklerine göre size özel belirlenir.']),
   ('Birden fazla banka ile çalışabilir miyim?',['Evet, tek cihazda birden çok bankanın POS uygulamasını kullanabilirsiniz.']),
   ('Cihaz arızasında ne oluyor?',['7/24 teknik destek ve hızlı cihaz değişimi ile kesintisiz hizmet sağlanır.']),
   ('İade işlemi nasıl yapılır?',['İade işlemlerini doğrudan cihaz üzerinden veya yönetim panelinden gerçekleştirebilirsiniz.']),
   ('Gün sonu mutabakatı nasıl takip edilir?',['Tüm işlemler, mutabakat ve hesaba geçiş bilgileri merkezi raporlama panelinde tek yerden izlenir.']),
   ('Yurt dışı kartları kabul ediyor mu?',['Evet, cihazlarımız Visa ve Mastercard başta olmak üzere yurt dışı kartlarını kabul eder.'])])

PAGES['linkle-tahsilat.html'] = content_faq_page(
  'linkle-tahsilat.html', 'LİNKLE TAHSİLAT', 'pos',
  'Ödeme Almada Yeni Dönem: Moka United Linkle Tahsilat',
  'Web siteniz olmadan, tek bir ödeme linkiyle müşterilerinizden güvenle tahsilat yapın.',
  [('Linkle Tahsilat Nedir?','Oluşturduğunuz ödeme linkini müşterinize göndererek kart ile tahsilat yapmanızı sağlayan çözümdür.'),
   ('Moka United Linkle Tahsilat Nedir?','Panelden saniyeler içinde link üretip WhatsApp, SMS veya e-posta ile paylaşabileceğiniz altyapıdır.'),
   ('Linkle Tahsilat Avantajları','Web sitesi gerektirmez, hızlı kurulur ve her kanaldan paylaşılabilir.')],
  'Moka United Link ile Tahsilat Avantajları','Linkle tahsilatın başlıca avantajları:',
  ['Web sitesi gerektirmeden ödeme alma','Saniyeler içinde link oluşturma','WhatsApp, SMS ve e-posta ile paylaşım',
   'Taksitli ve tek çekim seçenekleri','Güvenli 3D Secure ödeme'],
  'Linkle Tahsilat ile Neler Yapabilirsiniz?',
  ['Tek linkle peşin veya taksitli tahsilat','Her kanaldan (WhatsApp/SMS/e-posta/sosyal medya) paylaşım',
   'Tutar ve açıklama içeren kişiselleştirilmiş linkler','Ödeme durumunu anlık takip','Tekrar kullanılabilir veya tek seferlik linkler'],
  'Linkle Tahsilat Kimler İçin Uygun?', ['Sosyal medyadan satış yapanlar','Serbest çalışanlar','Küçük işletmeler','Hizmet sağlayıcılar'],
  'Linkle Tahsilat Hakkında Sıkça Sorulan Sorular',
  [('Link nasıl oluşturulur?',['Panele giriş yapıp tutar ve açıklama girerek saniyeler içinde link üretirsiniz.']),
   ('Linki nasıl paylaşırım?',['WhatsApp, SMS, e-posta veya sosyal medya üzerinden paylaşabilirsiniz.']),
   ('Ödeme güvenli mi?',['Evet, tüm ödemeler 3D Secure ve şifreleme ile korunur.']),
   ('Taksit yapılabilir mi?',['Evet, banka anlaşmalarıyla taksit seçeneği sunulabilir.']),
   ('Web sitem yok, kullanabilir miyim?',['Evet, linkle tahsilatın en büyük avantajı web sitesi gerektirmemesidir.']),
   ('Ödeme durumunu nasıl görürüm?',['Panel üzerinden her linkin ödenip ödenmediğini anlık takip edebilirsiniz.']),
   ('Komisyon oranları nedir?',['Komisyon; işlem hacminiz, sektörünüz ve taksit tercihlerinize göre size özel belirlenir.']),
   ('Linkin geçerlilik süresi var mı?',['Evet, oluşturduğunuz linke geçerlilik süresi tanımlayabilir veya tek kullanımlık link üretebilirsiniz.']),
   ('Yurt dışı kartlarından tahsilat yapabilir miyim?',['Evet, dövizli ödeme ve yurt dışı kart kabulü desteklenmektedir.']),
   ('Para hesabıma ne zaman geçer?',['Anlaşma koşullarınıza göre tahsilatlar belirlenen valörde hesabınıza aktarılır.'])])

# ---------- ÜRÜN DETAY SAYFALARI ----------
def ribbon_hero(title, tagline, intro=None, img=None):
    src = img or 'assets/images/placeholder.svg'
    intro_html = f'<p class="ribbon-intro">{intro}</p>' if intro else ''
    return f'''<section class="ribbon-hero container">
      <div class="ribbon-hero-inner">
        <div class="ribbon-hero-text reveal">
          <h1 class="multicolors">{title}</h1>
          <p class="ribbon-tagline">{tagline}</p>
          {intro_html}
        </div>
        <div class="ribbon-hero-img reveal"><img src="{src}" alt="{title}"></div>
      </div>
      <div class="band"></div>
    </section>'''

def product_page(title, active, theme, hero, sections, desc):
    body = [breadcrumb([('Moka United','index.html'),('Ürünler','urunler.html'),(title.title(),None)]),
            hero] + sections
    return shell(title, desc[:150], f'product-detail {theme}', active, ''.join(body))

PROD_ILLUS = {
  'kart': 'assets/images/prod-kart.svg', 'cuzdan': 'assets/images/prod-cuzdan.svg',
  'transfer': 'assets/images/prod-transfer.svg', 'kasa': 'assets/images/prod-kasa.svg',
  'kiosk': 'assets/images/prod-kiosk.svg',
}
# Temaya göre çeşitli illüstrasyonlar (tekrar eden placeholder yerine)
ILLUS = {
  'security': 'assets/images/illus-security.svg', 'api': 'assets/images/illus-api.svg',
  'city': 'assets/images/illus-city.svg', 'growth': 'assets/images/illus-growth.svg',
  'team': 'assets/images/illus-team.svg',
}

# --- KART ÇÖZÜMLERİ ---
PAGES['kart-cozumleri.html'] = product_page(
  'KART ÇÖZÜMLERİ', 'urunler', 'theme-blue',
  ribbon_hero('KART ÇÖZÜMLERİ', 'Kart Çözümlerimizle Finansal Özgürlüğün Anahtarı Cebinizde!',
              'Zengin özelliklere sahip kart API’lerimizle markanıza özel sanal ve fiziksel kartlar oluşturun, ödeme deneyimini uçtan uca yönetin.', PROD_ILLUS['kart']),
  [ inline_form('KENDİ KART EKOSİSTEMİNİZİ YARATIN', 'Markanıza özel kart programı için formu doldurun; ekibimiz sizi kısa sürede arasın.', extra_field='Konu / İlgi Alanı'),
    split(None, 'YALNIZCA BİRKAÇ GÜNDE MASTERCARD, VISA YA DA TROY KART PROGRAMI',
          'Kart ağlarıyla iş birliğimizden yararlanarak anında sanal ve/veya fiziksel kart programınızı hayata geçirin. Lisans, altyapı ve entegrasyon yükünü biz üstleniyoruz.', img=PROD_ILLUS['kart']),
    split(None, 'SİZİN MARKANIZ, BİZİM ALTYAPIMIZ',
          'Markanıza özel tasarlanmış fiziksel ve sanal kartlarla müşterilerinize kesintisiz bir ödeme deneyimi sunun. Tasarımdan üretime, dağıtımdan yönetime kadar tüm süreç tek elden ilerler.', reverse=True),
    info_boxes([('card','Dinamik Harcama Kontrolleri','Kart bazında limit, MCC kategorisi ve kanal (POS/ATM/online) kısıtları tanımlayın.'),
                ('code','Güçlü API Entegrasyonları','Tek ve çok kullanımlık kartlar, anlık kart üretimi ve programatik yönetim için açık API’ler.'),
                ('shield','Uçtan Uca Güvenlik','3D Secure, tokenizasyon ve gerçek zamanlı izleme ile her işlem koruma altında.')]),
    split(None, 'GÜVENLİ İŞLEMLERLE KAFANIZ RAHAT ETSİN',
          '7/24 kesintisiz çalışan, yapay zeka destekli fraud tespit ve izleme teknolojimiz şüpheli işlemleri anında yakalar. Siz büyümeye odaklanın, güvenliği bize bırakın.', img=ILLUS['security']),
    feature_split('SADAKAT PROGRAMLARI İLE KART İŞİNİZİ BÜYÜTÜN',
          'Geniş üye iş yeri ağımızla müşterilerinize cashback ve nakit iade kampanyaları sunun, sadakati ve işlem hacmini birlikte artırın.',
          ['Üye iş yeri ağında cashback kampanyaları','Kişiselleştirilmiş kampanya kuralları','Anlık puan/iade tahakkuku','Kampanya performans raporları'], reverse=True, img=ILLUS['growth']),
    split(None, 'AÇIK API’LER İLE KART PROGRAMINIZI KURUN VE TEST EDİN',
          'Geliştirici dostu API platformumuz ve sandbox ortamımızla kart programınızı hızlıca kurun, test edin ve canlıya alın. Kapsamlı dokümantasyon ve teknik destek yanınızda.', img=ILLUS['api']),
    split(None, 'ŞEHİR KARTLARI: AYNI ŞEHRE AİT İNSANLAR',
          'Belediyeler için Mastercard/Visa logolu şehir kartları: ulaşım, sosyal yaşam ve altyapı hizmetlerini tek kartta birleştirin. MCC kısıtlamaları, çoklu bakiye ve satıcı seçici desteğiyle.', reverse=True, img=ILLUS['city']),
    feature_split('AKILLI ŞEHİR KARTLARI İLE SOSYAL FAYDA YARATIN',
          'Belediye kartlarıyla sosyal destekleri şeffaf ve izlenebilir biçimde dağıtın; döngüsel ekonomiyi güçlendirin.',
          ['Ulaşım ve otopark ödemeleri','Vergi ve harç tahsilatı','Sosyal yardım ve kredi dağıtımı','Kültür-sanat erişimi'], img=ILLUS['city']),
    strip_section('BAĞIŞIN, DEĞİŞİMİN GÜCÜNE İNANIYORUZ', 'Ürettiğimiz her çözümde toplumsal fayda ve eşit erişim hedefimizi merkeze alıyoruz.', 'strip-blue'),
  ],
  'Markanıza özel sanal ve fiziksel kart programları, akıllı şehir kartları ve güvenli kart altyapısı Moka United ile.')

# --- CÜZDAN ÇÖZÜMLERİ ---
PAGES['cuzdan-cozumleri.html'] = product_page(
  'CÜZDAN ÇÖZÜMLERİ', 'urunler', 'theme-green-medium',
  ribbon_hero('CÜZDAN ÇÖZÜMLERİ', 'Yeni Nesil İletişimin Anahtarı: Dijital Cüzdan',
              'Büyüklüğü ve sektörü ne olursa olsun her şirketin finansal hizmet sunabileceği bir dünya için dijital cüzdan altyapımızla tanışın.', PROD_ILLUS['cuzdan']),
  [ feature_split('PİŞMAN OLMAK YA DA CÜZDAN SAHİBİ OLMAK',
          'Bireysel ve ticari cüzdan yönetiminden katma değerli finansal ürünlere kadar her şey tek uygulamada.',
          ['Cüzdan yönetimi, para transferi ve ön ödemeli kartlar','Kredi, yatırım ve sigorta gibi katma değerli ürünler','“Şimdi Al Sonra Öde” (BNPL) seçenekleri','Cashback ve sadakat kampanyaları'], img=PROD_ILLUS['cuzdan']),
    info_boxes([('safe','E-Para Lisansı Kullanımı','Kendi lisansınız olmadan, bizim e-para lisansımızın altında hizmet verin.'),
                ('code','Güçlü API’ler','Zengin API setiyle kendi fintek markanızı ve müşteri deneyiminizi yaratın.'),
                ('card','Ön Ödemeli Kart Programı','Markanıza özel ön ödemeli kart programını tasarlayıp yayımlayın.'),
                ('people','Teknik & Yasal Destek','Uzman teknik ve hukuk ekiplerimizle uyum ve entegrasyonda yanınızdayız.'),
                ('bolt','Proje Rehberliği','Kurulumdan operasyona kadar uçtan uca proje ve operasyonel destek.')], cols=3),
    faq('Dijital Cüzdan Hakkında Sıkça Sorulan Sorular',
        [('Dijital cüzdan hizmetini kimler sunabilir?',['6493 sayılı Kanun kapsamında, TCMB ve MASAK denetimine tabi lisanslı kuruluşlar sunabilir. Moka United olarak kendi lisansımızla iş ortaklarımıza altyapı sağlıyoruz.']),
         ('Dijital cüzdanın işletmeme faydaları neler?',['Müşteri deneyimini iyileştirir, yeni bir gelir kaynağı yaratır, cashback ve kampanyalarla dönüşüm oranlarını artırır ve güvenli bir ödeme ekosistemi kurar.']),
         ('Cüzdanı markama göre kişiselleştirebilir miyim?',['Evet. Zengin API setimiz ve sürekli güncellenen inovasyonlarımızla cüzdanı tamamen kendi markanıza uyarlayabilirsiniz.']),
         ('Test ortamı sunuyor musunuz?',['Evet. Geliştirici portalımız ve sandbox ortamımızla entegrasyonunuzu canlıya almadan önce güvenle test edebilirsiniz.'])], visible=4),
    inline_form('FİNTEK DÜNYASINA İLK ADIMINIZI DİJİTAL CÜZDAN İLE ATIN!', 'Kendi cüzdan markanızı konuşalım. Formu doldurun, uzman ekibimiz sizinle iletişime geçsin.'),
  ],
  'E-para lisansı, güçlü API’ler ve ön ödemeli kart programlarıyla kendi dijital cüzdan markanızı Moka United ile kurun.')

# --- PARA TRANSFERİ ---
PAGES['para-transferi.html'] = product_page(
  'PARA TRANSFERİ', 'urunler', 'theme-yellow-soft',
  ribbon_hero('PARA TRANSFERİ', 'Dünyanın Her Yerine Işık Hızında Para Transferi',
              'Zamanınız çok kısıtlı ve dünya çok mu büyük? Güvenli ve anlık uluslararası transfer altyapımızla dünyayı bir cep telefonuna sığdırıyoruz.', PROD_ILLUS['transfer']),
  [ split(None, 'BİZ İNSANLARI BİRLEŞTİRMEK VE DÜNYAYI BİR CEP TELEFONUNA SIĞDIRMAK İÇİN BURADAYIZ',
          'API entegrasyonlarımızla güvenli, anlık ve uyumlu uluslararası para transferini herkes için erişilebilir kılıyoruz.', img=PROD_ILLUS['transfer']),
    info_boxes([('clock','%99,9 Çalışma Süresi','Kesintisiz altyapıyla 3 dakikadan kısa sürede tamamlanan işlemler.'),
                ('shield','Güvenlik ve Hız','7/24 izleme, şifreleme ve regülasyona tam uyum.'),
                ('chart','Uyum ve Verimlilik','Operasyonel yükü azaltan, raporlanabilir ve ölçeklenebilir yapı.')]),
    feature_split('ULUSLARARASI PARA TRANSFERİ',
          'İki yönlü transfer altyapımızla dünyayı Türkiye’ye, Türkiye’yi dünyaya bağlıyoruz. İş ortaklarımız arasında Wise ve TransferGo yer alır.',
          ['Yurt dışından Türkiye’ye: banka hesabı, kredi kartı ve cüzdanlara','Türkiye’den yurt dışına: anında para gönderimi','Geniş koridor ağı ve şeffaf ücretlendirme','İş ortakları: Wise, TransferGo'], img=PROD_ILLUS['transfer']),
    feature_split('TİCARİ İŞLETMELER İÇİN',
          'Global ödeme API’lerimizle 190 ülke ve 40’tan fazla para biriminde tahsilat ve ödeme yapın, kendi fintek markanızı kurun.',
          ['190 ülke, 40+ para birimi desteği','Toplu ödeme ve tahsilat','Güvenli emanet (escrow) hizmeti','Kendi fintek markanızı hayata geçirme'], reverse=True, img=ILLUS['api']),
    info_boxes([('building','Sanal Hesap (TL)','İşletmenize özel sanal TL hesabıyla tahsilatlarınızı tek noktada toplayın.'),
                ('clock','Nöbetçi Transfer','Mesai dışı ve tatil günlerinde de kesintisiz işlem imkânı.'),
                ('shield','Uyum ve Güvenlik','TCMB ve MASAK düzenlemelerine tam uyum, çok katmanlı güvenlik.')]),
    inline_form('TÜRKİYE’Yİ PARA TRANSFERİ AĞINIZA EKLEYİN', 'Global transfer ağınıza Türkiye’yi eklemek için ekibimizle iletişime geçin.', extra_field='Şirket / Ülke'),
    faq('Para Transferi Hakkında Sıkça Sorulan Sorular',
        [('Hangi lisansla hizmet veriyorsunuz?',['TCMB tarafından yetkilendirilmiş ödeme ve elektronik para kuruluşu olarak, MASAK düzenlemelerine uyumlu şekilde hizmet veriyoruz.']),
         ('Hangi ülkelere transfer yapabilirim?',['Global API ağımızla 190 ülke ve 40’tan fazla para biriminde işlem yapabilirsiniz.']),
         ('Entegrasyon ne kadar sürer?',['İhtiyaca göre değişmekle birlikte, hazır API’lerimiz ve dokümantasyonumuzla entegrasyon hızlı şekilde tamamlanır.']),
         ('İşlem limitleri nedir?',['Limitler regülasyon ve müşteri profiline göre belirlenir; kurumsal ihtiyaçlar için özel limitler tanımlanabilir.']),
         ('Dövizli işlem yapabilir miyim?',['Evet, 40’tan fazla para biriminde işlem ve dönüşüm desteklenir.']),
         ('Transfer ne kadar sürede ulaşır?',['Birçok koridorda işlemler 3 dakikadan kısa sürede, anlık veya aynı gün tamamlanır.']),
         ('Hangi sektörlere hizmet vermiyorsunuz?',['Bahis, kumar ve kripto gibi regülasyon gereği kısıtlı sektörlere hizmet verilmemektedir.']),
         ('İşlemlerim güvende mi?',['Tüm işlemler şifreli, izlenebilir ve regülasyona uyumlu altyapıda gerçekleştirilir.'])], visible=4),
  ],
  '190 ülke ve 40+ para biriminde anlık uluslararası para transferi; Wise ve TransferGo iş ortaklığıyla Moka United güvencesinde.')

# --- AKILLI KASA ---
PAGES['akilli-kasa.html'] = product_page(
  'AKILLI KASA', 'urunler', 'theme-yellow',
  ribbon_hero('AKILLI KASA', 'Nakit Yönetimi Artık Çok Daha Kolay!',
              'Nakdin depolanması, toplanması, dağıtımı, izlenmesi ve sigortalanması dahil uçtan uca nakit yönetimini üstleniyoruz; siz işinize odaklanın.', PROD_ILLUS['kasa']),
  [ split(None, 'AKILLI KASA İLE TANIŞIN',
          'Mağazanıza yerleştirilen akıllı kasaya yatırılan nakit anında sayılır, geçerliliği doğrulanır ve hesabınıza yansıtılır. Sayım ve güvenlik derdi ortadan kalkar.', img=PROD_ILLUS['kasa']),
    feature_split('İŞLETMENİZDE VERİMLİLİĞİ ARTIRIN',
          'Akıllı kasa, nakit operasyonunuzu baştan sona hızlandırır ve güvence altına alır.',
          ['Nakdiniz anında doğrulansın ve geçerliliği teyit edilsin','Nakit sayma ve tasnif zamanından tasarruf edin','Fonlarınıza daha hızlı erişin','Sigorta kapsamıyla kayıp/hırsızlık riskini ortadan kaldırın'], reverse=True, img=PROD_ILLUS['kasa']),
    info_boxes([('chart','Otomatik Boşaltma İzleme','Kasa doluluğu sistemce takip edilir, doğru zamanda boşaltılır.'),
                ('money','Banka Masrafı Yok','İşlem masrafları şirketimiz tarafından karşılanır.'),
                ('clock','Hafta Sonu & Tatil Erişimi','Mesai dışı günlerde de nakdiniz dijitalleşmeye devam eder.')]),
    inline_form('AKILLI KASA İLE TANIŞMA ZAMANI', 'İşletmeniz için akıllı kasa çözümünü konuşalım; formu doldurun, sizi arayalım.'),
    faq('Akıllı Kasa Hakkında Sıkça Sorulan Sorular',
        [('Kasa dolduğunda ne oluyor?',['Sistem doluluğu otomatik takip eder ve doğru zamanda güvenli tahliye planlar; süreç sizin için yönetilir.']),
         ('Banka masrafları bana mı ait?',['Hayır. İşleme dair masraflar şirketimiz tarafından karşılanır.']),
         ('Kayıp veya çalıntı durumunda sorumluluk kimde?',['Nakit kasaya girdiği andan itibaren sorumluluk ve sigorta kapsamı bize aittir.'])], visible=4),
  ],
  'Akıllı kasa ile mağazanızdaki nakit anında dijitalleşsin; sayım, güvenlik ve sigorta yükünü Moka United üstlensin.')

# --- KİOSK ---
PAGES['kiosk.html'] = product_page(
  'KİOSK', 'urunler', 'theme-green-dark',
  ribbon_hero('KİOSK', 'Self-Servis Kiosk Deneyimi ile Müşterilerinizi Tanıştırın',
              'Kişiselleştirilmiş self-servis kiosklarımızla operasyon maliyetlerinizi azaltın, verimliliğinizi ve müşteri memnuniyetinizi artırın.', PROD_ILLUS['kiosk']),
  [ inline_form('DİJİTALLEŞMEYE İLK ADIMI ATIN', 'Sektörünüze özel kiosk çözümünü konuşalım; formu doldurun, ekibimiz sizinle iletişime geçsin.'),
    feature_split('FARK YARATIN',
          'Dayanıklı donanım ve esnek yazılımıyla kiosklarımız her ortama ve markaya uyum sağlar.',
          ['Yüksek kaliteli malzeme ve işçilik','Dayanıklı, uzun ömürlü yapı','Özelleştirilebilir yazılım ve donanım','Kolay kullanım ve bakım','Farklı boyut ve renk seçenekleri'], img=PROD_ILLUS['kiosk']),
    split(None, 'DÖNÜŞÜMÜ BAŞLATIN',
          'Self-servis kiosklarla müşteri deneyimini iyileştirin, bekleme sürelerini kısaltın ve rekabette öne geçin. 7/24 hizmet, daha az operasyonel yük demek.', reverse=True, img=ILLUS['growth']),
    info_boxes([('plane','Turizm','Otel ve tesislerde self check-in/out ve ödeme.'),
                ('plane','Havaalanı','Lounge girişi, bagaj paketleme, döviz ve ödeme işlemleri.'),
                ('store','Perakende','Self-servis kasa ile hızlı ve temassız alışveriş.'),
                ('file','Fatura Servisleri','Fatura, akaryakıt ve elektrik dağıtım ödemeleri.'),
                ('heart','Sağlık','Hızlı hasta kaydı, randevu ve ödeme işlemleri.'),
                ('building','Kamu','Vatandaş hizmetlerinde hızlı self-servis çözümler.')], cols=3),
    faq('Kiosk Hakkında Sıkça Sorulan Sorular',
        [('Kiosk hangi sektörlerde kullanılır?',['Turizm, havaalanı, perakende, sağlık, kamu ve fatura servisleri başta olmak üzere birçok sektörde kullanılır.']),
         ('Kiosklar özelleştirilebilir mi?',['Evet, marka ve ihtiyaçlarınıza göre yazılım ve donanım özelleştirmesi yapılır.']),
         ('Kioskta ödeme alınabilir mi?',['Evet, kart ve temassız ödeme dahil çeşitli ödeme yöntemleri desteklenir.'])], visible=4),
  ],
  'Turizm, havaalanı, perakende, sağlık ve kamu için özelleştirilebilir self-servis kiosk çözümleri Moka United ile.')

# ---------- HAKKIMIZDA ALT SAYFALARI ----------
def qa_section(title, body, reverse=False, img=None):
    src = img or 'assets/images/placeholder.svg'
    txt = f'<div class="col reveal"><h2>{title}</h2><h4>{body}</h4></div>'
    im = f'<div class="col narrow reveal"><img src="{src}" alt=""></div>'
    inner = (txt + im) if not reverse else (im + txt)
    return f'<section class="split container"><div class="row">{inner}</div></section>'

def country_grid():
    countries = [('Türkiye','tr'),('Almanya','de'),('Azerbaycan','az'),('Özbekistan','uz'),('Gürcistan','ge'),('Birleşik Krallık','gb')]
    cells = ''.join(f'<div class="country-cell reveal"><span class="flag flag-{c}"></span><span>{n}</span></div>' for n, c in countries)
    return f'''<section class="country-section container"><h2 class="text-center">NEREDEYİZ?</h2>
      <p class="text-center" style="max-width:640px;margin:14px auto 40px;color:#555">Altı ülkede yerel gücü uluslararası fintek vizyonuyla birleştiriyoruz.</p>
      <div class="country-grid">{cells}</div></section>'''

PAGES['hikayemiz.html'] = shell(
  'Hikayemiz', 'Moka United’ın kuruluş hikayesi ve zaman içindeki yolculuğu.', 'product-detail', 'hakkimizda',
  breadcrumb([('Moka United','index.html'),('Hakkımızda','hakkimizda.html'),('Hikayemiz',None)]) +
  page_title('HİKAYEMİZ') +
  '<section class="split container"><div class="col reveal" style="flex:1 1 100%;text-align:center"><h2>FİNANSAL <strong>ÇÖZÜM ANAHTARINIZ</strong></h2><h4>Öncü finansal teknolojilerle bugünden geleceğe güvenle adım atmak için bize katılın. Kurumlar, bankalar, KOBİ’ler ve kamu için tek entegrasyonla yenilikçi fintek çözümleri sunuyoruz.</h4></div></section>' +
  strip_section('ZAMANDA ÖNE GEÇMENİZİ SAĞLAYAN FİNANSAL ÇÖZÜM ANAHTARINIZ',
                'Müşterilerimizin zamanının kıymetli olduğunun farkındayız. Ürettiğimiz en yeni, en akıllı, en hızlı ve en güvenli finansal teknolojiyle kıymetli zamanı kazanca dönüştürüyoruz.', 'strip-black') +
  timeline('ZAMAN İÇİNDE UNITED PAYMENT',
           [('2010','United Payment kuruldu; fintek yolculuğu başladı.'),
            ('2015','Elektronik para (e-para) lisansı alındı.'),
            ('2017','Wise ile ortaklık kuruldu; globalleşme başladı.'),
            ('2019','Finberg’den ilk kurumsal yatırım alındı.'),
            ('2021','Remitly, TransferGo, PaySend ve Azimo ile ortaklıklar; OYAK Portföy yatırımı.')]) +
  timeline('ZAMAN İÇİNDE MOKA',
           [('2014','Moka kuruldu; Visa, Mastercard, American Express ve Troy onaylı ödeme kuruluşu.'),
            ('2021','İş Bankası Moka’yı bünyesine kattı.'),
            ('2025','İki güçlü fintek birleşerek Moka United’ı oluşturdu.')]) +
  '<section class="strip strip-black container reveal strip-image"><img src="' + ILLUS['growth'] + '" alt="Moka United büyüme yolculuğu"></section>' +
  '<section class="split container"><div class="col reveal" style="flex:1 1 100%;text-align:center"><h2>BU GÜÇLÜ BİRLEŞMEYLE <span class="multicolors">TÜRKİYE’NİN EN DEĞERLİ FİNTEK ŞİRKETİ</span> OLMA YOLCULUĞUMUZ BURADA BAŞLIYOR.</h2></div></section>' +
  '<section class="landing special"><div class="container"><h3 class="text-center" style="margin-bottom:40px">FİNANSAL <span class="multicolors">ÇÖZÜMLERİNİZ İÇİN</span> HANGİ ANAHTARI İSTERSİNİZ?</h3></div>' +
  cards([('KART ÇÖZÜMLERİ','kart-cozumleri.html',PROD_IMG['kart-cozumleri.html']),
         ('CÜZDAN ÇÖZÜMLERİ','cuzdan-cozumleri.html',PROD_IMG['cuzdan-cozumleri.html']),
         ('PARA TRANSFERİ','para-transferi.html',PROD_IMG['para-transferi.html']),
         ('AKILLI KASA','akilli-kasa.html',PROD_IMG['akilli-kasa.html']),
         ('KİOSK','kiosk.html',PROD_IMG['kiosk.html'])], special=True) + '</section>' +
  qa_section('NASIL BİR <strong>DESTEK SUNUYORUZ?</strong>',
             'Zamanınızın değerli olduğunu biliyoruz. Bu yüzden en yeni, en akıllı, en hızlı ve en güvenli finansal teknoloji yolunu sizin için inşa ediyoruz.', img=ILLUS['security']) +
  qa_section('SİZİ NEREDE <strong>HAYAL EDİYORUZ?</strong>',
             'Sizi; hayatı kolaylaşmış, işi büyümüş ve global rekabette öne geçmiş olarak hayal ediyoruz. Ürettiğimiz her çözüm bu hedefe hizmet ediyor.', reverse=True, img=ILLUS['growth']) +
  qa_section('NASIL BİR <strong>EKİBİMİZ VAR?</strong>',
             'Yüzlerce çalışanımız, her gün milyonlarca kullanıcıya hızlı, kusursuz ve kazançlı bir finansal akış deneyimi sunuyor. Her parça, kesintisiz bir bütün oluşturuyor.', img=ILLUS['team']) +
  country_grid() +
  strip_section('BİZİ NE MOTİVE EDİYOR?',
                'Çözüm anahtarını elinde tutan herkesin eşit şekilde rekabet edebildiği bir finansal dünya yaratmak. Adil, eşit ve akıllı finansal çözümlerin herkes için mümkün olduğuna inanıyoruz.', 'strip-blue') +
  numbers_block('<strong>SAYILARLA</strong> MOKA UNITED',
                ['Altı ülkedeki ofislerimizle yerel gücü uluslararası fintek vizyonuyla birleştiriyoruz.',
                 'Sanal POS, fiziki POS, dijital cüzdan ve kart çözümleriyle farklı sektörlere güvenli ve hızlı hizmet veriyoruz.',
                 'Regülasyonlara uyumlu, sürdürülebilir ve ölçeklenebilir bir altyapı sunuyoruz.']) +
  strip_section('FİNANSAL TEKNOLOJİLERİN TEK BİR ANAHTARA İHTİYACI VAR: MOKA UNITED', 'Yolculuğa birlikte devam edelim.', 'strip-black'))

# (isim, unvan, kısa biyografi)
TEAM_GROUPS = [
  ('YÖNETİM KURULU', [
    ('Necdet Akyel','Yönetim Kurulu Başkanı','Finans ve teknoloji alanında uzun yıllara dayanan deneyimiyle Moka United’ın stratejik yönünü belirler; kurumun büyüme vizyonuna liderlik eder.'),
    ('Yalçın Sezen','Yönetim Kurulu Başkan Vekili','Ödeme sistemleri ve kurumsal yönetim konularındaki tecrübesiyle şirketin sürdürülebilir büyümesine katkı sağlar.'),
    ('Murat Özgen','Yönetim Kurulu Üyesi','Bankacılık ve sermaye piyasaları geçmişiyle kurumsal stratejilere yön verir.'),
    ('Erhan Yeşilkaya','Yönetim Kurulu Üyesi','Finansal hizmetler alanındaki deneyimini şirketin yönetişim süreçlerine taşır.'),
    ('Sezgin Lüle','Yönetim Kurulu Üyesi','Teknoloji ve iş geliştirme perspektifiyle yönetim kuruluna katkı sunar.'),
    ('Hasan Cahit Çınar','Yönetim Kurulu Üyesi','Uzun yıllara dayanan sektör tecrübesiyle stratejik kararların şekillenmesinde rol alır.'),
    ('Oğulcan Toper','Yönetim Kurulu Üyesi','Girişimcilik ve fintek ekosistemi deneyimiyle şirketin inovasyon gündemine katkıda bulunur.'),
    ('Halim Memiş','Yönetim Kurulu Üyesi','Finansal yönetim ve regülasyon alanındaki birikimiyle yönetim kurulunda görev alır.'),
    ('İlker Sözdinler','Yönetim Kurulu Üyesi','Kurumsal strateji ve büyüme konularındaki deneyimini şirketin hedeflerine yansıtır.'),
  ]),
  ('GENEL MÜDÜR YARDIMCILARI', [
    ('Aslı Odabaşı','Strateji ve Büyümeden Sorumlu GMY','Şirketin büyüme stratejilerini, yeni pazarlara açılım ve iş ortaklıklarını yönetir.'),
    ('Başak Yüzbaşıoğlu','Bilgi Teknolojilerinden Sorumlu GMY','Teknoloji altyapısı, yazılım geliştirme ve dijital dönüşüm süreçlerini yönetir.'),
    ('Erender Çekim','Ürün ve İş Geliştirmeden Sorumlu GMY','Ürün stratejisi ve iş geliştirme faaliyetlerini uçtan uca yönetir.'),
    ('Mustafa Ömer Okay','Kamu İlişkilerinden Sorumlu GMY','Düzenleyici kurumlar ve kamu paydaşlarıyla ilişkileri yürütür.'),
    ('Şafak Ergönül','Operasyon ve Fraud’dan Sorumlu GMY','Operasyonel süreçleri ve dolandırıcılık önleme sistemlerini yönetir.'),
    ('Erkut Gazioğulları','Finanstan Sorumlu GMY','Şirketin finansal yönetimini, bütçe ve raporlama süreçlerini yürütür.'),
  ]),
  ('DİREKTÖRLER', [
    ('Aziz Erdem','İç Denetim Direktörü','İç denetim faaliyetlerini planlar ve kurumsal risklerin izlenmesini sağlar.'),
    ('Selma Sever','Kıdemli Risk Yönetimi Direktörü','Kurum genelinde risk yönetimi çerçevesini kurar ve yönetir.'),
    ('Bahar Örücü Atay','Kıdemli Pazarlama Direktörü','Marka, pazarlama ve iletişim stratejilerini yönetir.'),
    ('Başak Sakarya Gül','İnsan Kaynakları Direktörü','İşe alım, yetenek gelişimi ve kurum kültürü süreçlerini yönetir.'),
  ]),
]
def team_cards():
    out = []
    idx = 0
    for group, members in TEAM_GROUPS:
        cards_html = []
        for name, title, bio in members:
            initials = ''.join(w[0] for w in name.split()[:2]).upper()
            cards_html.append(f'''<button class="team-card reveal" data-name="{name}" data-title="{title}" data-bio="{bio}">
              <div class="avatar">{initials}</div>
              <div class="tc-info"><h3>{name}</h3><span class="tc-title">{title}</span></div>
              <span class="tc-arrow">{icon('check') if False else '→'}</span></button>''')
            idx += 1
        out.append(f'<h3 class="team-group-title">{group}</h3><div class="team-grid">' + ''.join(cards_html) + '</div>')
    modal = '''<div class="bio-modal" id="bioModal"><div class="bio-modal-inner">
      <button class="bio-close" aria-label="Kapat">×</button>
      <div class="bio-avatar" id="bioAvatar"></div>
      <h3 id="bioName"></h3><span class="bio-title" id="bioTitle"></span>
      <p id="bioText"></p></div></div>'''
    return '<section class="landing-grid container team-section">' + ''.join(out) + '</section>' + modal

PAGES['kurumsal-yonetim.html'] = shell(
  'Kurumsal Yönetim', 'Moka United yönetim kurulu, genel müdür yardımcıları ve direktörlerinden oluşan kadromuz.', '', 'hakkimizda',
  breadcrumb([('Moka United','index.html'),('Hakkımızda','hakkimizda.html'),('Kurumsal Yönetim',None)]) +
  page_title('KURUMSAL YÖNETİM') + team_cards())

CAREER_DEPTS = ['Bilgi Teknolojileri','Hukuk','İç Kontrol & Uyum','İnsan Kaynakları','Mali ve İdari İşler',
                'Operasyon & Fraud','Pazarlama İletişimi','Risk Yönetimi','Satış','Staj','Strateji ve Büyüme','Ürün','Genel Başvuru']
career_form = '''<section class="career-form-section container">
  <div class="career-links reveal">
    <h2>AÇIK POZİSYONLAR</h2>
    <p>Güncel açık pozisyonlarımızı inceleyin ve size en uygun rolü keşfedin.</p>
    <div class="col-buttons">
      <a class="button button-primary" href="https://www.linkedin.com/company/mokaunited/jobs/" target="_blank" rel="noopener"><span>LINKEDIN’DE GÖR</span></a>
      <a class="button button-secondary" href="https://www.kariyer.net/" target="_blank" rel="noopener"><span>KARİYER.NET’TE GÖR</span></a>
    </div>
  </div>
  <div class="career-form-card reveal">
    <h3>BAŞVURU FORMU</h3>
    <p class="step-sub">Genel havuza başvurmak için formu doldurun; uygun pozisyonlarda sizinle iletişime geçelim.</p>
    <form class="contact-form career-form apply-light" novalidate>
      <div class="form-fields">
        <div class="form-row">
          <div class="form-group"><label class="fld-label">Ad</label><input class="form-control only-letter" name="FirstName" placeholder="Ad" required></div>
          <div class="form-group"><label class="fld-label">Soyad</label><input class="form-control only-letter" name="LastName" placeholder="Soyad" required></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label class="fld-label">E-Posta</label><input class="form-control" type="email" name="Email" placeholder="ornek@eposta.com" required></div>
          <div class="form-group"><label class="fld-label">Telefon</label><input class="form-control only-number" type="tel" name="Phone" placeholder="0 5xx xxx xx xx" required></div>
        </div>
        <div class="form-group full"><label class="fld-label">Departman</label>
          <select class="form-control" name="Department" required>
            <option value="">Seçiniz</option>''' + ''.join(f'<option>{d}</option>' for d in CAREER_DEPTS) + '''
          </select>
        </div>
        <div class="form-group full"><label class="fld-label">Özgeçmiş (PNG, JPG veya PDF — en fazla 10MB)</label>
          <label class="file-drop"><input type="file" name="CV" accept=".png,.jpg,.jpeg,.pdf"><span class="file-drop-text">Dosya seçmek için tıklayın veya sürükleyin</span></label>
        </div>
        <div class="form-group full"><label class="fld-label">Ön Yazı (opsiyonel)</label><textarea class="form-control" name="Message" placeholder="Kendinizden kısaca bahsedin"></textarea></div>
        <label class="form-check"><input type="checkbox" required> Kişisel verilerimin <a href="kvkk-aydinlatma-metni.html">Aydınlatma Metni</a>’nde belirtilen amaçlarla işleneceğini okudum, anladım.</label>
        <div style="text-align:right"><button type="submit" class="button button-primary"><span>GÖNDER</span></button></div>
      </div>
      <div class="form-success"><div class="ok-badge">'''+icon('check')+'''</div><h3>BAŞVURUNUZ ALINMIŞTIR.</h3><p>Uygun pozisyonlarda İnsan Kaynakları ekibimiz sizinle iletişime geçecektir.</p></div>
    </form>
  </div>
</section>'''

PAGES['kariyer.html'] = shell(
  'Kariyer', "Moka United'ta kariyer fırsatları, açık pozisyonlar ve başvuru formu.", '', 'hakkimizda',
  breadcrumb([('Moka United','index.html'),('Hakkımızda','hakkimizda.html'),('Kariyer',None)]) +
  page_title("MOKA UNITED'TA KARİYER") +
  split(None,'NEDEN <strong>MOKA UNITED?</strong>','Fintek ekosisteminin bir parçası olun. 200+ kişilik ekibimizle; esnek çalışma modelleri, açık iletişim ve güvene dayalı bir kültür sunuyoruz. Öncü finansal teknolojiler üreten, global ölçekte büyüyen ve çalışanının gelişimine yatırım yapan bir ekibin parçası olun.',reverse=True, img=ILLUS['team']) +
  info_boxes([('chart','Gelişim','Sürekli öğrenme ve kariyer gelişimi için fırsatlar.'),
              ('global','Global Ekip','6 ülkede 250+ çalışanla uluslararası bir ekip.'),
              ('bolt','Esneklik','Modern ve esnek çalışma kültürü.')]) +
  career_form)

def subsidiary(name, meta, body, reverse=False):
    metas = ''.join(f'<span class="sub-meta">{m}</span>' for m in meta)
    txt = f'''<div class="col reveal"><h2>{name}</h2><div class="sub-metas">{metas}</div><h4>{body}</h4></div>'''
    im = '<div class="col narrow reveal"><img src="assets/images/placeholder.svg" alt=""></div>'
    inner = (txt + im) if not reverse else (im + txt)
    return f'<section class="split container"><div class="row">{inner}</div></section>'

PAGES['istirakler.html'] = shell(
  'İştirakler', 'Moka United iştirakleri: RUUT, Turan, Up Enerji ve SmartUp.', '', 'hakkimizda',
  breadcrumb([('Moka United','index.html'),('Hakkımızda','hakkimizda.html'),('İştirakler',None)]) +
  page_title('İŞTİRAKLER') +
  subsidiary('RUUT', ['Kuruluş: 2022','Merkez: Londra','Is United Payment Systems Limited'],
             'İngiltere’deki KOBİ’ler için ödeme kabul çözümleri, ticari hesap ve kart ile para transferini tek platformda birleştiren dijital finans markası. İletişim: info@ruutapp.com', reverse=True) +
  subsidiary('TURAN', ['Kuruluş: 2022','Moka United hissesi: %68','8 dil desteği'],
             'Tüm Türk Devletlerinde yaşayan kullanıcılar için tasarlanmış uluslararası para transferi ve finans uygulaması. Türkçe, Azerbaycan Türkçesi, Özbekçe, Türkmence, Rusça, Gürcüce, Moğolca ve İngilizce desteği sunar.') +
  subsidiary('UP ENERJİ', ['Kuruluş: 2021','Moka United hissesi: %75','Enerji & mobilite'],
             'Akaryakıt, elektrikli araç şarjı ve mobilite hizmetlerini tek bir dijital ekosistemde birleştiren enerji odaklı finansal teknoloji markası.', reverse=True) +
  subsidiary('SMARTUP', ['SmartUp Teknoloji Araştırma ve Geliştirme A.Ş.','Donanım & yazılım'],
             'Kiosk sistemleri, akıllı kargo dolapları, RVM (geri dönüşüm) cihazları ve EV şarj sistemleri geliştirir. Mekanik tasarım, elektronik geliştirme ve gömülü sistemler alanında uçtan uca çözüm sunar.'))

# ---------- İLETİŞİM ----------
OFFICES_TR = [
  ('İstanbul Merkez','Levent Mah. Meltem Sk. İş Bankası Kuleleri No: 10 Kule: 2 PK. 34330 Beşiktaş/İstanbul','İş Bankası Kuleleri Beşiktaş İstanbul'),
  ('Ankara','Macun Mah. 187 Cad. No: 54/89 Yenimahalle/Ankara','Macun Mahallesi Yenimahalle Ankara'),
  ('İstanbul Teknopark','Kazlıçeşme Mah. 245. Sk. No: 5 Zeytinburnu/İstanbul','Teknopark İstanbul Zeytinburnu'),
  ('İstanbul Gayrettepe','Esentepe Mah. Büyükdere Cad. No:102/14 Maya Akar Center, Şişli/İstanbul','Maya Akar Center Şişli İstanbul'),
]
OFFICES_INTL = [
  ('Birleşik Krallık — Londra','1 King William St, London EC4N 7AF','1 King William Street London'),
  ('Azerbaycan — Bakü','Alaaddin Guliyev 1131, Babek Plaza A Block','Babek Plaza Baku'),
  ('Almanya — Frankfurt','Maxi Digital GmbH, Taunustor 1, Frankfurt am Main','Taunustor 1 Frankfurt'),
  ('Gürcistan — Tiflis','United Payment Georgia LTD, D. Arakishvili St.','D. Arakishvili Street Tbilisi'),
]
def office_cards():
    def card(name, addr, q):
        maps = 'https://www.google.com/maps/search/?api=1&query=' + q.replace(' ', '+')
        return f'''<div class="office-card reveal"><h5>{name}</h5><p>{addr}</p>
          <a class="button button-secondary" href="{maps}" target="_blank" rel="noopener"><span>YOL TARİFİ AL</span></a></div>'''
    tr = ''.join(card(*o) for o in OFFICES_TR)
    intl = ''.join(card(*o) for o in OFFICES_INTL)
    return f'''<section class="offices-section container">
      <h2 class="text-center"><strong>OFİSLERİMİZ</strong></h2>
      <h3 class="offices-sub">Türkiye</h3><div class="office-cards">{tr}</div>
      <h3 class="offices-sub">Uluslararası</h3><div class="office-cards">{intl}</div>
    </section>'''

contact_form = '''<form class="contact-form" novalidate>
  <div class="form-fields">
    <div class="form-row">
      <div class="form-group"><input class="form-control only-letter" type="text" name="FirstName" placeholder="Ad" required></div>
      <div class="form-group"><input class="form-control only-letter" type="text" name="LastName" placeholder="Soyad" required></div>
    </div>
    <div class="form-row">
      <div class="form-group"><input class="form-control only-number" type="tel" name="Phone" placeholder="Telefon" required></div>
      <div class="form-group"><input class="form-control" type="email" name="Email" placeholder="E-Posta" required></div>
    </div>
    <div class="form-group full"><textarea class="form-control" name="Message" placeholder="Mesajınız" required></textarea></div>
    <label class="form-check"><input type="checkbox" required> Kişisel verilerimin <a href="kvkk-aydinlatma-metni.html">Aydınlatma Metni</a>’nde belirtilen amaçlarla işleneceğini okudum, anladım.</label>
    <div style="text-align:right"><button type="submit" class="button button-primary"><span>GÖNDER</span></button></div>
  </div>
  <div class="form-success">
    <h3 style="color:#fff">MESAJINIZ BAŞARIYLA GÖNDERİLMİŞTİR.</h3>
    <p style="color:#ccc;margin-top:12px">Ekibimiz 48 saat içinde e-posta veya telefonla dönüş yapacaktır.</p>
  </div>
</form>'''

PAGES['iletisim.html'] = shell(
  'İletişim', 'Moka United ile iletişime geçin.', 'product-detail', 'iletisim',
  breadcrumb([('Moka United','index.html'),('İletişim',None)]) +
  '<section class="contact-page container"><h1 class="multicolors">SİZE NASIL YARDIMCI OLABİLİRİZ?</h1>' +
  '<div class="contact-row"><div class="contact-col reveal">' +
  '<div class="contact-box dark"><h5>İletişim</h5><h3>İLETİŞİM FORMUMUZU DOLDURUN</h3>' + contact_form + '</div>' +
  '</div><div class="contact-col reveal">' +
  '<div class="contact-box contact-side-box"><div><h5>Müşteri Hizmetleri</h5><h3>BİZİ ARAYIN</h3></div><a class="button button-primary" href="tel:+908502522222"><span>ARA</span></a></div>' +
  '<div class="contact-box contact-side-box"><div><h5>Whatsapp</h5><h3>WHATSAPP’TAN KONUŞALIM MI?</h3></div><a class="button button-primary" href="https://api.whatsapp.com/send?phone=908502522222" target="_blank" rel="noopener"><span>İLETİŞİME GEÇ</span></a></div>' +
  '<div class="contact-box"><h5 style="color:var(--brand-blue)">E-Posta</h5><h3>info@mokaunited.com</h3></div>' +
  '</div></div></section>' + office_cards())

# ---------- BAŞVURU (Hemen Başvurun) — çok adımlı sihirbaz ----------
apply_wizard = '''<div class="apply-wizard" id="applyWizard">
  <div class="wizard-progress">
    <div class="wp-step active" data-step="1"><span class="wp-num">1</span> İşletme Bilgileri</div>
    <div class="wp-step" data-step="2"><span class="wp-num">2</span> Yetkili &amp; İletişim</div>
    <div class="wp-step" data-step="3"><span class="wp-num">3</span> Çözüm Seçimi</div>
    <div class="wp-step" data-step="4"><span class="wp-num">4</span> Özet &amp; Onay</div>
  </div>
  <div class="apply-form-wrap">
    <form class="apply-light" id="applyForm" novalidate>
      <div class="wizard-card">

        <!-- ADIM 1: İşletme -->
        <div class="form-step active" data-step="1">
          <h3>İşletme Bilgileri</h3>
          <p class="step-sub">Başvuru yapan işletmeyi tanıyalım.</p>
          <div class="form-group">
            <label class="fld-label">İşletme Türü</label>
            <div class="biz-type">
              <label><input type="radio" name="BizType" value="Şahıs Şirketi" required> Şahıs Şirketi</label>
              <label><input type="radio" name="BizType" value="Limited Şirket"> Limited Şirket</label>
              <label><input type="radio" name="BizType" value="Anonim Şirket"> Anonim Şirket</label>
              <label><input type="radio" name="BizType" value="Esnaf"> Esnaf</label>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">İşletme / Ticari Unvan</label><input class="form-control" name="Company" placeholder="Örn. Demo Ticaret Ltd. Şti." required></div>
            <div class="form-group"><label class="fld-label">Faaliyet Sektörü</label>
              <select class="form-control" name="Sector" required>
                <option value="">Seçiniz</option>
                <option>E-ticaret</option><option>Perakende</option><option>Restoran / Kafe</option>
                <option>Hizmet</option><option>Turizm / Konaklama</option><option>Sağlık</option>
                <option>Eğitim</option><option>Diğer</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">Vergi Dairesi</label><input class="form-control" name="TaxOffice" placeholder="Örn. Beşiktaş"></div>
            <div class="form-group"><label class="fld-label">Vergi / TC Kimlik No</label><input class="form-control only-number" name="TaxNo" placeholder="Vergi veya TC No" required></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">Web Sitesi (varsa)</label><input class="form-control" name="Website" placeholder="https://"></div>
            <div class="form-group"><label class="fld-label">Tahmini Aylık Ciro</label>
              <select class="form-control" name="Turnover">
                <option value="">Seçiniz</option>
                <option>0 - 100.000 ₺</option><option>100.000 - 500.000 ₺</option>
                <option>500.000 - 1.000.000 ₺</option><option>1.000.000 ₺ ve üzeri</option>
              </select>
            </div>
          </div>
          <div class="step-nav"><span class="spacer"></span>
            <button type="button" class="button button-primary wz-next"><span>İLERİ →</span></button>
          </div>
        </div>

        <!-- ADIM 2: Yetkili -->
        <div class="form-step" data-step="2">
          <h3>Yetkili &amp; İletişim</h3>
          <p class="step-sub">Başvuruyu değerlendirdiğimizde size nasıl ulaşalım?</p>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">Ad</label><input class="form-control only-letter" name="FirstName" placeholder="Ad" required></div>
            <div class="form-group"><label class="fld-label">Soyad</label><input class="form-control only-letter" name="LastName" placeholder="Soyad" required></div>
          </div>
          <div class="form-group"><label class="fld-label">Yetkili Ünvanı</label><input class="form-control" name="Title" placeholder="Örn. Genel Müdür / İşletme Sahibi"></div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">Telefon</label><input class="form-control only-number" type="tel" name="Phone" placeholder="0 5xx xxx xx xx" required></div>
            <div class="form-group"><label class="fld-label">E-Posta</label><input class="form-control" type="email" name="Email" placeholder="ornek@sirket.com" required></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">İl</label><input class="form-control only-letter" name="City" placeholder="İstanbul" required></div>
            <div class="form-group"><label class="fld-label">İlçe</label><input class="form-control only-letter" name="District" placeholder="Beşiktaş"></div>
          </div>
          <div class="form-group"><label class="fld-label">Adres</label><textarea class="form-control" name="Address" placeholder="İşletme adresi"></textarea></div>
          <div class="step-nav">
            <button type="button" class="button button-secondary wz-prev"><span>← GERİ</span></button>
            <span class="spacer"></span>
            <button type="button" class="button button-primary wz-next"><span>İLERİ →</span></button>
          </div>
        </div>

        <!-- ADIM 3: Çözümler -->
        <div class="form-step" data-step="3">
          <h3>Çözüm Seçimi</h3>
          <p class="step-sub">İlgilendiğiniz ödeme çözümlerini seçin (birden fazla seçebilirsiniz).</p>
          <div class="choice-grid">
            <label class="choice-card"><input type="checkbox" name="Product" value="Sanal POS"><span><span class="cc-title">Sanal POS</span><span class="cc-desc">E-ticaret ve mobil uygulamadan online ödeme</span></span></label>
            <label class="choice-card"><input type="checkbox" name="Product" value="Fiziki POS"><span><span class="cc-title">Fiziki POS</span><span class="cc-desc">Mağaza içi kartlı tahsilat cihazı</span></span></label>
            <label class="choice-card"><input type="checkbox" name="Product" value="Linkle Tahsilat"><span><span class="cc-title">Linkle Tahsilat</span><span class="cc-desc">Web sitesiz, ödeme linkiyle tahsilat</span></span></label>
            <label class="choice-card"><input type="checkbox" name="Product" value="Kart Çözümleri"><span><span class="cc-title">Kart Çözümleri</span><span class="cc-desc">Kuruma özel fiziksel/sanal kart</span></span></label>
            <label class="choice-card"><input type="checkbox" name="Product" value="Cüzdan Çözümleri"><span><span class="cc-title">Cüzdan Çözümleri</span><span class="cc-desc">Dijital cüzdan ve ön ödemeli kart</span></span></label>
            <label class="choice-card"><input type="checkbox" name="Product" value="Para Transferi"><span><span class="cc-title">Para Transferi</span><span class="cc-desc">Yurt içi ve yurt dışı transfer</span></span></label>
          </div>
          <div class="form-group" style="margin-top:20px"><label class="fld-label">Eklemek istedikleriniz (opsiyonel)</label><textarea class="form-control" name="Message" placeholder="İhtiyaçlarınızı kısaca anlatın"></textarea></div>
          <div class="step-nav">
            <button type="button" class="button button-secondary wz-prev"><span>← GERİ</span></button>
            <span class="spacer"></span>
            <button type="button" class="button button-primary wz-next"><span>İLERİ →</span></button>
          </div>
        </div>

        <!-- ADIM 4: Özet & Onay -->
        <div class="form-step" data-step="4">
          <h3>Özet &amp; Onay</h3>
          <p class="step-sub">Bilgilerinizi kontrol edip başvuruyu tamamlayın.</p>
          <div class="summary-box" id="applySummary"></div>
          <label class="form-check"><input type="checkbox" name="kvkk" required> Kişisel verilerimin <a href="kvkk-aydinlatma-metni.html">Aydınlatma Metni</a>’nde belirtilen amaçlarla işleneceğini okudum, anladım.</label>
          <label class="form-check"><input type="checkbox" name="sozlesme" required> <a href="yasal-belgeler-ve-temsilcilikler.html">Üye İş Yeri Sözleşmesi</a> ve başvuru koşullarını kabul ediyorum.</label>
          <div class="step-nav">
            <button type="button" class="button button-secondary wz-prev"><span>← GERİ</span></button>
            <span class="spacer"></span>
            <button type="submit" class="button button-primary"><span>BAŞVURUYU GÖNDER</span></button>
          </div>
        </div>

      </div>
    </form>
  </div>

  <div class="wizard-card wizard-success" id="applySuccess">
    <div class="ok-badge">✓</div>
    <h3 style="color:var(--brand-blue)">BAŞVURUNUZ ALINMIŞTIR</h3>
    <p style="color:#555;max-width:480px;margin:14px auto 0">Ekibimiz başvurunuzu değerlendirip <strong>en geç 3 iş günü içinde</strong> e-posta veya telefonla sizinle iletişime geçecektir. Acil durumlar için WhatsApp hattımızı kullanabilirsiniz.</p>
    <div style="margin-top:24px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a class="button button-primary" href="index.html"><span>ANA SAYFAYA DÖN</span></a>
      <a class="button button-secondary" href="https://api.whatsapp.com/send?phone=908502522222" target="_blank" rel="noopener"><span>WHATSAPP</span></a>
    </div>
  </div>

  <div class="apply-trust">
    <span class="t-item">Ücretsiz başvuru</span>
    <span class="t-item">3 iş gününde sonuç</span>
    <span class="t-item">Tüm bankalarla tek entegrasyon</span>
    <span class="t-item">PCI DSS uyumlu güvenlik</span>
  </div>
</div>'''

PAGES['basvuru.html'] = shell(
  'Hemen Başvurun', 'Moka United POS başvurusu yapın; sanal POS, fiziki POS ve linkle tahsilat çözümleri için çok adımlı başvuru formunu doldurun.',
  'product-detail', 'basvuru',
  breadcrumb([('Moka United','index.html'),('Hemen Başvurun',None)]) +
  '<section class="apply-page container"><h1 class="multicolors">HEMEN BAŞVURUN</h1>' +
  '<p class="lead">POS ve ödeme çözümleri başvurunuzu 4 adımda tamamlayın. Başvuru ücretsizdir ve hiçbir taahhüt içermez.</p>' +
  apply_wizard + '</section>')

# ---------- İTİRAZ (İşlem Sorgulama ve İtiraz) — çok adımlı sihirbaz ----------
dispute_wizard = '''<div class="apply-wizard dispute-wizard" id="disputeWizard">
  <div class="wizard-progress">
    <div class="wp-step active" data-step="1"><span class="wp-num">1</span> Sorgu</div>
    <div class="wp-step" data-step="2"><span class="wp-num">2</span> Doğrulama</div>
    <div class="wp-step" data-step="3"><span class="wp-num">3</span> Hatırlatma</div>
    <div class="wp-step" data-step="4"><span class="wp-num">4</span> Sonuç</div>
  </div>
  <div class="apply-form-wrap">
    <div class="wizard-card">

      <!-- EKRAN: sorgu formu -->
      <div class="dispute-screen active" data-screen="query">
        <h3>İşleminizi Sorgulayın</h3>
        <p class="step-sub">Ekstrenizde tanımadığınız bir işlem mi var? Aşağıdaki bilgilerle işleminizi bulalım.</p>
        <div class="kvkk-note">
          <span class="kn-ic">🔒</span>
          <p>Girdiğiniz bilgiler yalnızca işleminizi eşleştirmek amacıyla kullanılır ve üçüncü kişilerle paylaşılmaz. Detaylar için <a href="kvkk-aydinlatma-metni.html">Aydınlatma Metni</a>'ni inceleyebilirsiniz.</p>
        </div>
        <form class="apply-light" id="disputeQueryForm" novalidate>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">İşlem Tarihi</label><input class="form-control" type="date" name="TxnDate" required></div>
            <div class="form-group"><label class="fld-label">İşlem Tutarı (₺)</label><input class="form-control" type="number" step="0.01" min="0" name="TxnAmount" placeholder="Örn. 7650.00" required></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="fld-label">Kartın İlk 6 Hanesi (BIN)</label><input class="form-control only-number" name="TxnBin" maxlength="6" inputmode="numeric" placeholder="Örn. 526955" required></div>
            <div class="form-group"><label class="fld-label">Kartın Son 4 Hanesi</label><input class="form-control only-number" name="TxnLast4" maxlength="4" inputmode="numeric" placeholder="Örn. 3339" required></div>
          </div>
          <div class="dispute-attempts" id="queryAttempts" hidden></div>
          <div class="step-nav"><span class="spacer"></span>
            <button type="submit" class="button button-primary"><span>SORGULA →</span></button>
          </div>
        </form>
      </div>

      <!-- EKRAN: bulunamadı -->
      <div class="dispute-screen" data-screen="notfound">
        <div class="dispute-result-icon warn">✕</div>
        <h3>İşlem Bulunamadı</h3>
        <p class="step-sub">Girdiğiniz bilgilerle eşleşen bir işlem bulamadık. Lütfen tarih, tutar ve kart bilgilerinizi kontrol ederek tekrar deneyin.</p>
        <div class="step-nav"><span class="spacer"></span>
          <button type="button" class="button button-primary" id="disputeRetry"><span>TEKRAR DENE</span></button>
        </div>
      </div>

      <!-- EKRAN: çok fazla deneme -->
      <div class="dispute-screen" data-screen="locked">
        <div class="dispute-result-icon warn">⏳</div>
        <h3>Çok Fazla Deneme</h3>
        <p class="step-sub">Güvenliğiniz için bu oturumda çok fazla başarısız deneme yapıldı. Lütfen bir süre sonra tekrar deneyin ya da doğrudan bankanızla iletişime geçin.</p>
      </div>

      <!-- EKRAN: kart hamili doğrulama -->
      <div class="dispute-screen" data-screen="challenge">
        <h3>Kart Hamili Doğrulama</h3>
        <p class="step-sub">İşyeri bilgisini gösterebilmemiz için işlemi gerçekten sizin yaptığınızı doğrulamamız gerekiyor.</p>
        <div class="form-group">
          <label class="fld-label">Bu işlem tek çekim mi, taksitli mi?</label>
          <div class="challenge-options" id="chInstallment" data-group="installment">
            <button type="button" class="chip-option" data-value="1">Tek Çekim</button>
            <button type="button" class="chip-option" data-value="2">2 Taksit</button>
            <button type="button" class="chip-option" data-value="3">3 Taksit</button>
            <button type="button" class="chip-option" data-value="6">6 Taksit</button>
            <button type="button" class="chip-option" data-value="9">9 Taksit</button>
          </div>
        </div>
        <div class="form-group">
          <label class="fld-label">İşlem yaklaşık saat kaçta yapıldı?</label>
          <div class="challenge-options" id="chTime" data-group="time">
            <button type="button" class="chip-option" data-value="00-06">00:00–06:00</button>
            <button type="button" class="chip-option" data-value="06-09">06:00–09:00</button>
            <button type="button" class="chip-option" data-value="09-12">09:00–12:00</button>
            <button type="button" class="chip-option" data-value="12-15">12:00–15:00</button>
            <button type="button" class="chip-option" data-value="15-18">15:00–18:00</button>
            <button type="button" class="chip-option" data-value="18-21">18:00–21:00</button>
            <button type="button" class="chip-option" data-value="21-24">21:00–24:00</button>
          </div>
        </div>
        <div class="dispute-attempts" id="challengeAttempts" hidden></div>
        <div class="step-nav"><span class="spacer"></span>
          <button type="button" class="button button-primary" id="challengeSubmit"><span>DOĞRULA →</span></button>
        </div>
      </div>

      <!-- EKRAN: asgari ifşa / hatırlatma -->
      <div class="dispute-screen" data-screen="disclosure">
        <h3>Bu Harcamayı Hatırlıyor musunuz?</h3>
        <p class="step-sub">Doğrulamanız başarılı. İşte işleminize ait asgari bilgiler:</p>
        <div class="disclosure-card" id="disclosureCard"></div>
        <div class="step-nav dispute-choice-nav">
          <button type="button" class="button button-secondary" id="btnNotRecall"><span>HÂLÂ TANIMIYORUM</span></button>
          <button type="button" class="button button-primary" id="btnRecall"><span>BU HARCAMAYI HATIRLADIM</span></button>
        </div>
      </div>

      <!-- EKRAN: hatırladı (deflection başarılı) -->
      <div class="dispute-screen" data-screen="remembered">
        <div class="dispute-result-icon ok">✓</div>
        <h3>Teşekkürler!</h3>
        <p class="step-sub">Harcamanızı hatırladığınıza sevindik. Herhangi bir itiraz sürecine gerek kalmadı; ekstrenizde başka bir sorun görürseniz bu sayfaya tekrar dönebilirsiniz.</p>
        <div class="step-nav"><span class="spacer"></span>
          <a class="button button-primary" href="index.html"><span>ANA SAYFAYA DÖN</span></a>
        </div>
      </div>

      <!-- EKRAN: taze işlem — otomatik iade -->
      <div class="dispute-screen" data-screen="result-unsettled">
        <div class="dispute-result-icon ok">✓</div>
        <h3>İşleminiz İade Sürecine Alındı</h3>
        <p class="step-sub">İşleminiz henüz takas edilmediği için tarafımızca otomatik olarak iptal (void) işlemine alındı. Tutar, bankanızın süreçlerine bağlı olarak birkaç iş günü içinde hesabınıza yansıyacaktır.</p>
        <div class="summary-box" id="resultRefUnsettled"></div>
        <p class="dispute-fineprint">Bu bilgilendirme kesin bir iade garantisi teşkil etmez; sürecin nihai sonucu bankanız ve ilgili kart şeması kurallarına tabidir.</p>
        <div class="step-nav"><span class="spacer"></span>
          <a class="button button-primary" href="index.html"><span>ANA SAYFAYA DÖN</span></a>
        </div>
      </div>

      <!-- EKRAN: takas edilmiş işlem — üye işyerine iletildi -->
      <div class="dispute-screen" data-screen="result-settled">
        <div class="dispute-result-icon info">ℹ</div>
        <h3>Talebiniz Üye İşyerine İletildi</h3>
        <p class="step-sub">İşleminiz zaten takas edildiği için tarafımızca doğrudan iptal edilemiyor. Talebiniz üye işyerine iletildi. Süreci hızlandırmak isterseniz aşağıdaki bilgilerle kendi bankanıza başvurup ters ibraz (chargeback) talebinde bulunabilirsiniz; bu süreci yalnızca kartınızı veren banka başlatabilir.</p>
        <div class="summary-box" id="resultRefSettled"></div>
        <p class="dispute-fineprint">Bu bilgilendirme kesin bir sonuç garantisi teşkil etmez.</p>
        <div class="step-nav"><span class="spacer"></span>
          <a class="button button-primary" href="index.html"><span>ANA SAYFAYA DÖN</span></a>
        </div>
      </div>

    </div>
  </div>
</div>'''

PAGES['itiraz.html'] = shell(
  'İtiraz — İşlem Sorgulama', 'Ekstrenizde tanımadığınız bir işlem mi var? İşleminizi sorgulayın, gerekirse itiraz sürecini bu sayfadan başlatın.',
  'product-detail', 'itiraz',
  breadcrumb([('Moka United','index.html'),('İtiraz',None)]) +
  '<section class="apply-page container"><h1 class="multicolors">İŞLEM SORGULAMA VE İTİRAZ</h1>' +
  '<p class="lead">Ekstrenizde tanımadığınız bir işlem mi var? Aşağıdaki bilgilerle işleminizi sorgulayın; hatırlamıyorsanız itiraz sürecini bu sayfadan başlatabilirsiniz.</p>' +
  dispute_wizard + '</section>')

# ---------- PANEL GİRİŞİ ----------
PAGES['panel-giris.html'] = shell(
  'Panel Girişi', 'Moka United paneline giriş yapın.', 'product-detail', 'panel',
  breadcrumb([('Moka United','index.html'),('Panel Girişi',None)]) +
  '''<section class="login-page container"><div class="login-card reveal">
    <h2>PANEL GİRİŞİ</h2><p>Moka United paneline giriş yaparak ödeme süreçlerinizi yönetin.</p>
    <form class="contact-form" novalidate>
      <div class="form-fields">
        <div class="form-group"><input class="form-control" type="email" placeholder="E-Posta" required></div>
        <div class="form-group"><input class="form-control" type="password" placeholder="Şifre" required></div>
        <div class="login-row"><label class="remember"><input type="checkbox"> Beni hatırla</label><a href="javascript:;">Şifremi unuttum</a></div>
        <button type="submit" class="button button-primary w-full"><span>GİRİŞ YAP</span></button>
      </div>
      <div class="form-success"><h3 style="color:#fff">Giriş Demo</h3><p style="color:#ccc;margin-top:8px">Bu bir klon çalışmasıdır; gerçek panel bağlantısı yoktur.</p></div>
    </form>
    <p class="login-foot">Hesabınız yok mu? <a href="basvuru.html">Hemen başvurun</a></p>
  </div></section>''')

# ---------- YASAL / METİN SAYFALARI ----------
def legal_page(fname, title, active, intro, sections):
    blocks = ''
    for h, ps in sections:
        inner = ''.join(f'<p>{p}</p>' for p in ps)
        blocks += f'<div class="legal-block reveal"><h3>{h}</h3>{inner}</div>'
    body = (breadcrumb([('Moka United','index.html'),(title,None)]) + page_title(title) +
            f'<section class="legal container"><p class="legal-intro">{intro}</p>{blocks}</section>')
    return shell(title, intro[:150], '', active, body)

PAGES['gizlilik-politikasi.html'] = legal_page(
  'gizlilik-politikasi.html', 'GİZLİLİK POLİTİKASI', '',
  'Moka United olarak kullanıcılarımızın gizliliğine önem veriyoruz. Bu politika, kişisel verilerinizin nasıl toplandığını, kullanıldığını ve korunduğunu açıklar. (Bu metin klon çalışması için hazırlanmış örnek içeriktir.)',
  [('Toplanan Bilgiler',['Web sitemizi kullanırken form aracılığıyla paylaştığınız ad, e-posta ve telefon gibi iletişim bilgileri ile site kullanımına dair teknik veriler toplanabilir.']),
   ('Bilgilerin Kullanımı',['Toplanan bilgiler; taleplerinizi yanıtlamak, hizmet kalitesini artırmak ve yasal yükümlülükleri yerine getirmek amacıyla kullanılır.']),
   ('Çerezler',['Site deneyimini iyileştirmek için çerezler kullanılır. Çerez tercihlerinizi tarayıcınızdan yönetebilirsiniz.']),
   ('Veri Güvenliği',['Verileriniz endüstri standardı güvenlik önlemleriyle korunur ve yetkisiz erişime karşı saklanır.']),
   ('İletişim',['Gizlilikle ilgili sorularınız için info@mokaunited.com adresinden bize ulaşabilirsiniz.'])])

PAGES['kisisel-verilerin-korunmasi.html'] = legal_page(
  'kisisel-verilerin-korunmasi.html', 'KİŞİSEL VERİLERİN KORUNMASI', '',
  '6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) kapsamında kişisel verilerinizin işlenmesine ilişkin bilgilendirme. (Örnek klon içeriği.)',
  [('Veri Sorumlusu',['Kişisel verileriniz, veri sorumlusu sıfatıyla Moka United tarafından işlenmektedir.']),
   ('İşleme Amaçları',['Kişisel verileriniz; hizmetlerin sunulması, sözleşmesel yükümlülüklerin yerine getirilmesi ve yasal zorunluluklar kapsamında işlenir.']),
   ('Haklarınız',['KVKK kapsamında verilerinize erişme, düzeltilmesini isteme, silinmesini talep etme ve işlemeye itiraz etme haklarına sahipsiniz.']),
   ('Başvuru',['Haklarınızı kullanmak için info@mokaunited.com adresine yazılı başvuruda bulunabilirsiniz.'])])

PAGES['cerez-politikasi.html'] = legal_page(
  'cerez-politikasi.html', 'ÇEREZ POLİTİKASI', '',
  'Bu çerez politikası, web sitemizde kullanılan çerezler ve bunları nasıl yönetebileceğiniz hakkında bilgi verir. (Örnek klon içeriği.)',
  [('Çerez Nedir?',['Çerezler, siteyi ziyaret ettiğinizde cihazınıza kaydedilen küçük metin dosyalarıdır ve site deneyimini iyileştirmeye yardımcı olur.']),
   ('Çerez Türleri',['Zorunlu çerezler sitenin çalışması için gereklidir. Analitik çerezler kullanım istatistiklerini toplar. Pazarlama çerezleri ilgi alanlarınıza uygun içerik sunar.']),
   ('Çerezleri Yönetme',['Tarayıcı ayarlarınızdan çerezleri kabul edebilir, reddedebilir veya silebilirsiniz.'])])

PAGES['bilgi-toplumu-hizmetleri.html'] = shell(
  'Bilgi Toplumu Hizmetleri', 'Moka United şirket ve ticaret sicil bilgileri.', '', '',
  breadcrumb([('Moka United','index.html'),('Bilgi Toplumu Hizmetleri',None)]) + page_title('BİLGİ TOPLUMU HİZMETLERİ') +
  '''<section class="legal container"><p class="legal-intro">Ticaret sicili ve şirket bilgileri aşağıda yer almaktadır. (Örnek klon içeriği.)</p>
  <table class="info-table">
    <tr><td>Ticaret Unvanı</td><td>Moka United Ödeme Hizmetleri ve Elektronik Para Kuruluşu A.Ş.</td></tr>
    <tr><td>Mersis No</td><td>0178071182100017</td></tr>
    <tr><td>Adres</td><td>Levent Mah. Meltem Sk. İş Bankası Kuleleri No: 10 Kule: 2, Beşiktaş/İstanbul</td></tr>
    <tr><td>Telefon</td><td>+90 850 252 22 22</td></tr>
    <tr><td>E-Posta</td><td>info@mokaunited.com</td></tr>
    <tr><td>KEP Adresi</td><td>mokaunited@hs01.kep.tr</td></tr>
  </table></section>''')

# (belge adı, hedef sayfa veya None → modalda örnek metin)
LEGAL_DOCS = [
  ('Ürün ve Ücretler', None), ('Bağımsız Denetim Bilgileri', None), ('Şikayet Politikası', None),
  ('Tek Seferlik Ödeme Bilgisi', None), ('Temsilciliklerimiz', None), ('Bilgi Güvenliği Politikası', None),
  ('KVKK Aydınlatma Metni', 'kvkk-aydinlatma-metni.html'), ('TÖDEB Hakem Heyeti', None),
  ('Şirket Bilgileri', 'bilgi-toplumu-hizmetleri.html'), ('Bilgi Toplumu Hizmetleri', 'bilgi-toplumu-hizmetleri.html'),
  ('Tüketici Bilgilendirme Metni', None), ('Üye İş Yeri Sözleşmesi', None), ('POS Başvuru Koşulları', None),
  ('Çerçeve Sözleşmesi', None), ('Aydınlatma Metni', 'kvkk-aydinlatma-metni.html'),
  ('Sanal Cüzdan ve Ön Ödemeli Kart Sözleşmesi', None), ('Kişisel Verilerin İşlenmesi Politikası', 'kisisel-verilerin-korunmasi.html'),
  ('Mesafeli Satış Sözleşmesi', None), ('Ödeme Hizmetleri Çerçeve Sözleşmesi', None), ('Kurumsal İletişim Bilgileri', 'bilgi-toplumu-hizmetleri.html'),
]
def legal_doc_cards():
    cards = []
    for title, link in LEGAL_DOCS:
        if link:
            cards.append(f'<a class="doc-card reveal" href="{link}"><span>{title}</span><span class="doc-arrow">→</span></a>')
        else:
            cards.append(f'<button class="doc-card reveal" data-doc="{title}"><span>{title}</span><span class="doc-arrow">↗</span></button>')
    modal = '''<div class="bio-modal doc-modal" id="docModal"><div class="bio-modal-inner" style="text-align:left;max-width:640px">
      <button class="bio-close" aria-label="Kapat">×</button>
      <div class="doc-badge">''' + icon('file') + '''</div>
      <h3 id="docTitle"></h3>
      <p class="doc-note">Aşağıdaki metin, klon çalışması kapsamında hazırlanmış <strong>örnek</strong> bir belge özetidir.</p>
      <p>Bu belge; Moka United Ödeme Hizmetleri ve Elektronik Para Kuruluşu A.Ş.'nin ilgili mevzuat (6493 ve 6698 sayılı Kanunlar, TCMB ve MASAK düzenlemeleri) kapsamındaki yükümlülüklerini ve müşteri haklarını düzenler.</p>
      <p>Belgenin güncel ve tam sürümü için <a href="iletisim.html">iletişim</a> sayfasından bize ulaşabilir veya <strong>info@mokaunited.com</strong> adresine yazabilirsiniz.</p>
    </div></div>'''
    return '<section class="legal container" style="max-width:1100px"><div class="doc-grid">' + ''.join(cards) + '</div></section>' + modal

PAGES['yasal-belgeler-ve-temsilcilikler.html'] = shell(
  'Yasal Belgeler ve Temsilcilikler', 'Moka United yasal belgeleri ve temsilcilikleri.', '', '',
  breadcrumb([('Moka United','index.html'),('Yasal Belgeler ve Temsilcilikler',None)]) +
  page_title('YASAL BELGELER VE TEMSİLCİLİKLER') +
  legal_doc_cards())

PAGES['kvkk-aydinlatma-metni.html'] = legal_page(
  'kvkk-aydinlatma-metni.html', 'KVKK AYDINLATMA METNİ', '',
  '6698 sayılı Kanun kapsamında hazırlanan aydınlatma metni. (Örnek klon içeriği.)',
  [('Amaç',['Bu metin, kişisel verilerinizin hangi amaçlarla işlendiği konusunda sizi bilgilendirmek için hazırlanmıştır.']),
   ('İşlenen Veriler',['Kimlik, iletişim ve işlem güvenliği verileriniz hizmetin gerektirdiği ölçüde işlenir.']),
   ('Aktarım',['Verileriniz yasal yükümlülükler ve hizmet gereklilikleri çerçevesinde yetkili kurum ve iş ortaklarıyla paylaşılabilir.'])])

for fname, html in PAGES.items():
    with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f:
        f.write(html)
    print('yazıldı:', fname)
print(f'\nToplam {len(PAGES)} sayfa üretildi.')
