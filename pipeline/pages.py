"""Partage et référencement : balises d'aperçu, une page HTML statique par candidat et pour la méthode,
plan du site et robots.txt. Appelé par run.py ; tout est régénéré à chaque passage (ne pas éditer public/).
Même gabarit pour les 8 candidats ; aucun sondage sur ces pages (pas de risque pendant les jours de silence)."""
import html, json, os, shutil

SITE = os.environ.get('SITE_URL', 'https://promesses-2027.pages.dev').rstrip('/')
MOIS = {m: i + 1 for i, m in enumerate(['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'])}
VERD = {'faisable': 'Faisable', 'sous_conditions': 'Sous conditions', 'tres_difficile': 'Très difficile', 'bloque': 'Exige une révision'}
LIFE = {'securite': 'Sécurité', 'sante': 'Santé', 'ecole': 'École', 'environnement': 'Environnement', 'logement': 'Logement',
        'libertes': 'Libertés', 'economie': 'Économie', 'rayonnement': 'Rayonnement'}
FAVICON = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20'><rect width='10' height='20' fill='#0055a4'/><rect x='10' width='10' height='20' fill='#fff'/><rect x='20' width='10' height='20' fill='#ef4135'/></svg>"
e = lambda s: html.escape(str(s), quote=True)

def iso(asof):
    d, m, y = asof.split()
    return f"{y}-{MOIS[m]:02d}-{int(d):02d}"

def md1(x):
    return ('+' if x > 0 else '−' if x < 0 else '') + f"{abs(x):.1f}".replace('.', ',')

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'

def meta(title, desc, path, image, alt):
    """Balises communes : description, adresse canonique, aperçu de partage (Open Graph, X/Twitter), icônes."""
    url, img = SITE + path, SITE + image
    return f'''<meta name="description" content="{e(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{e(url)}">
<meta property="og:site_name" content="Promesses 2027">
<meta property="og:locale" content="fr_FR">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(url)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(img)}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(img)}">
<meta name="theme-color" content="#13203f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">'''

HOME_TITLE = "Promesses 2027 : combien me coûtent leurs promesses ?"
HOME_DESC = ("Les programmes des candidats à la présidentielle 2027 chiffrés mesure par mesure, avec la même méthode pour tous "
             "et les sources à l'appui. Simulateur, quiz à l'aveugle, faisabilité.")

