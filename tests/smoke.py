"""Test de bout en bout de public/index.html (Playwright, Chromium).
Usage : python3 tests/smoke.py   (après python3 pipeline/run.py)
Vérifie : pas d'erreur JS, pas de débordement à 360 px (clair et sombre), navigation et retour,
équilibre du quiz (20 duels, 5 apparitions par candidat), simulateur sur une matrice de profils."""
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

    pg.evaluate("go('quiz')"); bad = 0; rep = 0
    for _ in range(50):
        pg.evaluate('quizStart()')
        qs = pg.evaluate('quizState.qs.map(q=>q.opts.map(o=>o.c))'); c = Counter(x for q in qs for x in q)
        if len(qs) != 20 or set(c.values()) != {5}: bad += 1
        txts = pg.evaluate('quizState.qs.flatMap(q=>q.opts.map(o=>(o.m.quiz_text||o.m.proposal).trim().toLowerCase()))')
        if len(set(txts)) < len(txts): rep += 1
    sans_effets = pg.evaluate("D.candidates.flatMap(c=>c.measures.filter(m=>!m.a_confirmer&&m.quiz_concret&&!(m.claude&&m.claude.exclude)&&!(m.quiz_plus&&m.quiz_moins)).map(m=>c.id+'.'+m.id))")
    check(not sans_effets, f'quiz : chaque proposition a ses deux effets {sans_effets[:3]}')
    check(bad == 0, f'quiz équilibré sur 50 tirages ({bad} écarts)')
    check(rep == 0, f'quiz : aucune proposition répétée dans une partie ({rep} parties sur 50)')

    pg.evaluate("go('moi')"); worst = 0
    for st in ('prive', 'public', 'enseignant', 'independant', 'chomage', 'minima', 'etudiant', 'retraite'):
        pg.evaluate(f"document.querySelector('#s-status [data-v=\"{st}\"]').click()")
        for sal in (0, 800, 1478, 2733, 5000):
            for kids in (0, 2, 4):
                pg.evaluate(f"S.kids={kids}; document.getElementById('s-salary').value={sal}; sim()")
                vals = pg.evaluate("[...document.querySelectorAll('#simres .srow .eur')].map(e=>+e.textContent.replace(/[^0-9−-]/g,'').replace('−','-')||0)")
                worst = max(worst, *[abs(v) for v in vals])
    check(worst < 1500, f'simulateur : aucun gain ou perte mensuel absurde (max {worst} €)')
    # chaque réglage du simulateur doit changer le résultat d'au moins un candidat, sans texte invalide
    SET = """(p)=>{ document.querySelector(`#s-status [data-v="${p.st}"]`).click(); document.querySelector(`#s-nat [data-v="${p.nat}"]`).click();
      S.kids=p.kids; S.wealth=p.w; S.inh=p.inh; const g=id=>document.getElementById(id);
      g('s-salary').value=p.sal; g('s-year').value=p.year; g('s-res').checked=p.lt5; g('s-baby').checked=true; g('s-energy').value=p.en; g('s-food').value=p.food; g('s-ot').checked=p.ot; g('s-cfe').value=p.cfe;
      openSim.clear(); D.candidates.forEach(c=>openSim.add(c.id)); sim(); return document.getElementById('simres').innerHTML; }"""
    base = dict(st='prive', nat='fr', kids=2, w=0, inh=0, sal=1800, year=1990, lt5=False, en=220, food=400, ot=False, cfe=250)
    starts = [base, dict(base, st='minima', sal=600, nat='hors'), dict(base, st='enseignant', sal=2400), dict(base, st='independant'), dict(base, st='retraite', year=1958, sal=1500)]
    grid = dict(st=['prive', 'public', 'chomage', 'minima', 'etudiant', 'retraite'], nat=['fr', 'ue', 'hors'], kids=[0, 3], sal=[0, 4500], year=[1960, 2005],
                w=[0, 100000000], inh=[0, 12000000], lt5=[False, True], ot=[False, True], en=[0, 400], food=[0, 800], cfe=[0, 2000])
    inert, invalid = [], 0
    for k, vals in grid.items():
        moved = False
        for s0 in starts:
            outs = {pg.evaluate(SET, dict(s0, **{k: v})) for v in vals}
            invalid += sum(1 for h in outs if any(x in h for x in ('NaN', 'undefined', 'Infinity')))
            moved = moved or len(outs) > 1
        if not moved: inert.append(k)
    check(not inert, f'simulateur : chaque réglage change au moins un résultat {inert}')
    # pas de saut brutal quand le salaire augmente de 100 € (effets de seuil), impôt des jeunes parents plafonné
    jumps = 0
    for st in ('prive', 'public', 'enseignant'):
        prev = None
        for sal in range(0, 8001, 100):
            h = pg.evaluate(SET, dict(base, st=st, sal=sal, kids=2))
            vals = pg.evaluate("[...document.querySelectorAll('#simres .srow .eur')].map(e=>+e.textContent.replace(/[^0-9−-]/g,'').replace('−','-')||0)")
            if prev: jumps = max(jumps, *[abs(a - b) for a, b in zip(vals, prev)])
            prev = vals
    check(jumps < 150, f'simulateur : pas de saut brutal pour +100 € de salaire (max {jumps} €)')
    check(invalid == 0, f'simulateur : aucun texte invalide (NaN, undefined) [{invalid}]')
    check(not errs, f'aucune erreur JS {errs[:1]}')
    b.close()
sys.exit(1 if fail else 0)
