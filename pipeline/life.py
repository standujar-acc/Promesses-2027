"""Fusionne la dimension « vie quotidienne » dans D (D.life, D.baseline).
Entrées : data/life-a.json, data/life-b.json, data/life-eco.json, data/baseline.json, data/evidence_levels.json
Même test « vérifiable » appliqué à toutes les propositions, quel que soit le candidat."""
import json, re, os
H = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(H, 'data', f)))
VERIF = re.compile(r"\d|\b(loi|décret|référendum|ordonnance|article|révision constitutionnelle|proposition de loi|projet de loi|directive|règlement européen)\b", re.I)
THEMES = ['securite', 'sante', 'ecole', 'environnement', 'logement', 'libertes', 'economie', 'rayonnement']

import html
OLD = re.compile(r"\s*\((non reconfirm[ée]e?s? en 2026|programme 2022|2022)\)", re.I)
def norm_prop(p):
    t = p['text'] if isinstance(p, dict) else p
    t = html.unescape(re.sub(r"\s+", " ", t)).strip().rstrip('.')
    old = bool(OLD.search(t)); t = OLD.sub('', t).strip()
    v = p.get('verifiable') if isinstance(p, dict) else None
    if not isinstance(v, bool): v = bool(VERIF.search(t))
    return {'text': t, 'verifiable': v, 'old': old}

# Même type de mesure → même lecture des études, chez tous les candidats.
IPP_PP = {'label': 'IPP – Note n°105 peines planchers', 'year': 2024, 'url': 'https://www.ipp.eu/wp-content/uploads/2024/03/Note_IPP_105_peines_planchers.pdf'}
PP = "Peines planchers (2007-2014) : pas d'effet dissuasif immédiat, récidive ciblée −13 % à quatre ans, ≈ 4 000 années de détention en plus par an (IPP, 2024)."
OVR = {
 ('le-pen', 'securite'): {'evidence': PP + " Nouvelles places de prison vite comblées (Sénat, 2023).", 'evidence_level': 'mitigee', 'add': [IPP_PP]},
 ('philippe', 'securite'): {'evidence': PP + " Bracelet plutôt que courte prison : récidive −6 à 7 points (Henneguelle, 2016).", 'evidence_level': 'mitigee', 'add': [IPP_PP]},
 ('retailleau', 'securite'): {'evidence': PP, 'evidence_level': 'mitigee'},
 ('philippe', 'economie'): {'evidence': "Heures sup défiscalisées (TEPA) : pas d'effet significatif sur les heures travaillées (IPP, 2012). Chômage plus court de 12 %, mais emplois peu durables (Dares, 2025). Impôts de production : baisse de 2021 sans effet mesurable sur l'investissement (IPP, 2025).", 'evidence_level': 'mitigee', 'add': [{'label': 'IPP, impôts de production', 'year': 2025, 'url': 'https://www.ipp.eu/wp-content/uploads/2025/10/FS_ImpotsProductions-9.pdf'}]},
 ('zemmour', 'securite'): {'evidence': "Expulsions après arrestation (États-Unis) : pas d'effet observable sur la criminalité (Miles & Cox, 2014). " + PP, 'evidence_level': 'non_demontree'},
}

def NOFF(u, lab):
    if 'non officiel' in lab or 'agrégateur' in lab: return ''
    if any(d in u for d in ('wikiglucksmann', 'lisnard.cards')): return ' (non officiel)'
    if any(d in u for d in ('votons-2027', 'monvote2027', 'repere2027', 'france-vote')): return ' (agrégateur)'
    return ''


