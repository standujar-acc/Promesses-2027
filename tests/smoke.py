"""Test de bout en bout de public/index.html (Playwright, Chromium).
Usage : python3 tests/smoke.py   (après python3 pipeline/run.py)
Vérifie : pas d'erreur JS, pas de débordement à 360 px (clair et sombre), navigation et retour,
équilibre du quiz (20 duels, 5 apparitions par candidat), simulateur sur une matrice de profils."""
import os, re, sys
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
    sans_effets = pg.evaluate("D.candidates.flatMap(c=>c.measures.filter(m=>!m.a_confirmer&&m.quiz_concret&&!(m.claude&&m.claude.exclude)&&!(m.quiz_plus&&m.quiz_moins)).map(m=>c.id+'.'+m.id)).concat((D.quiz_extra||[]).filter(m=>!(m.quiz_plus&&m.quiz_moins&&m.quiz_concret)).map(m=>m.c+'.'+m.id))")
    check(not sans_effets, f'quiz : chaque proposition a ses deux effets {sans_effets[:3]}')
    sans_preuve = pg.evaluate("D.candidates.flatMap(c=>c.measures.filter(m=>!m.a_confirmer&&m.quiz_concret&&!(m.claude&&m.claude.exclude)).map(m=>({k:c.id+'.'+m.id,m}))).concat((D.quiz_extra||[]).map(m=>({k:m.c+'.'+m.id,m}))).filter(({m})=>!(m.quiz_preuve_pour&&m.quiz_preuve_contre&&m.quiz_cas_pour&&m.quiz_cas_contre)).map(x=>x.k)")
    check(not sans_preuve, f'quiz : chaque proposition a son Pour et son Contre avec niveau de preuve et cas réels {sans_preuve[:3]}')
    check(bad == 0, f'quiz équilibré sur 50 tirages ({bad} écarts)')
    check(rep == 0, f'quiz : aucune proposition répétée dans une partie ({rep} parties sur 50)')
    # thèmes choisis à l'accueil : plus de duels sur ces thèmes, sans casser l'équilibre entre candidats
    pg.evaluate("quizIntro()")
    check(pg.evaluate("document.querySelectorAll('.qchips button').length===quizThemes().length && quizThemes().length>=5"), "quiz : accueil, un bouton par thème jouable")
    share = lambda: pg.evaluate("quizState.qs.filter(q=>quizImp.has(q.t)).length")
    priL = pg.evaluate("['ecole','sante','logement'].filter(t=>quizThemes().includes(t))"); pri = priL or ['energie', 'institutions']
    pg.evaluate(f"quizImp.clear(); {pri}.forEach(t=>quizImp.add(t))"); bad = 0; n_pri = 0
    for _ in range(30):
        pg.evaluate('quizStart()'); qs = pg.evaluate('quizState.qs.map(q=>q.opts.map(o=>o.c))'); c = Counter(x for q in qs for x in q)
        if len(qs) != 20 or set(c.values()) != {5}: bad += 1
        n_pri += share()
    pg.evaluate("quizImp.clear()"); n_base = 0
    for _ in range(30):
        pg.evaluate('quizStart()'); pg.evaluate(f"{pri}.forEach(t=>quizImp.add(t))"); n_base += share(); pg.evaluate("quizImp.clear()")
    check(bad == 0 and n_pri > n_base, f'quiz : thèmes choisis plus présents ({n_pri} contre {n_base} duels sur 30 parties), équilibre gardé ({bad} écarts)')

    # duel : constat, Pour / Contre avec preuve, volet dépliable avec les cas et des sources numérotées valides
    pg.evaluate('quizStart()')
    r = pg.evaluate("""()=>{ const q=quizState.qs[0], el=document.getElementById('v-quiz');
      return {pv:el.querySelectorAll('.duel .pv').length, cases:el.querySelectorAll('.qsrc .qx li.qc2').length,
        want:q.opts.reduce((t,o)=>t+o.m.quiz_cas_pour.length+o.m.quiz_cas_contre.length+(o.m.quiz_complement?1:0),0),
        refs:[...el.querySelectorAll('.qsrc .qx li a')].every(a=>/^https?:/.test(a.getAttribute('href'))), w:document.documentElement.scrollWidth}; }""")
    check(r['pv'] == 4 and r['cases'] == r['want'] and r['refs'] and r['w'] <= 390, f"quiz : duel avec niveaux de preuve et cas réels dépliables ({r['pv']} preuves, {r['cases']}/{r['want']} cas)")
    # résultat du quiz : ce qui est affiché est ce qui est compté ; égalités jamais départagées ; thème marqué compté double
    pg.set_viewport_size({'width': 360, 'height': 800})
    def play(seq):
        pg.evaluate('quizStart()')
        for i in range(20):
            pg.click(f'#v-quiz [data-k="{seq(i)}"]')
    DU = "quizScore(quizState).duels.map(d=>({t:d.t,o:d.opts.map(o=>[o.c,o.k])}))"
    def expected(duels, imp):
        acc, w = Counter(), Counter()
        for d in duels:
            for c, k in d['o']:
                x = 2 if d['t'] in imp else 1
                w[c] += x; acc[c] += x * (k in ('pick', 'both'))
        return {c: acc[c] / w[c] for c in w}
    STATE = """()=>{ const R=quizScore(quizState), rows=R.rows, v=r=>r.x.acc/r.x.w;
      return {dots:[...document.querySelectorAll('.qc .qdots')].map(e=>e.children.length), ws:rows.map(r=>r.x.a), rings:document.querySelectorAll('.qc .qdots .x2').length, nstar:quizScore(quizState).duels.filter(d=>quizImp.has(d.t)).length*2, v:Object.fromEntries(rows.map(r=>[r.c.id,v(r)])),
        nums:[...document.querySelectorAll('.qc .num')].map(e=>e.textContent), fr:rows.map(r=>r.x.acc+'/'+r.x.w),
        sorted:rows.every((r,i)=>!i||v(rows[i-1])>=v(r)), duels:document.querySelectorAll('.qdet .qd').length,
        cards:[...document.querySelectorAll('[data-cand]')].map(b=>b.dataset.cand), near:R.near.map(r=>r.c.id),
        g1:R.groups[0].map(r=>r.c.id), g1acc:R.groups[0][0].x.acc, head:R.head, then:R.then,
        headIn:R.near.length===0||R.near.some(r=>R.head.includes(r.c.short)), shorts:Object.fromEntries(D.candidates.map(c=>[c.id,c.short])),
        ok:[...document.querySelectorAll('[data-cand]')].every(b=>b.closest('.card').querySelectorAll('.results button').length===rows.find(r=>r.c.id===b.dataset.cand).x.a),
        txt:document.getElementById('v-quiz').innerText, w:document.documentElement.scrollWidth}; }"""
    play(lambda i: ["0", "1", "both", "none", "0"][i % 5]); r = pg.evaluate(STATE); ex = expected(pg.evaluate(DU), set())
    check(r['dots'] == r['ws'] and r['nums'] == r['fr'] and r['sorted'] and all(abs(r['v'][c] - ex[c]) < 1e-9 for c in ex),
          'quiz résultat : une pastille par proposition vue, chiffre et classement identiques au calcul')
    check(r['duels'] == 20 and r['cards'] == r['near'] and r['ok'] and r['headIn'] and not re.search(r'undefined|NaN', r['txt']),
          'quiz résultat : détail des 20 duels ; cartes des plus proches cohérentes avec le titre')
    check(r['w'] <= 360, 'quiz résultat : pas de débordement à 360 px')
    t = pg.evaluate("document.querySelector('.star').dataset.t"); pg.click('.star >> nth=0'); r2 = pg.evaluate(STATE); ex2 = expected(pg.evaluate(DU), {t})
    check(pg.evaluate(f"document.querySelector('.star[data-t=\"{t}\"]').getAttribute('aria-pressed')") == 'true' and all(abs(r2['v'][c] - ex2[c]) < 1e-9 for c in ex2)
          and r2['dots'] == r2['ws'] and r2['rings'] == r2['nstar'] and pg.evaluate("document.getElementById('quiz-live').textContent.startsWith('Classement recalculé')"),
          'quiz résultat : un thème marqué compte double (pastilles cerclées, annonce pour lecteur d\'écran)')
    pg.click('.star >> nth=0'); pg.evaluate('quizImp.clear()')
    # égalités : tout « Les deux » → personne ne se détache, aucune carte choisie par l'ordre ; tout « Aucune » → rien de retenu
    play(lambda i: 'both'); r = pg.evaluate(STATE)
    check(r['head'] == 'Aucun candidat ne se détache' and not r['cards'], 'quiz résultat : égalité générale, aucun candidat mis en avant')
    play(lambda i: 'none'); r = pg.evaluate(STATE)
    check(r['head'] == 'Aucune proposition retenue' and not r['cards'] and 'Aucun effet sur le déficit' in r['txt'], 'quiz résultat : aucune proposition retenue')
    # parties au hasard : le titre nomme un candidat qui a des propositions retenues ; « puis » = groupe suivant ; égalités en tête jamais tranchées
    import random as _r; _r.seed(5); bad = []
    for n in range(25):
        play(lambda i: _r.choice(['0', '1', 'both', 'none', 'none'])); r = pg.evaluate(STATE)
        if r['g1acc'] > 0 and len(r['g1']) > 1 and len(r['g1']) <= 3 and set(r['cards']) != set(r['g1']): bad.append(('égalité', r['head']))
        if r['g1acc'] > 0 and len(r['g1']) == 1 and r['shorts'][r['g1'][0]] not in r['head']: bad.append(('titre', r['head']))
    check(not bad, f'quiz résultat : titres et cartes sans départage arbitraire sur 25 parties {bad[:2]}')
    pg.evaluate("navigator.clipboard.writeText=t=>{window._cp=t;return Promise.resolve()}"); pg.click('#quiz-copy'); cp = pg.evaluate('window._cp')
    check(cp.startswith('Mon quiz Promesses 2027 — ') and ('déficit :' not in cp) and not re.search(r'de [AEIOUÉ]', cp.split('—')[1].split('.')[0]),
          f'quiz résultat : texte copié fidèle à la page ({cp[:90]})')
    pg.set_viewport_size({'width': 390, 'height': 844})
    if priL:
        pg.evaluate(f"{priL}.forEach(t=>quizImp.add(t)); quizStart()")
        for i in range(20):
            pg.click(f'#v-quiz [data-k="{["0", "1", "both"][i % 3]}"]')
        check(pg.evaluate("document.querySelectorAll('.qdet [data-life]').length>0 && !/undefined|NaN/.test(document.getElementById('v-quiz').innerText)"),
              'quiz résultat : propositions « vie quotidienne » affichées, sans verdict ni coût')
        pg.evaluate("quizImp.clear()")

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
