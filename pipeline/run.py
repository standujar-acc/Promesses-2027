"""Construit tout le site : corrections → données → app.
Usage : python3 pipeline/run.py
Sorties :
  public/index.html               site autonome (Cloudflare Pages ou tout hébergeur statique)
  public/data/promesses-2027.json données ouvertes
  lib/context.js                  contexte de l'assistant (fonction /api/ask)
  pipeline/promesses-2027.html    version artifact claude.ai (non versionnée)
"""
import json, os, runpy, re, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.chdir(HERE)
runpy.run_path('corrections.py', run_name='__main__')
runpy.run_path('build.py', run_name='__main__')
D = json.load(open('promesses-2027-data.json'))
art = open('promesses-2027.html').read()

# page web complète : <title> et polices dans <head>
head, body = art.split('<style>', 1)
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
open(os.path.join(ROOT, 'public', 'index.html'), 'w').write(page)
json.dump(D, open(os.path.join(ROOT, 'public', 'data', 'promesses-2027.json'), 'w'), ensure_ascii=False, indent=1)

# contexte de l'assistant, identique à celui de l'app
V = {'faisable': 'Faisable', 'sous_conditions': 'Sous conditions', 'tres_difficile': 'Très difficile', 'bloque': 'Exige une révision'}
TH = D['themes']
def md(n):
    s = f"{abs(n):.1f}".rstrip('0').rstrip('.').replace('.', ',')
    return ('+' if n > 0 else '−' if n < 0 else '') + s
has = lambda m: m.get('claude') and not m['claude'].get('exclude') and not m['claude'].get('nc')
parts = []
for c in D['candidates']:
    t = c['claude_total']
    lines = [f"## {c['name']} ({c['party']}) · notre total {md(t['sum'])} Md€/an en 2030 (fourchette {md(t['p10'])} à {md(t['p90'])}) · camp : {c['total']['claimed']} · non chiffré : {t.get('missing','')}"]
    for m in c['measures']:
        k = m.get('claude') or {}
        fig = f"{md(k['central'])} Md€/an ({md(k['low'])} à {md(k['high'])})" if has(m) else 'non chiffrable'
        lines.append(f"- [{c['id']}.{m['id']}] {m['title']} ({TH.get(m['theme'], m['theme'])}) : {m['proposal']} | camp : {m.get('claimed')} | notre chiffrage : {fig}{' | non confirmé en 2026, hors total' if m.get('a_confirmer') else ''} | verdict : {V[m['verdict']]} | {'chemin' if m['verdict']=='bloque' else 'obstacle'} : {m['obstacle']}")
    parts.append('\n'.join(lines))
ctx = '\n\n'.join(parts)
budget = ' ; '.join(f"{x['v']} {x['l']}" for x in D['context'])
open(os.path.join(ROOT, 'lib', 'context.js'), 'w').write(
    '// Généré par pipeline/run.py : ne pas modifier à la main.\n'
    f'export const CONTEXT = {json.dumps(ctx, ensure_ascii=False)};\n'
    f'export const BUDGET = {json.dumps(budget, ensure_ascii=False)};\n'
    f'export const ASOF = {json.dumps(D["asof"], ensure_ascii=False)};\n')
print('ok :', len(page)//1024, 'Ko ;', sum(len(c['measures']) for c in D['candidates']), 'mesures')