def home_head(D):
    """Balises de la page d'accueil (l'app) ; données structurées : site et jeu de données ouvert."""
    date = iso(D['asof'])
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Promesses 2027", "url": SITE + "/", "inLanguage": "fr-FR", "description": HOME_DESC},
          {"@context": "https://schema.org", "@type": "Dataset", "name": "Promesses 2027 : chiffrage des programmes de la présidentielle",
           "description": "Mesures des 8 programmes de la présidentielle 2027, chiffrage (effet sur le solde public en 2030, en Md€), fourchettes, faisabilité, données d'entrée et sources.",
           "url": SITE + "/methode/", "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True, "inLanguage": "fr-FR",
           "dateModified": date, "creator": {"@type": "Organization", "name": "Promesses 2027", "url": SITE + "/"},
           "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "/data/promesses-2027.json"}]}]
    return meta(HOME_TITLE, HOME_DESC, "/", "/og/index.png", "Promesses 2027 : combien me coûtent leurs promesses ?") + "\n" + "\n".join(jsonld(x) for x in ld)

CSS = """:root{--bg:#f2f3f7;--surface:#fff;--ink:#121521;--muted:#596074;--line:#dfe2ea;--accent:#2b4acb;--band:#13203f;--band-ink:#f4f6fb;--band-muted:#a9b3cf;--ok:#1b7a4b;--warn:#946400;--hard:#a04415;--bad:#b3263a;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0e1220;--surface:#161b2c;--ink:#e8ebf3;--muted:#a3abc2;--line:#283049;--accent:#8ea3ff;--ok:#5fcf95;--warn:#e2b54c;--hard:#ef8a55;--bad:#ff8a9a;color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.55 'IBM Plex Sans',system-ui,sans-serif}
a{color:var(--accent)}
.band{background:var(--band);color:var(--band-ink);border-left:10px solid;border-image:linear-gradient(#0055a4 33%,#fff 33% 66%,#ef4135 66%) 1}
.band .in,main,footer{max-width:900px;margin:0 auto;padding:0 16px}
.brand{display:inline-block;padding:14px 0;font:700 1.25rem/1 'Barlow Condensed',sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--band-ink);text-decoration:none}
.hero{padding:10px 0 26px}.hero .eyebrow{font:600 .75rem/1.3 'IBM Plex Sans',sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--band-muted)}
h1{margin:6px 0 10px;font:700 clamp(2.2rem,9vw,3.6rem)/.95 'Barlow Condensed',sans-serif;text-transform:uppercase}
.hero p{margin:0;color:#cdd4e6;max-width:70ch}
.total{margin-top:18px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}
.total b{font:700 2.4rem/1 'Barlow Condensed',sans-serif}.total span{color:var(--band-muted);font-size:.92rem}
.cta{display:inline-block;margin-top:18px;background:#ffd166;color:#13203f;font-weight:600;padding:10px 16px;border-radius:10px;text-decoration:none}
h2{margin:34px 0 10px;font:700 1.7rem/1.1 'Barlow Condensed',sans-serif;text-transform:uppercase}
h3{margin:0 0 4px;font-size:1.02rem}
.m{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:10px 0}
.m p{margin:4px 0}.m .k{font-size:.92rem;color:var(--muted)}.m .k b{color:var(--ink)}
.m .k .v-faisable{color:var(--ok)}.m .k .v-sous_conditions{color:var(--warn)}.m .k .v-tres_difficile{color:var(--hard)}.m .k .v-bloque{color:var(--bad)}
.th{margin:22px 0 4px;font:600 .78rem/1.3 'IBM Plex Sans',sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
ul{padding-left:20px}li{margin:4px 0}.small{font-size:.9rem;color:var(--muted)}
nav.c{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}nav.c a{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 12px;text-decoration:none;color:var(--ink);font-size:.92rem}
footer{padding:28px 16px 40px;color:var(--muted);font-size:.9rem}"""

def shell(title, desc, path, image, alt, body, ld):
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
{meta(title, desc, path, image, alt)}
{jsonld(ld)}
<link rel="preload" href="/fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>
<style>@font-face{{font-family:'IBM Plex Sans';font-weight:400 600;font-display:swap;src:url(/fonts/ibm-plex-sans.woff2) format('woff2')}}
@font-face{{font-family:'Barlow Condensed';font-weight:700;font-display:swap;src:url(/fonts/barlow-condensed-700.woff2) format('woff2')}}
{CSS}</style>
</head>
<body>
{body}
</body>
</html>
'''

def nav(D, cur=None):
    return '<nav class="c" aria-label="Candidats">' + ''.join(f'<a href="/candidats/{c["id"]}/"{" aria-current=\"page\"" if c["id"] == cur else ""}>{e(c["name"])}</a>' for c in D['candidates']) + '<a href="/methode/">Méthode</a></nav>'

def foot(D):
    return (f'<footer>Données à jour au {e(D["asof"])}. Site indépendant : aucun lien avec un parti, un candidat ou une équipe de campagne. '
            f'Même méthode pour tous les candidats ; code et données ouverts. <a href="/">Retour à l\'app</a> · <a href="/methode/">Méthode</a> · '
            f'<a href="/data/promesses-2027.json">Données (JSON)</a></footer>')

def amount(m):
    k = m['claude']
    if m.get('a_confirmer'): return 'À confirmer (non reconfirmée en 2026), hors total'
    if k.get('exclude'): return 'Compté dans une autre fiche (hors total)'
    if k.get('nc') or k.get('method') == 'nc': return 'Non chiffrable (paramètre clé non publié)'
    s = f'{md1(k["central"])} Md€ par an en 2030'
    if k['low'] != k['high']: s += f' (de {md1(k["low"])} à {md1(k["high"])})'
    return s + (', si la révision passe' if m['verdict'] == 'bloque' else '')

def cand_page(D, c):
    t, n = c['claude_total'], len(c['measures'])
    title = f"{c['name']} : son programme 2027 chiffré, mesure par mesure | Promesses 2027"
    desc = (f"Programme de {c['name']} ({c['party']}) chiffré mesure par mesure : {n} mesures, effet de {md1(t['sum'])} Md€ par an sur le déficit public en 2030, "
            "faisabilité et sources. Même méthode pour les 8 candidats.")
    themes = list(D['themes'])
    ms = sorted(c['measures'], key=lambda m: (themes.index(m['theme']) if m['theme'] in themes else 99, -abs(m['claude']['central'])))
    parts, last = [], None
    for m in ms:
        if m['theme'] != last:
            parts.append(f'<p class="th">{e(D["themes"].get(m["theme"], m["theme"]))}</p>'); last = m['theme']
        parts.append(f'<article class="m"><h3>{e(m["title"])}</h3><p>{e(m["proposal"])}</p>'
                     f'<p class="k">Notre chiffrage : <b>{e(amount(m))}</b> · Faisabilité : <b class="v-{e(m["verdict"])}">{e(VERD.get(m["verdict"], m["verdict"]))}</b></p>'
                     + (f'<p class="k">{e(m["obstacle"])}</p>' if m.get('obstacle') else '') + '</article>')
    life = []
    for th in (D.get('life') or {}).get(c['id'], []):
        if not th['proposals']: continue
        items = ''.join(f'<li>{e(p["text"])}<span class="small"> · {"précis" if p["verifiable"] else "intention"}{" · programme 2022, non reconfirmé" if p.get("old") else ""}</span></li>' for p in th['proposals'])
        life.append(f'<p class="th">{e(LIFE.get(th["theme"], th["theme"]))}</p><ul>{items}</ul>' + (f'<p class="small">Ce que disent les études : {e(th["evidence"])}</p>' if th.get('evidence') else ''))
    real = f' ; sans les mesures qui exigent une révision : {md1(t["realsum"])} Md€' if t.get('realsum') is not None and abs(t['realsum'] - t['sum']) >= 0.05 else ''
    body = f'''<header class="band"><div class="in"><a class="brand" href="/">Promesses 2027</a>
<div class="hero"><div class="eyebrow">Présidentielle 2027 · {e(c['party'])}</div><h1>{e(c['name'])}</h1><p>{e(c['summary'])}</p>
<div class="total"><b>{md1(t['sum'])} Md€</b><span>par an sur le solde public en 2030, si tout passe ; fourchette probable de {md1(t['p10'])} à {md1(t['p90'])}{e(real)}</span></div>
<a class="cta" href="/#{e(c['id'])}">Ouvrir la fiche interactive : simulateur, quiz, sources</a></div></div></header>
<main>{nav(D, c['id'])}
<h2>Mesures chiffrées ({n})</h2>
<p class="small">Effet de chaque mesure sur le solde public, en milliards d'euros par an en 2030 (+ améliore le solde, − le dégrade). Le détail des calculs et toutes les sources sont dans la fiche interactive.</p>
{''.join(parts)}
{'<h2>Vie quotidienne</h2>' + ''.join(life) if life else ''}
{f'<h2>Non compté</h2><p class="small">{e(t["missing"])}</p>' if t.get('missing') else ''}
{nav(D, c['id'])}</main>
{foot(D)}'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": f"{SITE}/candidats/{c['id']}/", "inLanguage": "fr-FR",
          "dateModified": iso(D['asof']), "about": {"@type": "Person", "name": c['name']},
          "isPartOf": {"@type": "WebSite", "name": "Promesses 2027", "url": SITE + "/"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Promesses 2027", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": c['name'], "item": f"{SITE}/candidats/{c['id']}/"}]}}
    return shell(title, desc, f"/candidats/{c['id']}/", f"/og/{c['id']}.png", f"{c['name']} : son programme chiffré mesure par mesure", body, ld)

