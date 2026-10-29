"""Aperçu des liens partagés (WhatsApp, réseaux sociaux, messageries) et référencement de la page d'accueil :
balises, données structurées, plan du site, robots.txt, icônes. Appelé par run.py (ne pas éditer public/).
L'image d'aperçu est pipeline/static/og.png (1200 × 630, sans chiffre ni sondage) ; pipeline/static/ est copié dans public/."""
import html, json, os, shutil

SITE = os.environ.get('SITE_URL', 'https://p2027.org').rstrip('/')
MOIS = {m: i + 1 for i, m in enumerate(['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'])}
FAVICON = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20'><rect width='10' height='20' fill='#0055a4'/><rect x='10' width='10' height='20' fill='#fff'/><rect x='20' width='10' height='20' fill='#ef4135'/></svg>"
TITLE = "Promesses 2027 : combien me coûtent leurs promesses ?"
DESC = ("Les programmes des candidats à la présidentielle 2027 chiffrés mesure par mesure, avec la même méthode pour tous "
        "et les sources à l'appui. Simulateur, quiz à l'aveugle, faisabilité.")
e = lambda s: html.escape(str(s), quote=True)

def iso(asof):
    d, m, y = asof.split()
    return f"{y}-{MOIS[m]:02d}-{int(d):02d}"

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'

def home_head(D):
    """Balises de l'accueil : description, adresse canonique, aperçu de partage (Open Graph, X/Twitter), icônes,
    données structurées (site et jeu de données ouvert)."""
    url, img = SITE + '/', SITE + '/og.png'
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Promesses 2027", "url": url, "inLanguage": "fr-FR", "description": DESC},
          {"@context": "https://schema.org", "@type": "Dataset", "name": "Promesses 2027 : chiffrage des programmes de la présidentielle",
           "description": "Mesures des 8 programmes de la présidentielle 2027, chiffrage (effet sur le solde public en 2030, en Md€), fourchettes, faisabilité, données d'entrée et sources.",
           "url": url, "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True, "inLanguage": "fr-FR",
           "dateModified": iso(D['asof']), "creator": {"@type": "Organization", "name": "Promesses 2027", "url": url},
           "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "/data/promesses-2027.json"}]}]
    return f'''<meta name="description" content="{e(DESC)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Promesses 2027">
<meta property="og:locale" content="fr_FR">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(TITLE)}">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:image" content="{img}">
<meta property="og:image:secure_url" content="{img}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(TITLE)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(TITLE)}">
<meta name="twitter:description" content="{e(DESC)}">
<meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#13203f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
''' + "\n".join(jsonld(x) for x in ld)

def write(D, root, here):
    pub = os.path.join(root, 'public')
    shutil.copytree(os.path.join(here, 'static'), pub, dirs_exist_ok=True)
    open(os.path.join(pub, 'favicon.svg'), 'w').write(FAVICON)
    open(os.path.join(pub, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'<url><loc>{SITE}/</loc><lastmod>{iso(D["asof"])}</lastmod></url>\n</urlset>\n')
    open(os.path.join(pub, 'robots.txt'), 'w').write(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE}/sitemap.xml\n")
