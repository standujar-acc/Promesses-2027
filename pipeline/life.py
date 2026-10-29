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
# Reprises d'agence (AFP, via connaissancedesenergies.org) remplacées par l'original officiel, chez tous les candidats qui les citent (registre S027, 29/10/2026)
EPR_S = {'label': "Cour des comptes, « La filière EPR : une dynamique nouvelle, des risques persistants »", 'year': 2025, 'url': 'https://www.ccomptes.fr/fr/publications/la-filiere-epr-une-dynamique-nouvelle-des-risques-persistants'}
MAINT_S = {'label': "Cour des comptes, « La maintenance du parc électronucléaire d'EDF en France »", 'year': 2025, 'url': 'https://www.ccomptes.fr/fr/publications/la-maintenance-du-parc-electronucleaire-dedf-en-france'}
HCC_S = {'label': "Haut Conseil pour le climat, rapport annuel 2026", 'year': 2026, 'url': 'https://www.hautconseilclimat.fr/publications/dangers-climatiques-la-france-face-a-ses-responsabilites/'}
RTE_S = {'label': "RTE, Futurs énergétiques 2050, résumé exécutif (vie-publique.fr)", 'year': 2021, 'url': 'https://vie-publique.fr/files/rapports/fichiers_joints/282232-resume-executif.pdf'}
ORIG = {'connaissancedesenergies.org/afp/programme-depr-': EPR_S, 'connaissancedesenergies.org/afp/prolonger-jusqua-60-ans-': MAINT_S,
        'connaissancedesenergies.org/afp/climat-la-france-nest-pas-prete-': HCC_S, 'connaissancedesenergies.org/afp/il-serait-pertinent-': RTE_S,
        'connaissancedesenergies.org/afp/futurs-energetiques-2050-': RTE_S}
OVR.update({
 ('le-pen', 'logement'): {'evidence': SRU + " " + RENO, 'evidence_level': 'mitigee'},
 ('lisnard', 'logement'): {'evidence': SRU, 'evidence_level': 'mitigee'},
 ('melenchon', 'logement'): {'evidence': RENO + " Cour des comptes : la crise exige d'accroître durablement l'offre.", 'evidence_level': 'mitigee'},
 ('attal', 'logement'): {'evidence': RENO, 'evidence_level': 'mitigee'},
 ('zemmour', 'logement'): {'evidence': RENO, 'evidence_level': 'mitigee'},
 ('lisnard', 'environnement'): {'evidence': EPR, 'evidence_level': 'mitigee', 'add': [EPR_S]},
 ('zemmour', 'environnement'): {'evidence': EPR + " " + RTE, 'evidence_level': 'mitigee', 'add': [MAINT_S, RTE_S]},
 # écart RTE : « de l'ordre de 10 milliards d'euros par an » (valeur de référence du résumé exécutif), 20 dans certaines variantes (registre S027)
 ('melenchon', 'environnement'): {'evidence': "RTE : scénarios sans nouveau nucléaire plus coûteux, de l'ordre de 10 Md€/an (jusqu'à 20 dans certaines variantes). HCC 2026 : baisse requise >4 %/an, contre −2,1 % en 2025."},
 # gain promis cité avec ses dates (site du candidat, 16/10/2026) ; lisnard.cards, site non officiel, retiré de ce thème (registre S069)
 ('lisnard', 'economie'): {'indicator': "250 à 400 €/mois net selon les interventions (250 € pour 2 500 € de revenu), estimation du camp", 'drop': ['lisnard.cards'],
     'add': [{'label': "Nouvelle Énergie, « Le programme de David Lisnard est-il chiffré ? »", 'year': 2026, 'url': 'https://www.unenouvelleenergie.fr/questions/le-programme-de-david-lisnard-est-il-chiffre/'}]},
 ('retailleau', 'securite'): {'evidence': PP + HEN, 'evidence_level': 'mitigee', 'add': [HEN_S]},
 ('zemmour', 'sante'): {'evidence': "Médecins salariés par l'État et obligation de garde : pas d'évaluation française identifiée.", 'evidence_level': 'pas_d_etude', 'drop': ['csem.org']},
 ('le-pen', 'rayonnement'): {'evidence': VED + " Baisser la contribution à l'UE demande l'unanimité.", 'evidence_level': 'mitigee'},
 ('melenchon', 'rayonnement'): {'evidence': VED, 'evidence_level': 'mitigee'},
 ('zemmour', 'rayonnement'): {'evidence': "Banque de Finlande (2025) : multiplicateur des dépenses de défense d'environ 0,6 à 1,0. " + VED, 'evidence_level': 'mitigee'},
 ('philippe', 'logement'): {'evidence_level': 'non_demontree'},
 ('philippe', 'sante'): {'evidence_level': 'pas_d_etude'},
})
# école : même lecture d'une étude pour un même type de mesure (petites classes, salaires, examen de fin de cycle), études du quiz (registre S058)
DD = "Petites classes en CP-CE1 : gains nets en CP ; en 6e, aucun en français, petit gain en maths après la 1re génération (DEPP, 2026)."
DD_S = [{'label': 'DEPP, Synthèse n° 8, réduction de la taille de classe en éducation prioritaire', 'year': 2026, 'url': 'https://www.education.gouv.fr/sites/default/files/document/r-duction-de-la-taille-de-classe-en-ducation-prioritaire-que-nous-apprennent-les-donn-es-de-la-depp--478949.pdf'},
        {'label': 'DEPP, effets à long terme des classes réduites (cohortes 2023-2024), via professeurs-des-ecoles.com', 'year': 2026, 'url': 'https://www.professeurs-des-ecoles.com/2026/10/14/classes-reduites-en-rep-un-effet-positif-en-maths-encore-visible-en-6e-selon-la-depp/'}]
