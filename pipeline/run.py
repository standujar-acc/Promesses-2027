"""Construit tout le site : corrections → données → app.
Usage : python3 pipeline/run.py
Sorties :
  public/index.html               site autonome (Cloudflare Pages ou tout hébergeur statique)
  public/data/promesses-2027.json données ouvertes
  public/og.png, sitemap.xml, robots.txt  aperçu des liens partagés, référencement (pipeline/pages.py)
  pipeline/promesses-2027.html    version artifact claude.ai (non versionnée)
"""
import json, os, runpy, re, html, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.chdir(HERE)
runpy.run_path('corrections.py', run_name='__main__')
runpy.run_path('build.py', run_name='__main__')
D = json.load(open('promesses-2027-data.json'))
# textes publiés (fiches, notes, obstacles, résumés, simulateur, Vie quotidienne, quiz, méthode) : aucune note de travail
# (arbitrage présenté comme non tranché, consigne de correction, identifiant du registre : ils vont dans pipeline/data/suivi.json)
NOTE_TRAVAIL = re.compile(r"[àa] trancher|verdict proposé|retirer «|corriger le simulateur|à signaler|à aligner sur|\bS\d{3}\b|\bsim\.[a-z_]+|\b[a-z]+_[a-z_]+ = \d", re.I)
def _textes(o, chemin):
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in ('url', 'u'): yield from _textes(v, chemin + '.' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from _textes(v, f'{chemin}[{i}]')
    elif isinstance(o, str):
        yield chemin, o
_notes = [(c, m.group(0)) for cle in ('candidates', 'life', 'quiz_extra', 'method') for c, s in _textes(D[cle], cle) for m in [NOTE_TRAVAIL.search(s)] if m]
assert not _notes, "note de travail dans un texte publié : " + " ; ".join(f"{c} ({g})" for c, g in _notes[:10])
art = open('promesses-2027.html').read()

# page web complète : <title> et polices dans <head> ; polices servies par le site (pas d'appel à Google Fonts)
head, body = art.split('<style>', 1)
head = re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts\.(googleapis|gstatic)\.com[^>]*>\n?', '', head)
head += '<link rel="preload" href="fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>\n<style>' + open('fonts/fonts.css').read() + '</style>\n'
# titre et balises de partage / référencement : pipeline/pages.py
import pages
head = re.sub(r'<title>.*?</title>', '<title>' + html.escape(pages.TITLE) + '</title>', head)
page = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{head.strip()}
{pages.home_head(D)}
</head>
<body>
<style>{body}
</body>
</html>
'''
os.makedirs(os.path.join(ROOT, 'public', 'data'), exist_ok=True)
shutil.rmtree(os.path.join(ROOT, 'public', 'fonts'), ignore_errors=True)
shutil.copytree('fonts', os.path.join(ROOT, 'public', 'fonts'), ignore=shutil.ignore_patterns('fonts.css'))
open(os.path.join(ROOT, 'public', 'index.html'), 'w').write(page)
json.dump(D, open(os.path.join(ROOT, 'public', 'data', 'promesses-2027.json'), 'w'), ensure_ascii=False, indent=1)
# image d'aperçu des liens partagés, icônes, plan du site, robots.txt, en-têtes (pipeline/static/)
pages.write(D, ROOT, HERE)

# README : date et tableau des totaux, régénérés à chaque passage
def fr(x, sign=True):
    s = f"{abs(x):.1f}".replace('.', ',')
    return ('+' if x > 0 else '−' if x < 0 else '') + s if sign else s
rows = [f"| {c['name']} | {c['party']} | {c['claude_total']['n']} | {fr(c['claude_total']['sum'])} | {fr(c['claude_total']['p10'])} à {fr(c['claude_total']['p90'])} |" for c in D['candidates']]
tab = (f"Données à jour au {D['asof']} : {len(D['candidates'])} candidats, {sum(len(c['measures']) for c in D['candidates'])} mesures.\n\n"
       "| Candidat | Parti | Mesures chiffrées | Effet sur le déficit en 2030 (Md€/an) | Fourchette à 80 % |\n| --- | --- | --- | --- | --- |\n" + "\n".join(rows))
rp = os.path.join(ROOT, 'README.md'); rd = open(rp).read()
rd = re.sub(r"(<!-- totaux:debut[^>]*-->\n).*?(<!-- totaux:fin -->)", lambda m: m.group(1) + tab + "\n" + m.group(2), rd, flags=re.S)
open(rp, 'w').write(rd)
# METHODOLOGIE.md : même texte que l'onglet « Méthode », régénéré à chaque passage
md = lambda s: html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'</?b>', '**', s)))
open(os.path.join(ROOT, 'METHODOLOGIE.md'), 'w').write("# Méthode\n\nTexte identique à l'onglet « Méthode » de l'app, généré par `pipeline/run.py` depuis `pipeline/build.py`, à jour au "
    + D['asof'] + ".\n\n" + "\n\n".join(md(p) for p in D['method']) + "\n")
print('ok :', len(page)//1024, 'Ko ;', sum(len(c['measures']) for c in D['candidates']), 'mesures')
