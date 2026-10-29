"""Images d'aperçu pour le partage des liens (1200 × 630) et icônes, à lancer à la main quand la liste
des candidats ou le visuel change : python3 pipeline/og.py (Playwright + Chromium).
Sorties dans pipeline/static/ (copiées dans public/ par run.py) : og/index.png, og/<candidat>.png,
apple-touch-icon.png. Aucun chiffre sur les images : elles ne vieillissent pas avec les totaux.
Même gabarit pour les 8 candidats (nom, parti, même phrase)."""
import json, os, html, tempfile
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'static'); os.makedirs(os.path.join(OUT, 'og'), exist_ok=True)
D = json.load(open(os.path.join(HERE, '..', 'public', 'data', 'promesses-2027.json')))
F = 'file://' + os.path.join(HERE, 'fonts')
FONTS = f"""@font-face{{font-family:'Barlow Condensed';font-weight:700;src:url({F}/barlow-condensed-700.woff2) format('woff2')}}
@font-face{{font-family:'IBM Plex Sans';font-weight:400 600;src:url({F}/ibm-plex-sans.woff2) format('woff2')}}"""
CSS = FONTS + """
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#13203f;color:#f4f6fb;font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden}
.flag{position:absolute;left:0;top:0;bottom:0;width:22px;display:flex;flex-direction:column}
.flag i{flex:1}.flag i:nth-child(1){background:#0055a4}.flag i:nth-child(2){background:#fff}.flag i:nth-child(3){background:#ef4135}
.glow{position:absolute;right:-180px;top:-220px;width:720px;height:720px;border-radius:50%;background:radial-gradient(closest-side,rgba(43,74,203,.45),rgba(19,32,63,0))}
.wrap{position:absolute;left:92px;right:80px;top:64px;bottom:58px;display:flex;flex-direction:column}
.brand{font:700 34px/1 'Barlow Condensed';letter-spacing:.06em;text-transform:uppercase;color:#f4f6fb}
.eyebrow{margin-top:54px;font:600 24px/1.2 'IBM Plex Sans';letter-spacing:.12em;text-transform:uppercase;color:#a9b3cf}
h1{margin-top:14px;font:700 112px/.92 'Barlow Condensed';text-transform:uppercase;letter-spacing:.005em}
h1 em{font-style:normal;color:#ffd166}
p{margin-top:28px;font:400 31px/1.35 'IBM Plex Sans';color:#cdd4e6;max-width:960px}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font:600 24px/1 'IBM Plex Sans';color:#a9b3cf}
.chips{display:flex;gap:12px}.chips span{border:1.5px solid rgba(255,255,255,.22);border-radius:999px;padding:10px 18px;color:#f4f6fb}
"""
def card(eyebrow, title, text):
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="flag"><i></i><i></i><i></i></div><div class="glow"></div>
<div class="wrap"><div class="brand">Promesses 2027</div><div class="eyebrow">{html.escape(eyebrow)}</div><h1>{title}</h1><p>{html.escape(text)}</p>
<div class="foot"><div class="chips"><span>Chiffrage</span><span>Faisabilité</span><span>Simulateur</span><span>Quiz à l'aveugle</span></div><div>promesses-2027.pages.dev</div></div></div></body></html>"""

CARDS = {'index': card("Présidentielle 2027 · 8 candidats", "Combien me coûtent <em>leurs promesses</em> ?",
                        "Les programmes chiffrés mesure par mesure, avec la même méthode pour tous et les sources à l'appui.")}
for c in D['candidates']:
    CARDS[c['id']] = card(f"Présidentielle 2027 · {c['party']}", html.escape(c['name']),
                          "Son programme chiffré mesure par mesure : coût, faisabilité, sources. Même méthode pour les 8 candidats.")
ICON = """<!doctype html><html><head><style>*{margin:0}body{width:180px;height:180px;display:flex}i{flex:1}</style></head>
<body><i style="background:#0055a4"></i><i style="background:#fff"></i><i style="background:#ef4135"></i></body></html>"""

with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
    b = p.chromium.launch()
    def shot(doc, path, w, h):
        f = os.path.join(tmp, 'c.html'); open(f, 'w').write(doc)
        pg = b.new_page(viewport={'width': w, 'height': h}); pg.goto('file://' + f); pg.wait_for_timeout(300)
        pg.evaluate("document.fonts.ready"); pg.screenshot(path=path); pg.close()
    for k, doc in CARDS.items():
        shot(doc, os.path.join(OUT, 'og', k + '.png'), 1200, 630)
    shot(ICON, os.path.join(OUT, 'apple-touch-icon.png'), 180, 180)
    b.close()
print('ok :', len(CARDS), 'images')