SAL = "Salaires : hausse générale non évaluée ; prime REP+ doublée, +3 points de premiers vœux (Insee, 2023)."
SAL_S = [{'label': 'Insee Analyses n° 87, prime REP+ et vœux de mutation des enseignants', 'year': 2023, 'url': 'https://www.insee.fr/fr/statistiques/7658358'}]
EXAM_S = [{'label': 'Jürges, Schneider, Büchel, examens centraux et acquis des élèves (CESifo WP 939)', 'year': 2005, 'url': 'https://www.ifo.de/DocDL/cesifo_wp939.pdf'},
          {'label': 'Cnesco – redoublement', 'year': 2014, 'url': 'https://www.cnesco.fr/wp-content/uploads/2014/08/280814CNESCO_redoublement.pdf'}]
EXAM = "Examen de fin de cycle : un tiers d'année gagné en maths (Allemagne, 2005), mais redoubler après un échec réduit les chances de diplôme (Cnesco, 2014)."
NOAEF = ['media.ac-normandie.fr']  # copies de presse qui ne répondent plus : remplacées par la note DEPP officielle
OVR.update({
 ('le-pen', 'ecole'): {'evidence': "Uniforme : climat amélioré selon 36% des directeurs, effet quasi nul sur les résultats (ministère, 2026). " + DD + " " + SAL, 'add': SAL_S + DD_S, 'drop': NOAEF},
 ('melenchon', 'ecole'): {'evidence': DD + " Petites écoles : regroupements suivis d'une baisse passagère des résultats (Danemark, 2018) ou d'un léger gain (Pays-Bas, 2016).",
     'add': [{'label': "Beuchert et al., regroupements d'écoles au Danemark (CESifo WP 6082, Economics of Education Review)", 'year': 2018, 'url': 'https://www.ifo.de/en/cesifo/publications/2016/working-paper/short-term-effects-school-consolidation-student-achievement'},
             {'label': "de Haan, Leuven, Oosterbeek, regroupements d'écoles aux Pays-Bas (JLEO)", 'year': 2016, 'url': 'https://dare.uva.nl/id/e4bce2db-c078-4bfc-b20d-0cf53a47b7ba'}] + DD_S, 'drop': NOAEF},
 ('glucksmann', 'ecole'): {'evidence': DD + " " + SAL + " Mixité à Paris : objectif atteint dans 2 secteurs sur 3, évitement du privé de 24 % à 16 % dans l'un (IPP, 2021) ; condition imposée au privé non évaluée.",
     'add': SAL_S + [{'label': 'IPP, évaluation des secteurs multi-collèges à Paris (via Banque des territoires)', 'year': 2021, 'url': 'https://www.banquedesterritoires.fr/bilan-mitige-pour-les-experimentations-en-faveur-de-la-mixite-sociale-dans-des-colleges-parisiens'}] + DD_S, 'drop': NOAEF},
 ('philippe', 'ecole'): {'evidence': DD + " " + SAL + " Amendes aux parents d'absentéistes : sans lien avec le niveau d'absences (pays de Galles, 2018) ; pas d'évaluation française.",
     'add': SAL_S + [{'label': 'Gouvernement gallois (ICF), évaluation des amendes pour absentéisme scolaire', 'year': 2018, 'url': 'https://www.gov.wales/sites/default/files/statistics-and-research/2019-06/180508-evaluation-fixed-penalty-notices-issued-regular-non-attendance-school-en.pdf'}] + DD_S, 'drop': NOAEF},
 ('retailleau', 'ecole'): {'evidence': "Examen de fin de cycle : un tiers d'année gagné en maths (Allemagne, 2005). Redoublement : effet proche de zéro à court terme, négatif à long terme, chances de diplôme réduites (Cnesco, 2014). Établissements publics autonomes : progrès de collèges en difficulté (Angleterre, 2019), aucun gain dans des écoles primaires (Angleterre, 2017).",
     'evidence_level': 'mitigee', 'add': EXAM_S[:1] + [{'label': 'Eyles, Machin, académies en Angleterre (JEEA)', 'year': 2019, 'url': 'https://researchonline.lse.ac.uk/id/eprint/88581/'},
             {'label': 'Eyles, Machin, McNally, écoles primaires autonomes en Angleterre (CEP DP 1455)', 'year': 2017, 'url': 'https://researchonline.lse.ac.uk/id/eprint/69027'}]},
 ('attal', 'ecole'): {'evidence': DD + " " + SAL + " " + EXAM, 'add': SAL_S + EXAM_S + DD_S, 'drop': NOAEF},
 ('lisnard', 'ecole'): {'evidence': EXAM + " " + SAL + " Assouplissement de la carte scolaire (2007) : effets globaux faibles, mais fuite accélérée des collèges défavorisés et ségrégation accrue (DEPP, 2013).", 'evidence_level': 'mitigee', 'add': EXAM_S + SAL_S},
 ('zemmour', 'ecole'): {'evidence': EXAM + " Groupes de niveau : pas d'amélioration des résultats, et les élèves faibles risquent de perdre l'effet des pairs selon l'OCDE (PISA 2022).", 'evidence_level': 'mitigee', 'add': EXAM_S},
})
# même test « précis » pour une même formulation
VFLIP = {'Bloquer temporairement': False, 'Assistant médical fondé sur l': False, 'Contrôle du Conseil constitutionnel limité': False, 'Police de proximité modernisée': False, "Fonds national d'acquisition foncière": False,
         "commandement intégré de l'OTAN": True, "Sortir de l'OTAN": True}

