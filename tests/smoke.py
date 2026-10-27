"""Test de bout en bout de public/index.html (Playwright, Chromium).
Usage : python3 tests/smoke.py   (après python3 pipeline/run.py)
Vérifie : pas d'erreur JS, pas de débordement à 360 px (clair et sombre), navigation et retour,
équilibre du quiz (16 duels, 4 apparitions par candidat), simulateur sur une matrice de profils."""
import os, sys
from collections import Counter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(ROOT, 'public', 'index.html')
fail = []
def check(ok, msg):
    print(('ok   ' if ok else 'ÉCHEC'), msg)
    if not ok: fail.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ('light', 'dark'):
        pg = b.new_page(viewport={'width': 360, 'height': 800}, color_scheme=scheme); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(400)
        for v in ('accueil', 'cand', 'moi', 'quiz', 'methode'):
            pg.evaluate(f"go('{v}')"); pg.wait_for_timeout(80)
            check(pg.evaluate('document.documentElement.scrollWidth') <= 360, f'{scheme} · {v} : pas de débordement horizontal')
        check(not errs, f'{scheme} : aucune erreur JS {errs[:1]}')
        pg.close()

    pg = b.new_page(viewport={'width': 390, 'height': 844}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(300)
    pg.click('nav.bottom [data-go="moi"]'); pg.click('nav.bottom [data-go="quiz"]'); pg.go_back(); pg.wait_for_timeout(150)
    check(pg.evaluate('view') == 'moi', 'retour arrière : revient à la vue précédente')

    pg.evaluate("go('quiz')"); bad = 0
    for _ in range(50):
        pg.evaluate('quizStart()')
        qs = pg.evaluate('quizState.qs.map(q=>q.opts.map(o=>o.c))'); c = Counter(x for q in qs for x in q)
        if len(qs) != 16 or set(c.values()) != {4}: bad += 1
    check(bad == 0, f'quiz équilibré sur 50 tirages ({bad} écarts)')

    pg.evaluate("go('moi')"); worst = 0
    for st in ('prive', 'public', 'enseignant', 'independant', 'chomage', 'minima', 'etudiant', 'retraite'):
        pg.evaluate(f"document.querySelector('#s-status [data-v=\"{st}\"]').click()")
        for sal in (0, 800, 1478, 2733, 5000):
            for kids in (0, 2, 4):
                pg.evaluate(f"S.kids={kids}; document.getElementById('s-salary').value={sal}; sim()")
                vals = pg.evaluate("[...document.querySelectorAll('#simres .srow .eur')].map(e=>+e.textContent.replace(/[^0-9−-]/g,'').replace('−','-')||0)")
                worst = max(worst, *[abs(v) for v in vals])
    check(worst < 1500, f'simulateur : aucun gain ou perte mensuel absurde (max {worst} €)')
    check(not errs, f'aucune erreur JS {errs[:1]}')
    b.close()
sys.exit(1 if fail else 0)