RENO = "Rénovation énergétique : économies réelles de 5 à 6,6 %, environ 42 % des gains théoriques (Insee-SDES, 2026)."
SRU = "Loi SRU : son article 55 explique près de la moitié des logements sociaux construits dans les communes visées (CGDD, 2014) ; pas d'évaluation d'une suppression."
EPR = "Cour des comptes (2025) : prolonger les réacteurs reste moins cher que le neuf ; coût des six premiers EPR2 +30 % (67,4 Md€), risque d'échec."
RTE = "RTE (2021) : neutralité carbone impossible sans développement significatif des renouvelables ; nouveaux réacteurs économiquement pertinents."
VED = "Rapport Védrine (2012) : effets du retour dans le commandement intégré de l'OTAN mitigés ; une nouvelle sortie réduirait les leviers d'influence de la France."
HEN = " Bracelet plutôt que courte prison : récidive −6 à 7 points (Henneguelle, 2016)."
HEN_S = {'label': 'Journal of Law and Economics, bracelet', 'year': 2016, 'url': 'https://chicagounbound.uchicago.edu/jle/vol59/iss3/6/'}
OVR.update({
 ('le-pen', 'logement'): {'evidence': SRU + " " + RENO, 'evidence_level': 'mitigee'},
 ('lisnard', 'logement'): {'evidence': SRU, 'evidence_level': 'mitigee'},
 ('melenchon', 'logement'): {'evidence': RENO + " Cour des comptes : la crise exige d'accroître durablement l'offre.", 'evidence_level': 'mitigee'},
 ('attal', 'logement'): {'evidence': RENO, 'evidence_level': 'mitigee'},
 ('zemmour', 'logement'): {'evidence': RENO, 'evidence_level': 'mitigee'},
 ('lisnard', 'environnement'): {'evidence': EPR, 'evidence_level': 'mitigee', 'add': [{'label': 'Cour des comptes via AFP – EPR', 'year': 2025, 'url': 'https://www.connaissancedesenergies.org/afp/programme-depr-la-cour-des-comptes-publie-un-rapport-critique-et-recalcule-le-cout-de-flamanville-3-250114'}]},
 ('zemmour', 'environnement'): {'evidence': EPR + " " + RTE, 'evidence_level': 'mitigee', 'add': [{'label': 'RTE Futurs énergétiques via AFP', 'year': 2021, 'url': 'https://www.connaissancedesenergies.org/afp/il-serait-pertinent-de-construire-de-nouveaux-reacteurs-nucleaires-dun-point-de-vue-economique-selon-rte-211025'}]},
 ('retailleau', 'securite'): {'evidence': PP + HEN, 'evidence_level': 'mitigee', 'add': [HEN_S]},
 ('zemmour', 'sante'): {'evidence': "Médecins salariés par l'État et obligation de garde : pas d'évaluation française identifiée.", 'evidence_level': 'pas_d_etude', 'drop': ['csem.org']},
 ('le-pen', 'rayonnement'): {'evidence': VED + " Baisser la contribution à l'UE demande l'unanimité.", 'evidence_level': 'mitigee'},
 ('melenchon', 'rayonnement'): {'evidence': VED, 'evidence_level': 'mitigee'},
 ('zemmour', 'rayonnement'): {'evidence': "Banque de Finlande (2025) : multiplicateur des dépenses de défense d'environ 0,6 à 1,0. " + VED, 'evidence_level': 'mitigee'},
 ('philippe', 'logement'): {'evidence_level': 'non_demontree'},
 ('philippe', 'sante'): {'evidence_level': 'pas_d_etude'},
})
DD = "Petites classes en CP-CE1 : gains nets en CP ; à l'entrée en 6e, plus rien pour la 1re génération, un petit gain en maths pour les suivantes, aucun en français (DEPP, 2026)."
DD_S = {'label': 'DEPP, effets à long terme des classes réduites (cohortes 2023-2024), via professeurs-des-ecoles.com', 'year': 2026, 'url': 'https://www.professeurs-des-ecoles.com/2026/10/14/classes-reduites-en-rep-un-effet-positif'}
OVR.update({
 ('le-pen', 'ecole'): {'evidence': "Uniforme : climat amélioré selon 36% des directeurs, effet quasi nul sur les résultats (ministère, 2026). " + DD, 'add': [DD_S]},
 ('melenchon', 'ecole'): {'evidence': DD, 'add': [DD_S]},
 ('philippe', 'ecole'): {'evidence': DD + " Hausse salariale et amende parentale : pas d'évaluation française identifiée.", 'add': [DD_S]},
 ('glucksmann', 'ecole'): {'evidence': DD + " Mixité imposée à Paris : objectifs atteints dans 2 secteurs sur 3 (IPP, 2021).", 'add': [DD_S]},
 ('attal', 'ecole'): {'evidence': DD, 'add': [DD_S]},
})
# même test « précis » pour une même formulation
VFLIP = {'Bloquer temporairement': False, 'Assistant médical fondé sur l': False, 'Contrôle du Conseil constitutionnel limité': False, 'Police de proximité modernisée': False, "Fonds national d'acquisition foncière": False,
         "commandement intégré de l'OTAN": True, "Sortir de l'OTAN": True}