CAMP = {'melenchon': 'melenchon2027.fr', 'philippe': 'edouardphilippe.fr', 'attal': 'attalpresident.fr', 'lisnard': 'lisnard.cards'}

def merge(D):
    parts = [f for f in ('life-a.json', 'life-b.json', 'life-eco.json') if os.path.exists(os.path.join(H, 'data', f))]
    if not parts: return D
    ev = J('evidence_levels.json') if os.path.exists(os.path.join(H, 'data', 'evidence_levels.json')) else {}
    life = {}; used = set()
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
                olds = [d for d in ORIG if any(d in x['url'] for x in th['sources'])]
                if olds:
                    used.update(olds)
                    th['sources'] = [x for x in th['sources'] if not any(d in x['url'] for d in olds)]
                    th['sources'] += [dict(s) for s in {ORIG[d]['url']: ORIG[d] for d in olds}.values() if s['url'] not in {x['url'] for x in th['sources']}]
                life.setdefault(cid, {})[th['theme']] = th
        if 'baseline' in x: D.setdefault('baseline', {}).update({k: [dict(i, label=html.unescape(i['label'])) for i in v] for k, v in x['baseline'].items()})
    assert used == set(ORIG), f"ORIG sans effet : {set(ORIG) - used}"
    ids = [c['id'] for c in D['candidates']]
    themes = [t for t in THEMES if any(t in v for v in life.values())]
    D['life_themes'] = themes
    D['life'] = {cid: [life.get(cid, {}).get(t) or {'theme': t, 'proposals': [], 'indicator': None, 'evidence': 'Pas de proposition publiée sur ce thème.', 'sources': [], 'evidence_level': None} for t in themes] for cid in ids}
    b = J('baseline.json'); b.update(D.get('baseline', {})); D['baseline'] = b
    return D