def method_page(D):
    title = "Méthode : comment nous chiffrons les programmes de la présidentielle 2027 | Promesses 2027"
    desc = "Règles communes, sources, verdicts de faisabilité, ce qui n'est pas compté : la méthode appliquée à l'identique aux 8 candidats."
    body = f'''<header class="band"><div class="in"><a class="brand" href="/">Promesses 2027</a>
<div class="hero"><div class="eyebrow">Méthode</div><h1>Comment nous chiffrons</h1><p>{e(desc)}</p>
<a class="cta" href="/">Ouvrir l'app</a></div></div></header>
<main>{nav(D)}{''.join(f"<p>{p}</p>" for p in D['method'])}</main>
{foot(D)}'''
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": SITE + "/methode/", "inLanguage": "fr-FR", "dateModified": iso(D['asof'])}
    return shell(title, desc, "/methode/", "/og/index.png", "Promesses 2027 : la méthode", body, ld)

def write(D, root, here):
    pub = os.path.join(root, 'public')
    missing = [c['id'] for c in D['candidates'] if not os.path.exists(os.path.join(here, 'static', 'og', c['id'] + '.png'))]
    assert not missing, f"Image de partage manquante pour {missing} : lancez python3 pipeline/og.py"
    for d in ('og', 'candidats', 'methode'): shutil.rmtree(os.path.join(pub, d), ignore_errors=True)
    shutil.copytree(os.path.join(here, 'static'), pub, dirs_exist_ok=True)
    open(os.path.join(pub, 'favicon.svg'), 'w').write(FAVICON)
    for c in D['candidates']:
        os.makedirs(os.path.join(pub, 'candidats', c['id']), exist_ok=True)
        open(os.path.join(pub, 'candidats', c['id'], 'index.html'), 'w').write(cand_page(D, c))
    os.makedirs(os.path.join(pub, 'methode'), exist_ok=True)
    open(os.path.join(pub, 'methode', 'index.html'), 'w').write(method_page(D))
    date = iso(D['asof'])
    urls = ['/', '/methode/'] + [f"/candidats/{c['id']}/" for c in D['candidates']]
    open(os.path.join(pub, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{date}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    open(os.path.join(pub, 'robots.txt'), 'w').write(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE}/sitemap.xml\n")
