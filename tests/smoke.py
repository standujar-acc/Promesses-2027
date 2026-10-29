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

    # ordinateur : page large en colonnes (fiches sur deux colonnes, colonne latérale fixe, simulateur à deux colonnes, sommaire de la méthode), sans débordement
    for W in (1100, 1440, 1920):
        pg = b.new_page(viewport={'width': W, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(300)
        for v in ('accueil', 'cand', 'moi', 'quiz', 'methode'):
            pg.evaluate(f"go('{v}')"); pg.wait_for_timeout(60)
            check(pg.evaluate('document.documentElement.scrollWidth') <= W, f'ordinateur {W} px · {v} : pas de débordement horizontal')
        r = pg.evaluate("""(()=>{ go('cand'); const cols=getComputedStyle(document.getElementById('measures')).gridTemplateColumns.split(' ').length;
          const side=getComputedStyle(document.getElementById('picker')).gridTemplateColumns.split(' ').length; go('moi'); const sim=getComputedStyle(document.querySelector('.sim-grid')).gridTemplateColumns.split(' ').length;
          go('methode'); const toc=document.querySelector('.met-toc').offsetParent!==null; go('accueil'); const cta=getComputedStyle(document.querySelector('.home-top')).display;
          return [cols, side, sim, toc, cta]; })()""")
        check(r == [3, 8, 2, True, 'grid'], f'ordinateur {W} px : fiches sur 3 colonnes, 8 candidats sur une ligne, simulateur en 2 colonnes, sommaire, accueil en grille {r}')
        # page candidat : le total reste à la même place quand on passe à « Vie quotidienne » ; barre (candidats + onglets) fixe en haut au défilement
        r = pg.evaluate("""(()=>{ go('cand'); window.scrollTo(0,0); const t=()=>document.getElementById('total').getBoundingClientRect().top;
          document.querySelector('#ftab [data-t="budget"]').click(); const a=t(); document.querySelector('#ftab [data-t="vie"]').click(); const v=document.getElementById('total').offsetParent!==null, b=t();
          document.querySelector('#ftab [data-t="budget"]').click(); window.scrollTo(0,1500); const bar=document.getElementById('cand-bar').getBoundingClientRect().top;
          const stuck=getComputedStyle(document.getElementById('cand-bar')).position; window.scrollTo(0,0); return [v, Math.abs(a-b)<1, stuck, Math.abs(bar)<1]; })()""")
        check(r == [True, True, 'sticky', True], f'ordinateur {W} px : total affiché et immobile entre Budget et Vie quotidienne, barre des candidats fixe {r}')
        # résultat du quiz : « Par candidat » et « Par thème » côte à côte, « ce qui colle » et « ce qui colle moins » côte à côte
        r = pg.evaluate("""(()=>{ go('quiz'); quizStart(); for(let i=0;i<20;i++){ const k=quizState.qs[quizState.i].opts.findIndex(o=>o.c==='le-pen'); document.querySelector(`#v-quiz [data-k="${k>=0?k:'none'}"]`).click(); }
          const g=document.querySelector('.qgrid'), n=document.querySelector('.qnear'); const out=[g?getComputedStyle(g).gridTemplateColumns.split(' ').length:0, n?getComputedStyle(n).gridTemplateColumns.split(' ').length:0, document.documentElement.scrollWidth<=innerWidth];
          quizState=null; go('accueil'); return out; })()""")
        check(r == [2, 2, True], f'ordinateur {W} px : résultat du quiz sur deux colonnes, sans débordement {r}')
        check(not errs, f'ordinateur {W} px : aucune erreur JS {errs[:1]}')
        pg.close()
    # mobile : les enveloppes de mise en page sont transparentes
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    pg.goto(URL); pg.wait_for_timeout(300)
    r = pg.evaluate("[...document.querySelectorAll('.home-top,.sim-grid,.sim-in,.sim-out')].map(e=>getComputedStyle(e).display).every(d=>d==='contents') && getComputedStyle(document.querySelector('.met-toc')).display==='none'")
    check(r, 'mobile : mise en page en une colonne (enveloppes transparentes, pas de sommaire)')
    r = pg.evaluate("""(()=>{ go('cand'); const y=id=>document.getElementById(id).getBoundingClientRect().top; const ord=[y('picker')<y('fhead'), y('fhead')<y('ftab'), y('ftab')<y('total')];
      document.querySelector('#ftab [data-t="vie"]').click(); const hid=document.getElementById('total').offsetParent===null; document.querySelector('#ftab [data-t="budget"]').click(); return [...ord, hid]; })()""")
    check(r == [True, True, True, True], f'mobile : page candidat dans le même ordre (candidats, présentation, onglets, total), total masqué dans « Vie quotidienne » {r}')
    r = pg.evaluate("""(()=>{ go('cand'); const p=document.getElementById('picker'), cs=getComputedStyle(p); window.scrollTo(0,2000);
      const top=p.getBoundingClientRect().top, b=p.querySelector('[data-id="zemmour"]'); b.click(); const sel=p.querySelector('[aria-pressed="true"]').getBoundingClientRect(), pr=p.getBoundingClientRect();
      const out=[cs.position, cs.flexWrap, Math.abs(top)<1, sel.left>=pr.left-1 && sel.right<=pr.right+1, window.scrollY<2000, document.documentElement.scrollWidth<=innerWidth]; window.scrollTo(0,0); return out; })()""")
    check(r == ['sticky', 'nowrap', True, True, True, True], f'mobile : bande des candidats fixe au défilement, candidat choisi visible, retour en haut de la fiche, sans débordement {r}')
    r = pg.evaluate("[getComputedStyle(document.documentElement).touchAction, getComputedStyle(document.getElementById('q')).fontSize]")
    check(r == ['manipulation', '16px'], f'mobile : pas de zoom au double tap ni à la saisie (zoom à deux doigts conservé) {r}')
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
    c = pg.evaluate("""()=>{ const all=D.candidates.flatMap(c=>c.measures.map(m=>({c:c.id,m}))).filter(o=>has(o.m)&&!o.m.a_confirmer), a=all[0], b=all[1];
      return [quizCost({picks:[[a,b],[a]]}), (a.m.claude.central+b.m.claude.central)/2+a.m.claude.central]; }""")
    check(abs(c[0] - c[1]) < 1e-9, 'quiz résultat : « Les deux » compte la moyenne des deux effets sur le déficit')
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
    # logement : APL perdues si réservées selon la nationalité, +10 % chez qui le publie ; curseur caché hors location
    pg.evaluate("""document.querySelector('#s-nat [data-v="hors"]').click(); document.querySelector('#s-home [data-v="loc"]').click();
      document.getElementById('s-apl').value=200; D.candidates.forEach(c=>openSim.add(c.id)); sim()""")
    vals = sorted(pg.evaluate("""[...document.querySelectorAll('#simres .srow')].map(r=>{ const m=r.innerText.replace(/\\s+/g,' ').match(/Aide au logement.*?([+−]\\d+) €\\/mois/); return m?m[1]:null; }).filter(Boolean)"""))
    hidden = pg.evaluate("""(()=>{ document.querySelector('#s-home [data-v="proprio"]').click(); return document.getElementById('f-apl').hidden; })()""")
    check(vals.count('−200') == 2 and '+20' in vals and hidden, f'simulateur : logement (APL réservées ou +10 %, curseur caché hors location) {vals}')
    pg.evaluate("""document.querySelector('#s-nat [data-v="fr"]').click(); document.querySelector('#s-home [data-v="loc"]').click(); document.getElementById('s-apl').value=0; sim()""")
    # paramètre publié mais hors total : appliqué (allocations familiales +10 %, 2 enfants)
    pg.evaluate("document.querySelector('#s-status [data-v=\"prive\"]').click(); S.kids=2; document.getElementById('s-salary').value=1800; openSim.add('melenchon'); sim()")
    check(pg.evaluate("[...document.querySelectorAll('#simres .srow')].some(r=>/Allocations familiales \\+10 %/.test(r.textContent))"), 'simulateur : paramètre publié hors total appliqué (allocations familiales +10 %)')
    # second audit du simulateur : heures sup sans gain fictif, hausse des allocations reprise par le RSA, durée de cotisation, APL réservées
    rows = pg.evaluate("""(()=>{ document.querySelector('#s-status [data-v="prive"]').click(); S.kids=0; document.getElementById('s-salary').value=4500; document.getElementById('s-year').value=1990; document.getElementById('s-ot').checked=true;
      D.candidates.forEach(c=>openSim.add(c.id)); sim(); const t=document.getElementById('simres').innerText.replace(/\\s+/g,' ');
      document.getElementById('s-ot').checked=false; return t; })()""")
    check('Heures sup' not in re.sub(r'Heures sup sans[^:]*:', '', rows) and 'pas de gain calculé' in rows, 'simulateur : heures sup sans gain fictif de CSG (Philippe, Retailleau)')
    check(re.search(r'Durée pour le taux plein.{0,120}\+2 ans', rows) and re.search(r'Durée pour le taux plein.{0,120}−3 ans', rows), 'simulateur : durée de cotisation affichée (Philippe +2 ans, Mélenchon −3 ans)')
    t = pg.evaluate("""(()=>{ document.querySelector('#s-status [data-v="minima"]').click(); S.kids=3; document.getElementById('s-salary').value=1300; sim();
      const r=[...document.querySelectorAll('#simres .srow')].find(x=>x.dataset.c==='melenchon'); return r.innerText.replace(/\\s+/g,' '); })()""")
    check('Ajustement du RSA' in t, 'simulateur : hausse des allocations reprise par le RSA (Mélenchon)')
    t = pg.evaluate("""(()=>{ document.querySelector('#s-nat [data-v="hors"]').click(); document.querySelector('#s-home [data-v="loc"]').click(); document.getElementById('s-apl').value=200; sim();
      const t=document.getElementById('simres').innerText.replace(/\\s+/g,' '); document.querySelector('#s-nat [data-v="fr"]').click(); document.getElementById('s-apl').value=0; S.kids=0; sim(); return t; })()""")
    check('APL réservées aux Français' in t, 'simulateur : APL de Le Pen « réservées aux Français »')
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
    # repères officiels : chaque thème des fiches a les siens ; 4 visibles, les autres se déplient ; les faits sensibles y sont
    th = pg.evaluate("[...new Set(D.candidates.flatMap(c=>c.measures.map(m=>m.theme)))].filter(t=>!((D.baseline||{})[t]||[]).length)")
    check(not th, f'repères : chaque thème des fiches a ses repères officiels {th}')
    lt = pg.evaluate("(D.life_themes||Object.keys(LT)).filter(t=>!((D.baseline||{})[t]||[]).length)")
    check(not lt, f'repères : chaque thème « Vie quotidienne » a ses repères officiels {lt}')
    r = pg.evaluate("(()=>{ const d=document.createElement('div'); d.innerHTML=baseBox('securite'); return [d.querySelectorAll('.base > div').length, d.querySelectorAll('.bmore .bin > div').length, D.baseline.securite.length, /Viols/.test(d.textContent)]; })()")
    check(r[0] == 4 and r[1] == r[2] - 4 and r[3], f'repères : 4 visibles, {r[1]} dépliables, viols compris {r}')
    # signalement visible sur chaque page : bouton en bas de page, formulaire qui s'ouvre ; rubrique Contact
    r = pg.evaluate("(()=>{ go('quiz'); const b=document.getElementById('foot-report'); const vis=b.offsetParent!==null; b.click(); const f=document.getElementById('foot-rep'); const ok=!f.hidden && !!f.querySelector('textarea'); go('accueil'); return [vis, ok, f.hidden, document.getElementById('contact').textContent.length>50 && /indépendant/.test(document.getElementById('about').textContent) && /Hébergeur/.test(document.getElementById('legal').textContent)]; })()")
    check(r == [True, True, True, True], f'signalement : bouton en bas de page, formulaire, fermé au changement de page ; contact, qui fait ce site, mentions légales {r}')
    # carburant : baisse de la taxe par litre (Le Pen : tarif 2017 avec TVA à 5,5 % ; Zemmour : −1/3, TVA à 20 %) pour 300 €/mois d'essence
    r = pg.evaluate("""(()=>{ document.getElementById('s-fuel').value=300; document.querySelector('#s-status [data-v="prive"]').click(); openSim.clear(); ['le-pen','zemmour'].forEach(i=>openSim.add(i)); sim();
      const v=id=>{ const row=[...document.querySelectorAll(`#simres .srow[data-c="${id}"] .rw`)].find(x=>/Taxe sur les carburants/.test(x.textContent)); const m=row&&row.textContent.match(/([0-9]+) €\\/mois/); return m?+m[1]:0; };
      const out=[v('le-pen'), v('zemmour')]; document.getElementById('s-fuel').value=100; sim(); return out; })()""")
    check(r[0] in (4, 5) and r[1] in (37, 38, 39), f'simulateur : taxe carburant Le Pen ≈ 4,7 €, Zemmour ≈ 38 € pour 300 €/mois d\'essence {r}')
    # part fiscale entière dès le 2e enfant (Le Pen) : gain avec 2 enfants, rien avec 1, pas de double compte avec l'exonération des moins de 30 ans
    r = pg.evaluate("""(()=>{ const g=id=>document.getElementById(id); document.querySelector('#s-status [data-v="prive"]').click(); g('s-salary').value=3500; openSim.clear(); openSim.add('le-pen');
      const f=(k,y)=>{ S.kids=k; g('s-year').value=y; sim(); return [...document.querySelectorAll('#simres .srow[data-c="le-pen"] .rw')].filter(x=>/^Impôt/.test(x.textContent.trim())).length; };
      return [f(2,1985), f(1,1985), f(2,2000)]; })()""")
    check(r == [1, 0, 1], f'simulateur : part fiscale dès le 2e enfant (1 ligne avec 2 enfants, aucune avec 1, une seule avant 30 ans) {r}')
    check(not errs, f'aucune erreur JS {errs[:1]}')
    b.close()
sys.exit(1 if fail else 0)