CAMP = {'melenchon': 'melenchon2027.fr', 'philippe': 'edouardphilippe.fr', 'attal': 'attalpresident.fr', 'lisnard': 'lisnard.cards'}

def merge(D):
    parts = [f for f in ('life-a.json', 'life-b.json', 'life-eco.json') if os.path.exists(os.path.join(H, 'data', f))]
    if not parts: return D
    ev = J('evidence_levels.json') if os.path.exists(os.path.join(H, 'data', 'evidence_levels.json')) else {}
    life = {}
    for f in parts:
        x = J(f)
        for cid, arr in x['life'].items():
            for th in arr:
                th['proposals'] = [norm_prop(p) for p in th.get('proposals', []) if (p['text'] if isinstance(p, dict) else p).strip()]
                th['evidence'] = html.unescape(th.get('evidence') or '')
                if th.get('indicator'): th['indicator'] = html.unescape(th['indicator'])
                lvl = ev.get(cid, {}).get(th['theme']) or th.get('evidence_level')
                if lvl not in ('prouvee', 'mitigee', 'non_demontree', 'pas_d_etude'): lvl = None
                if not th['proposals']: lvl = None
                th['evidence_level'] = lvl
                th['sources'] = [dict(s, label=html.unescape(s.get('label', '')) + NOFF(s.get('url',''), s.get('label',''))) for s in th.get('sources', []) if s.get('url', '').startswith('http')]
                # pas de site d'un camp rival comme source d'un candidat
                own = {d for k, d in CAMP.items() if k == cid}
                keep = [x for x in th['sources'] if not any(d in x['url'] for k, d in CAMP.items() if k != cid)]
                if keep: th['sources'] = keep
                o = OVR.get((cid, th['theme']))
                for p in th['proposals']:
                    for k0, v0 in VFLIP.items():
                        if k0 in p['text']: p['verifiable'] = v0
                if o:
                    th.update({k: v for k, v in o.items() if k not in ('add', 'drop')})
                    th['sources'] = [x for x in th['sources'] if not any(d in x['url'] for d in o.get('drop', []))]
                    th['sources'] += [s for s in o.get('add', []) if s['url'] not in {x['url'] for x in th['sources']}]
                life.setdefault(cid, {})[th['theme']] = th
        if 'baseline' in x: D.setdefault('baseline', {}).update({k: [dict(i, label=html.unescape(i['label'])) for i in v] for k, v in x['baseline'].items()})
    ids = [c['id'] for c in D['candidates']]
    themes = [t for t in THEMES if any(t in v for v in life.values())]
    D['life_themes'] = themes
    D['life'] = {cid: [life.get(cid, {}).get(t) or {'theme': t, 'proposals': [], 'indicator': None, 'evidence': 'Pas de proposition publiée sur ce thème.', 'sources': [], 'evidence_level': None} for t in themes] for cid in ids}
    b = J('baseline.json'); b.update(D.get('baseline', {})); D['baseline'] = b
    return D
