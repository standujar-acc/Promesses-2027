"""Construit tout le site : corrections → données → app.
Usage : python3 pipeline/run.py
Sorties :
  public/index.html               site autonome (Cloudflare Pages ou tout hébergeur statique)
  public/data/promesses-2027.json données ouvertes
  pipeline/promesses-2027.html    version artifact claude.ai (non versionnée)
"""
import json, os, runpy, re, html, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.chdir(HERE)
runpy.run_path('corrections.py', run_name='__main__')
runpy.run_path('build.py', run_name='__main__')
D = json.load(open('promesses-2027-data.json'))
art = open('promesses-2027.html').read()

# page web complète : <title> et polices dans <head> ; polices servies par le site (pas d'appel à Google Fonts)
head, body = art.split('<style>', 1)
head = re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts\.(googleapis|gstatic)\.com[^>]*>\n?', '', head)
head += '<link rel="preload" href="fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>\n<style>' + open('fonts/fonts.css').read() + '</style>\n'
title = re.search(r'<title>(.*?)</title>', head).group(1)
desc = "Les programmes des candidats à la présidentielle 2027 chiffrés mesure par mesure, avec la même méthode pour tous et les sources à l'appui. Simulateur, quiz à l'aveugle, faisabilité."
page = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{head.strip()}
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)} : combien coûtent leurs promesses ?">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#13203f">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20'%3E%3Crect width='10' height='20' fill='%230055a4'/%3E%3Crect x='10' width='10' height='20' fill='%23fff'/%3E%3Crect x='20' width='10' height='20' fill='%23ef4135'/%3E%3C/svg%3E">
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
print('ok :', len(page)//1024, 'Ko ;', sum(len(c['measures']) for c in D['candidates']), 'mesures')
