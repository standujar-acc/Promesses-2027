"""Fusionne la dimension « vie quotidienne » dans D (D.life, D.baseline).
Entrées : data/life-a.json, data/life-b.json, data/life-eco.json, data/baseline.json, data/evidence_levels.json,
data/life-attribution.json (pour chaque proposition affichée, les sources qui parlent pour le candidat : contrôle du bloc « review 34 »)
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

# Sites non officiels d'un candidat, et agrégateurs : toute la liste D['weak_domains'] (fixée par merge), testée sur le nom d'hôte exact
# ou un sous-domaine, jamais sur une sous-chaîne de l'adresse (même test que l'app : franceinfo.fr n'est pas « info.fr ») ; review 32 (31/10/2026)
from urllib.parse import urlparse
NONOFF = ('wikiglucksmann.fr', 'lisnard.cards')
WEAKD = []
def host_in(u, doms):
    h = (urlparse(u).hostname or '').lower()
    return bool(h) and any((h == d or h.endswith('.' + d)) if '.' in d else d in h.split('.') for d in doms)
def NOFF(u, lab):
    if 'non officiel' in lab or 'agrégateur' in lab: return ''
    if host_in(u, NONOFF): return ' (non officiel)'
    if host_in(u, WEAKD): return ' (agrégateur)'
    return ''


RENO = "Rénovation énergétique : économies réelles de 5 à 6,6 %, environ 42 % des gains théoriques (Insee-SDES, 2026)."
SRU = "Loi SRU : son article 55 explique près de la moitié des logements sociaux construits dans les communes visées (CGDD, 2014) ; pas d'évaluation d'une suppression."
EPR = "Cour des comptes (2025) : prolonger les réacteurs reste moins cher que le neuf ; coût des six premiers EPR2 +30 % (67,4 Md€), risque d'échec."
RTE = "RTE (2021) : neutralité carbone impossible sans développement significatif des renouvelables ; nouveaux réacteurs économiquement pertinents."
VED = "Rapport Védrine (2012) : effets du retour dans le commandement intégré de l'OTAN mitigés ; une nouvelle sortie réduirait les leviers d'influence de la France."
UEU = "Baisser la contribution à l'UE demande l'unanimité."
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
 ('attal', 'environnement'): {'evidence': EPR + " HCC 2026 : émissions −2,1 % en 2025, un rythme qui doit au moins doubler ; leasing social et MaPrimeRénov' jugés sous-dimensionnés.", 'add': [EPR_S]},
 ('zemmour', 'environnement'): {'evidence': EPR + " " + RTE, 'evidence_level': 'mitigee', 'add': [MAINT_S, RTE_S]},
 # écart RTE : « de l'ordre de 10 milliards d'euros par an » (valeur de référence du résumé exécutif), 20 dans certaines variantes (registre S027)
 ('melenchon', 'environnement'): {'evidence': "RTE : scénarios sans nouveau nucléaire plus coûteux, de l'ordre de 10 Md€/an (jusqu'à 20 dans certaines variantes). HCC 2026 : baisse requise >4 %/an, contre −2,1 % en 2025."},
 # gain promis cité avec ses dates (site du candidat, 16/10/2026) ; lisnard.cards, site non officiel, retiré de ce thème (registre S069)
 ('lisnard', 'economie'): {'indicator': "250 à 400 €/mois net selon les interventions (250 € pour 2 500 € de revenu), estimation du camp", 'drop': ['lisnard.cards'],
     'add': [{'label': "Nouvelle Énergie, « Le programme de David Lisnard est-il chiffré ? »", 'year': 2026, 'url': 'https://www.unenouvelleenergie.fr/questions/le-programme-de-david-lisnard-est-il-chiffre/'}]},
 ('retailleau', 'securite'): {'evidence': PP + HEN, 'evidence_level': 'mitigee', 'add': [HEN_S]},
 ('zemmour', 'sante'): {'evidence': "Médecins salariés par l'État et obligation de garde : pas d'évaluation française identifiée.", 'evidence_level': 'pas_d_etude', 'drop': ['csem.org']},
 ('le-pen', 'rayonnement'): {'evidence': VED + " " + UEU, 'evidence_level': 'mitigee'},
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
# S117 (29/10) : une même proposition n'est affichée que dans un thème, le plus précis (énergie et nucléaire : « environnement »)
# --- review 23 : « casseur-payeur » et propositions oubliées (29/10/2026) ; registre S097 à S119
# Au plus 5 propositions par thème (décision du porteur du 29/10, la même pour tous). Règle d'ordre quand un thème dépasse cinq propositions :
# d'abord celles de 2026 (les non reconfirmées passent après), parmi elles les précises avant les intentions, puis les plus récentes ;
# à égalité ou à date inconnue, l'ordre déjà affiché est gardé (une page de programme mise à jour n'est pas une nouvelle annonce).
# Une proposition remplacée par sa version précise (ou celle du programme) n'est pas gardée en double. Ce qui reste hors affichage : registre S106.
# Les listes ci-dessous remplacent celles de data/life-*.json pour ces thèmes (même forme que norm_prop : text, verifiable, old).
# texte raccourci le 29/10 pour tous, même contenu (décision du porteur ; avant : « l'auteur et les parents d'un mineur doivent déjà réparer ;
# recours de l'État (2019) jamais utilisé ; dégâts à sa charge : 4,1 M€ par an en moyenne ; effet dissuasif non évalué »)
CASSE = ("Casseur-payeur : réparation déjà due (auteur, parents d'un mineur) ; l'État en paie 4,1 M€/an, recours (2019) inutilisé ; "
         "dissuasion non évaluée.")
CASSE_S = [{'label': "Sénat, projet de loi n° 952 sur la réparation des dommages (exposé des motifs, étude d'impact)", 'year': 2026, 'url': 'https://www.senat.fr/leg/pjl25-952.pdf'},
           {'label': 'LCP, projet de loi adopté au Sénat le 28/10', 'year': 2026, 'url': 'https://lcp.fr/actualites/projet-de-loi-casseurs-payeurs-le-texte-transmis-a-l-assemblee-apres-son-adoption-au'}]
PLACES = "Nouvelles places de prison vite comblées (Sénat, 2023)."
EXPUL = "Expulsions après arrestation (États-Unis) : pas d'effet observable sur la criminalité (Miles & Cox, 2014)."
RESEAUX = "En Inde, les coupures de réseaux vont de pair avec davantage d'actions violentes (Rydzak, 2019). Conseil d'État 2025 : le blocage de TikTok en Nouvelle-Calédonie jugé illégal."
IA = "DG Trésor (2024) : aucun effet macroéconomique significatif de l'IA mesuré à ce stade."
IA_S = {'label': "DG Trésor, enjeux de l'IA", 'year': 2024, 'url': 'https://www.tresor.economie.gouv.fr/Articles/65035441-140e-4e2f-b1a0-2c5abceb6cc7/files/337f850a-3329-4803-b509-e5276c04ab30'}
# RTE_S : source officielle (résumé exécutif), définie plus haut avec les originaux des reprises d'agence (registre S027)
def _p(t, v=True, old=False): return {'text': t, 'verifiable': v, 'old': old}
def _s(label, url): return {'label': label, 'year': 2026, 'url': url}
def _upd(cid, th, props, add=(), drop=(), **kw):
    o = OVR.setdefault((cid, th), {}); o['proposals'] = props; o.update(kw)
    if add: o['add'] = o.get('add', []) + [s for s in add if s['url'] not in {x['url'] for x in o.get('add', [])}]
    if drop: o['drop'] = o.get('drop', []) + list(drop)
# sécurité : casseur-payeur (même texte « évidence » pour tous, CASSE), propositions ajoutées ; lectures communes PP, PLACES, HEN
OVR[('le-pen', 'securite')] = {'evidence': PP + " " + PLACES + " " + CASSE, 'evidence_level': 'mitigee', 'add': [IPP_PP] + CASSE_S + [
    _s('franceinfo, Le Pen et les casseurs (21/10)', 'https://www.franceinfo.fr/politique/marine-le-pen/nous-sommes-confrontes-a-un-etat-qui-s-effondre-estime-marine-le-pen_8246899.html'),
    _s('Capital, Le Pen et les casseurs (21/10)', 'https://www.capital.fr/economie-politique/marine-le-pen-veut-faire-payer-a-vie-les-casseurs-et-solidairement-ceux-qui-ne-partent-pas-apres-les-sommations-1531173'),
    _s('Contre-budget 2027 du groupe RN', 'https://back.deputes-rn.fr/wp-content/uploads/2026/10/GRN-CONTRE-BUDGET-2027-DOSSIER.pdf')],
  'indicator': '30 000 places de prison de plus (contre-budget 2027)',
  'proposals': [_p('Faire payer les dégâts aux casseurs : responsabilité solidaire, prélèvement sur allocations ou salaire, parents pour les mineurs'),
                _p('Construire 30 000 places de prison'), _p('Rétablir les peines planchers, supprimer les remises de peine', True, True),
                _p("Présomption de légitime défense pour les forces de l'ordre", True, True)]}
OVR[('philippe', 'securite')] = {'evidence': PP + HEN + " " + CASSE, 'evidence_level': 'mitigee', 'add': [IPP_PP] + CASSE_S + [
    _s('Capital, plan contre les casseurs (29/10)', 'https://www.capital.fr/economie-politique/prison-des-la-premiere-casse-et-salaire-ponctionne-le-plan-dedouard-philippe-contre-les-casseurs-1531388'),
    _s("L'Express via Orange, entretien au Point (27/10)", 'https://actu.orange.fr/politique/presidentielle-2027-edouard-philippe-veut-diviser-l-immigration-legale-par-deux-face-a-l-echec-de-l-integration-l-express-via-6medias-CNT000002tpDKM.html')],
  'proposals': [_p('Courtes peines de prison dès la première infraction'), _p("Peines planchers pour violences contre dépositaires de l'autorité publique et professeurs"),
                _p('Faire payer les dégâts aux casseurs : prélèvement sur leurs salaires ou prestations sociales'), _p("Supprimer le juge d'application des peines")]}
OVR[('retailleau', 'securite')] = {'evidence': PP + HEN + " " + CASSE, 'evidence_level': 'mitigee', 'add': [HEN_S] + CASSE_S + [
    _s('Capital, Retailleau et les casseurs (RCF, 27/10)', 'https://www.capital.fr/economie-politique/les-aides-ce-nest-pas-un-du-bruno-retailleau-veut-saisir-le-rsa-les-apl-et-les-allocations-des-casseurs-1531316'),
    _s('franceinfo, déchéance de nationalité (19/10)', 'https://www.franceinfo.fr/societe/mobilisation-du-17-octobre/violences-du-17-octobre-bruno-retailleau-denonce-une-convergence-entre-l-extreme-gauche-et-des-racailles-issues-de-l-immigration_8245450.html')],
  'proposals': [_p('Faire payer les dégâts aux casseurs : présomption de responsabilité dans un attroupement violent, aides sociales remises en cause'),
                _p('Majorité pénale abaissée à 15 ans, courtes peines de 15 jours en centres dédiés'),
                _p("Déchéance de nationalité des binationaux auteurs de pillages ou de violences contre les forces de l'ordre"),
                _p('Peines minimales obligatoires pour agressions de policiers, gendarmes et pompiers'), _p("Suppression du juge d'application des peines")]}
OVR[('zemmour', 'securite')] = {'evidence': EXPUL + " " + PP + " " + CASSE, 'evidence_level': 'non_demontree', 'add': [IPP_PP] + CASSE_S + [
    _s('Europe 1, Zemmour et les casseurs (7/10)', 'https://www.europe1.fr/politique/blocus-des-lycees-eric-zemmour-veut-faire-payer-les-casseurs-et-leurs-parents-jusqua-la-nuit-des-temps-1129292'),
    _s('Entrevue, déclarations sur CNews (18/10)', 'https://entrevue.fr/medias/une-horde-de-barbares-maghrebins-et-africains-eric-zemmour-provoque/'),
    _s('Entrevue, émission du 25/10', 'https://entrevue.fr/politique/on-va-vers-une-guerre-civile-eric-zemmour-alerte-sur-le-chaos-en-france/')],
  'proposals': [_p("Rétablir les peines planchers, supprimer le juge de l'application des peines"), _p('Construire très vite 100 000 places de prison'),
                _p('Faire payer les dégâts aux casseurs et à leurs parents, y compris sur leurs allocations ; rétablir la loi anticasseurs de 1970'),
                _p('Déchéance de nationalité puis départ des binationaux auteurs des violences'),
                _p('Expulser les détenus étrangers, estimés à 25 % de la population carcérale')]}
OVR[('attal', 'securite')] = {'evidence': RESEAUX + " " + CASSE, 'evidence_level': 'non_demontree',
  'drop': ['plus-grande-reforme-institutionnelle'], 'add': CASSE_S + [
    _s("attalpresident.fr, rétablir l'ordre (BFM TV, 19/10)", 'https://attalpresident.fr/actualites/gabriel-attal-retablir-ordre-mettre-fin-impunite'),
    _s('attalpresident.fr, entretien sur RTL (19/10)', 'https://attalpresident.fr/actualites/gabriel-attal-rtl-retablir-ordre-jeunesse-avenir-france'),
    _s('attalpresident.fr, France 2 (23/10)', 'https://attalpresident.fr/actualites/gabriel-attal-retablir-ordre-pacte-avenir-jeunesse'),
    _s('RFI, porte-parole de campagne (22/10)', 'https://www.rfi.fr/fr/podcasts/invit%C3%A9-politique/20261022-manifestations-il-faut-faire-payer-ceux-qui-cassent-soutient-c%C3%A9line-g%C3%A9raud-porte-parole-de-gabriel-attal')],
  'proposals': [_p('Faire payer les dégâts aux casseurs (« Tu casses, tu répares ») : responsabilité automatique des deux parents d\'un mineur'),
                _p("Comparution immédiate dès 16 ans et fin de l'excuse de minorité automatique pour les mineurs récidivistes"),
                _p('Reconnaissance faciale et IA pour identifier les casseurs ; militaires et réservistes pour la garde statique des bâtiments publics'),
                _p('Bloquer temporairement et de façon ciblée certains réseaux sociaux pendant les émeutes', False),
                _p("Supprimer le juge d'application des peines", True, True)]}
OVR[('lisnard', 'securite')] = {'evidence': PLACES + " " + CASSE, 'evidence_level': 'non_demontree', 'add': CASSE_S + [
    _s('Europe 1, Objectif Élysée 2027 (27/10)', 'https://www.europe1.fr/politique/en-direct-emeutes-parcoursup-primaire-a-droite-ce-quil-faut-retenir-de-linterview-de-david-lisnard-dans-objectif-elysee-2027-1186743'),
    _s('Nouvelle Énergie, programme « Sécurité »', 'https://www.unenouvelleenergie.fr/notre-programme/securite/'),
    _s('Nouvelle Énergie, entretien au Point (23/10)', 'https://www.unenouvelleenergie.fr/quand-macron-a-parle-pas-un-casseur-na-tremble/')],
  'proposals': [_p('Majorité pénale à 16 ans, excuse de minorité réduite (de 50 % à 20 % de la peine), établissements disciplinaires fermés'),
                _p("Faire payer les dégâts aux casseurs : déduits de leurs aides sociales s'ils ne sont pas solvables"),
                _p('Fichier des casseurs avec obligation de pointer pendant les manifestations ; cagoule interdite, circonstance aggravante'),
                _p('Construire 20 000 places de prison'), _p('Perpétuité réelle et fin du non-cumul des peines pour crimes graves')]}
# libertés
_upd('le-pen', 'libertes', [_p('Élire les députés à la proportionnelle avec prime majoritaire'), _p('Inscrire la « communauté nationale » dans la Constitution'),
                            _p("Instaurer le référendum d'initiative citoyenne", True, True)],
     add=[_s("Europe 1, discours d'Orléans (25/10)", 'https://www.europe1.fr/politique/congres-du-rn-a-orleans-ce-quil-faut-retenir-du-premier-discours-de-campagne-de-marine-le-pen-1181118')])
_upd('melenchon', 'libertes', [_p('Convoquer une Constituante pour une 6e République'), _p('Droit de vote à 16 ans'), _p("Proportionnelle à l'Assemblée et RIC", True, True),
                               _p('Abolir le 49.3', True, True)],
     add=[_s("L'Express via Orange, meeting de Clermont-Ferrand (11/10)", 'https://actu.orange.fr/politique/presidentielle-2027-suppression-de-parcoursup-droit-de-vote-a-16-ans-jean-luc-melenchon-multiplie-les-propositions-pour-les-jeunes-magic-CNT000002sCYOg.html')])
_upd('retailleau', 'libertes', [_p('Référendum législatif étendu à tout le champ de la loi (article 11)'), _p('Seuil du RIP abaissé à environ 2,5 millions de signatures'),
                                _p('Surmonter une censure du Conseil constitutionnel par référendum ou Congrès'),
                                _p('Inscrire le droit à la sécurité dans la Constitution, à égalité avec les libertés fondamentales'),
                                _p('Cour disciplinaire de la magistrature à la place du CSM, avec des citoyens tirés au sort')],
     add=[_s('avecretailleau.fr, droit à la sécurité dans la Constitution', 'https://www.avecretailleau.fr/projet/mesure/inscrire-le-droit-a-la-securite-dans-la-constitution'),
          _s('Les Républicains, cour disciplinaire de la magistrature (6/06)', 'https://republicains.fr/actualites/2026/06/06/il-faut-creer-une-cour-disciplinaire-de-la-magistrature/')])
_upd('lisnard', 'libertes', [_p('Rétablir le septennat'), _p("Article 11 sans limite thématique et référendum d'initiative populaire à seuil atteignable"),
                             _p("Interdire les Frères musulmans et le voile à l'université"), _p('Contrôle du Conseil constitutionnel limité à la lettre de la Constitution', False)],
     add=[_s('Nouvelle Énergie, programme « Sécurité »', 'https://www.unenouvelleenergie.fr/notre-programme/securite/')])
# école
_upd('melenchon', 'ecole', [_p('Supprimer Parcoursup et MonMaster'), _p('Transport scolaire limité à 15 minutes, écoles à classe unique maintenues'),
                            _p("Scolarité obligatoire jusqu'à 18 ans", True, True), _p('Réduire les effectifs par classe, priorité maternelle et REP', False, True)],
     add=[_s('LFI, note sur les comptes publics (14/10)', 'https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf'),
          _s("L'Express via Orange, meeting de Clermont-Ferrand (11/10)", 'https://actu.orange.fr/politique/presidentielle-2027-suppression-de-parcoursup-droit-de-vote-a-16-ans-jean-luc-melenchon-multiplie-les-propositions-pour-les-jeunes-magic-CNT000002sCYOg.html')])
_upd('glucksmann', 'ecole', [_p('Loi de programmation éducation sur cinq ans : bâti, salaires, effectifs'), _p('Conditionner les aides au privé (10 Md€/an) à la mixité sociale'), _p('Abroger Parcoursup'),
                             _p("Baisser le nombre d'élèves par classe en primaire", False)],
     add=[_s('franceinfo, propositions à Matignon (22/10)', 'https://www.franceinfo.fr/societe/mobilisation-du-17-octobre/reunion-des-partis-a-matignon-sebastien-lecornu-a-fait-perdre-du-temps-au-pays-denonce-manuel-bompard_8249335.html')])
_upd('retailleau', 'ecole', [_p("Sélection à l'entrée de l'université et nouvelle plateforme d'admission au mérite à la place de Parcoursup"),
                             _p("Rétablir un examen d'entrée en sixième"), _p('Fin du passage automatique de classe, décidé par le conseil de classe'),
                             _p('Créer 1 000 établissements publics « libres » autonomes'),
                             _p("Au moins un internat disciplinaire par académie, affectation décidée par le rectorat après des exclusions répétées")],
     add=[_s("Public Sénat, sélection à l'université (14/10)", 'https://www.publicsenat.fr/actualites/politique/crise-lyceenne-bruno-retailleau-veut-une-selection-a-luniversite'),
          _s('avecretailleau.fr, internats disciplinaires', 'https://www.avecretailleau.fr/projet/mesure/retablir-l-evaluation-qui-dit-la-verite-et-la-selection-au')])
_upd('lisnard', 'ecole', [_p("Chèque-éducation progressif (même financement public, école publique ou privée) ; nouveaux enseignants recrutés comme contractuels"),
                          _p("Certificat de fin de primaire conditionnant l'entrée au collège"), _p('Hausse de 20 % des salaires enseignants en cinq ans, contre réorganisation'),
                          _p('Supprimer la carte scolaire')],
     add=[_s('Nouvelle Énergie, programme « Éducation »', 'https://www.unenouvelleenergie.fr/notre-programme/education/'),
          _s('Europe 1, Objectif Élysée 2027 (27/10)', 'https://www.europe1.fr/politique/en-direct-emeutes-parcoursup-primaire-a-droite-ce-quil-faut-retenir-de-linterview-de-david-lisnard-dans-objectif-elysee-2027-1186743')])
_upd('zemmour', 'ecole', [_p("Retour à la dictée, au calcul mental et à la récitation ; autonomie des chefs d'établissement ; concurrence entre public et privé", False),
                          _p("Certificat d'études en fin de primaire", True, True), _p('Classes de niveau au collège', True, True),
                          _p("Interdire toute propagande idéologique à l'école", False, True)],
     add=[_s('Entrevue, émission du 25/10', 'https://entrevue.fr/politique/on-va-vers-une-guerre-civile-eric-zemmour-alerte-sur-le-chaos-en-france/')])
# environnement
_upd('philippe', 'environnement', [_p("Fonds unique d'adaptation au climat de 2 Md€ par an"), _p('Produire un « Canadair français » durant le quinquennat'),
                                   _p("Instaurer une journée nationale d'alerte"), _p("Mêmes aides pour une voiture électrique d'occasion que pour une neuve")],
     add=[_s('Site Édouard Philippe, « Pour une France plus conquérante »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-conquerante')])
_upd('zemmour', 'environnement', [_p("Six EPR d'ici 2035 et quatorze d'ici 2045"), _p('Abroger le marché carbone européen sur les carburants et le chauffage (SEQE 2) avant 2028'),
                                  _p("Fin des financements français et européens à l'éolien", True, True), _p("Abroger l'interdiction des voitures thermiques neuves en 2035", True, True)],
     add=[_s('Reconquête, pétition sur les carburants', 'https://www.stop-hausse-carburant.fr/')])
# économie
OVR[('le-pen', 'economie')] = {'evidence': "IPP (2025) : la baisse CVAE/CFE de 2021 n'a eu aucun effet mesurable sur l'investissement et un impact limité sur la masse salariale. " + RTE,
  'evidence_level': 'mitigee', 'add': [RTE_S, _s('Contre-budget 2027 du groupe RN', 'https://back.deputes-rn.fr/wp-content/uploads/2026/10/GRN-CONTRE-BUDGET-2027-DOSSIER.pdf'), _s("LCP, règle d'or (tribune du 1/10)", 'https://lcp.fr/actualites/budget-comment-fonctionnerait-la-regle-d-or-que-marine-le-pen-veut-faire-adopter-par')],
  'proposals': [_p('Supprimer les subventions aux renouvelables : 5 Md€ dès la 1re année'), _p('Supprimer plus de 120 taxes'),
                _p("Règle d'or budgétaire par référendum : déficit de 4,9 % du PIB en 2027 à 2,4 % en 2033"), _p('Supprimer la CFE, la CVAE et la C3S')]}
_upd('philippe', 'economie', [_p('Heures au-delà de 35 h défiscalisées, zéro cotisation patronale au-delà de 37 h'), _p('Indemnisation chômage ramenée de 18 à 12 mois avant 50 ans'),
                              _p("Règle d'or budgétaire par référendum : déficit à 2 % du PIB en fin de quinquennat"), _p("Supprimer 50 Md€ d'impôts de production contre 50 Md€ d'aides aux entreprises en moins")],
     add=[_s('Site Édouard Philippe, « Pour une France plus prospère »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-prospere'),
          _s('Public Sénat, « deal » de 50 Md€', 'https://www.publicsenat.fr/actualites/economie/entreprises-un-deal-a-250-milliards-deuros-sur-un-quinquennat-que-represente-la-proposition-dedouard-philippe')])
_upd('glucksmann', 'economie', [_p('Taxer le 1 % des plus gros héritages pour hausser les salaires nets'), _p("État d'urgence industriel pour les secteurs menacés par la Chine", False),
                                _p('« Buy European Act » : préférence européenne dans les marchés publics', False, True)],
     add=[_s('LCP, premier meeting (13/06)', 'https://lcp.fr/actualites/gagner-en-2027-raphael-glucksmann-lance-sa-campagne-et-veut-ramener-la-gauche-au-pouvoir')])
OVR[('attal', 'economie')] = {'evidence': IA, 'evidence_level': 'mitigee', 'add': [
    _s('attalpresident.fr, programme « Travail & salaires »', 'https://attalpresident.fr/programme/travail-salaires'),
    _s('AFP via Orange, conférence économique (28/10)', 'https://actu.orange.fr/politique/attal-veut-une-economie-quot-liberale-quot-mais-quot-planifiee-quot-pour-financer-un-quot-capitalisme-de-l-innovation-quot-CNT000002tqRW2.html'),
    _s('attalpresident.fr, lettre aux Français (15/10)', 'https://attalpresident.fr/actualites/gabriel-attal-lettre-aux-francais-plan-finances-publiques')],
  'proposals': [_p('Remplacer le Code du travail par une « Constitution du travail » de quelques principes, le reste négocié par branche et par entreprise'),
                _p("Loi de stabilité fiscale et normative de dix ans votée dès l'été 2027 ; un quart de la charge administrative des entreprises supprimé"),
                _p("Former 20 millions de Français à l'IA d'ici 2030"),
                _p("Plan de 200 Md€ pour la puissance de calcul et l'IA")]}
_upd('retailleau', 'economie', [_p('Supprimer les impôts de production, dans 30 Md€ de baisses pour les entreprises'),
                                _p("Code du travail refondé sur 50 principes, le reste supplétif et renvoyé aux accords d'entreprise ou de branche"),
                                _p('Exonérer de cotisations sociales les heures supplémentaires', False)],
     add=[_s('avecretailleau.fr, code du travail sur 50 principes', 'https://www.avecretailleau.fr/projet/mesure/refonder-le-code-du-travail-sur-50-principes-rendre-le')])
_upd('lisnard', 'economie', [_p('Baisser de 40 Md€ les impôts de production, en commençant par la C3S'), _p('TVA unique à 25 % en douze ans pour baisser les charges'),
                             _p('Contrat de travail unique pour les nouveaux emplois, fusionnant CDI et CDD, indemnités de licenciement progressives'),
                             _p("Interdire de modifier un impôt à la hausse plus d'une fois par législature")],
     add=[_s('Nouvelle Énergie, programme « Réussir une nouvelle ambition française »', 'https://www.unenouvelleenergie.fr/notre-programme/reussir-une-nouvelle-ambition-francaise/'),
          _s('Nouvelle Énergie, « Changer de logiciel fiscal » (16/04)', 'https://www.unenouvelleenergie.fr/changer-de-logiciel-fiscal/')])
_upd('zemmour', 'economie', [_p("Former à l'IA dès l'école ; faire de la France la troisième puissance mondiale de l'IA", False),
                             _p('Baisser de 30 Md€ supplémentaires les impôts de production', True, True), _p("Prime « zéro charge » jusqu'à trois mois de salaire", True, True),
                             _p("Orienter 20 % du Livret A vers l'investissement stratégique", True, True)],
     evidence="IPP (2025) : la baisse des impôts de production de 2021 n'a eu aucun effet mesurable sur l'investissement et un impact limité sur la masse salariale. " + IA,
     add=[IA_S, _s('CNews, discours de rentrée (13/09)', 'https://www.cnews.fr/france/2026-09-13/presidentielle-2027-remigration-intelligence-artificielle-ce-quil-faut-retenir-du')])
# rayonnement
_upd('attal', 'rayonnement', [_p('Part européenne du calcul mondial : de 3 % à 20 %'),
                              _p("Taxes ciblées sur l'acier, les voitures électriques et les panneaux solaires chinois vendus à perte ; contrôle strict des investissements chinois dans les ports, télécoms et centres de données")],
     add=[_s('attalpresident.fr, programme « Frontières »', 'https://attalpresident.fr/programme/frontieres')])
_upd('retailleau', 'rayonnement', [_p('Schengen réservé aux Européens : visas limités au pays qui les délivre, comme règle de droit commun'),
                                   _p("Réduire la contribution française au budget de l'UE par la négociation", False), _p('Intégrer les dépenses de défense dans le calcul de cette contribution', False)],
     add=[_s('Les Républicains, entretien au JDD (2/08)', 'https://republicains.fr/actualites/2026/08/02/lespace-schengen-doit-etre-reserve-aux-europeens/')])

# --- review 24 : études des propositions ajoutées le 29/10 (29/10/2026) ; registre S107 (2), S108, S109, S126 à S132
# Une lecture par type de proposition, le même texte chez tous les candidats qui proposent ce type de mesure (règle n°1), dans l'ordre des
# propositions affichées ; chaque lecture aussi courte que possible (lecture « casseur-payeur » raccourcie pour tous : CASSE plus haut), mais
# aucune lecture n'est retirée pour tenir une longueur : le texte grandit avec le nombre de types de propositions affichées (bloc replié, S142).
# La faisabilité juridique (décision n° 2025-886 DC sur la justice des mineurs) n'entre pas dans ces textes, qui portent sur l'efficacité : S126.
def _ev(cid, th, ev, add=(), drop=(), level=None):
    o = OVR.setdefault((cid, th), {}); o['evidence'] = ev
    if level: o['evidence_level'] = level
    if drop:
        o['drop'] = o.get('drop', []) + list(drop)
        o['add'] = [s for s in o.get('add', []) if not any(d in s['url'] for d in drop)]
    if add: o['add'] = o.get('add', []) + [s for s in add if s['url'] not in {x['url'] for x in o.get('add', [])}]
def _src(label, year, url): return {'label': label, 'year': year, 'url': url}
# sécurité
MIN = "Mineurs jugés comme des adultes : récidive +34 % (États-Unis, 2007)."
MIN_S = _src("CDC, Task Force on Community Preventive Services : transfert des mineurs vers la justice des adultes (MMWR 56, RR-9)", 2007, 'https://www.cdc.gov/mmwr/preview/mmwrhtml/rr5609a1.htm')
CEF = "Centres éducatifs fermés : au moins 41 % des jeunes de nouveau poursuivis dans l'année (DPJJ, 2024) ; efficacité non évaluée (Cour des comptes, 2023)."
CEF_S = _src("Assemblée nationale, rapport d'information n° 1566 sur les centres éducatifs fermés (Cour des comptes 2023, étude DPJJ 2024)", 2025, 'https://www.assemblee-nationale.fr/dyn/17/rapports/cion_fin/l17b1566_rapport-information.pdf')
DECH = "Déchéance de nationalité : effet non évalué."
DECH_S = _src("Ministère de l'Intérieur, réponse à la question écrite n° 19446 sur la déchéance de nationalité (JO du 19/04/2022)", 2022, 'https://questions.assemblee-nationale.fr/dyn/15/questions/QANR5L15QE19446.pdf')
FICH = "Cagoule en manifestation : délit depuis 2019 ; pointage non évalué."
FICH_S = _src("Conseil constitutionnel, décision n° 2019-780 DC, loi « anticasseurs » (délit de dissimulation du visage)", 2019, 'https://www.conseil-constitutionnel.fr/decision/2019/2019780DC.htm')
RECO = "Reconnaissance faciale a posteriori : ≈ 616 000 recherches en 2021 (Sénat, 2022) ; effet non évalué."
RECO_S = _src("Sénat, rapport d'information n° 627 (2021-2022), la reconnaissance biométrique dans l'espace public", 2022, 'https://www.senat.fr/rap/r21-627/r21-6271.pdf')
# RESEAUX et EXPUL raccourcies, même contenu
RESEAUX = "Coupures de réseaux : plus d'actions violentes (Inde, 2019) ; blocage de TikTok en Nouvelle-Calédonie jugé illégal (Conseil d'État, 2025)."
EXPUL = "Expulsions après arrestation : pas de baisse observable de la criminalité (États-Unis, 2014)."
GILL = "Police de proximité : baisse limitée de la délinquance (Gill, 2014), sentiment d'insécurité réduit."
# justice des mineurs (MIN) : même lecture pour Attal, Lisnard et Retailleau ; HEN (courtes peines des adultes) reste chez Philippe et sort
# de la sécurité de Retailleau, dont la proposition porte sur les mineurs ; déchéance de nationalité (DECH) : Retailleau et Zemmour ;
# Miles et Cox vaut pour le « départ » et les expulsions de Zemmour, pas pour la déchéance elle-même
_ev('attal', 'securite', CASSE + " " + MIN + " " + RECO + " " + RESEAUX, add=[MIN_S, RECO_S])
_ev('lisnard', 'securite', MIN + " " + CEF + " " + CASSE + " " + FICH + " " + PLACES, add=[MIN_S, CEF_S, FICH_S])
_ev('retailleau', 'securite', CASSE + " " + MIN + " " + DECH + " " + PP, add=[MIN_S, DECH_S], drop=['chicagounbound.uchicago.edu/jle/vol59/iss3/6'])
_ev('zemmour', 'securite', PP + " " + PLACES + " " + CASSE + " " + DECH + " " + EXPUL, add=[DECH_S, _s('Les Incorrectibles, émission du 25/10', 'https://lesincorrectibles.substack.com/p/eric-zemmour-la-france-face-au-chaos-1'),
    {'label': 'Sénat – rapport plan 15 000 places', 'year': 2023, 'url': 'https://www.senat.fr/rap/r23-037/r23-037_mono.html'}])
_ev('melenchon', 'securite', GILL + " Régulation carcérale : pas d'évaluation française identifiée.")
_ev('glucksmann', 'securite', GILL + " Vidéosurveillance : utile dans 1,1 % des enquêtes (Gormand, gendarmerie).")
# école : Parcoursup (PARC) pour Mélenchon, Glucksmann et Retailleau (suppression comme sélection portent sur l'admission dans le supérieur) ;
# internats disciplinaires (INT, Retailleau) ; chèque-éducation (CHEQ, Lisnard ; pas pour la « concurrence public-privé » de Zemmour, sans mécanisme)
PARC = "Parcoursup : fin du tirage au sort, classements peu transparents, quotas de boursiers peu efficaces (Cour des comptes, 2020)."
PARC_S = _src("Cour des comptes, Un premier bilan de l'accès à l'enseignement supérieur dans le cadre de la loi ORE", 2020, 'https://www.ccomptes.fr/system/files/2020-03/20200227-rapport-premier-bilan-loi-ORE-3.pdf')
INT = "Établissements pour élèves exclus (2010) : résultats souvent décevants, abandonnés (inspection, 2012)."
INT_S = _src("Ministère de l'Éducation nationale, réponse à la question écrite n° 85814 (rapport d'inspection de 2012 sur les établissements de réinsertion scolaire)", 2016, 'https://www.assemblee-nationale.fr/dyn/14/questions/QANR5L14QE85814.pdf')
CHEQ = "Chèque-éducation : niveau en hausse (Suède, 2015) ou en baisse (Louisiane, 2018), tri social accru (Chili, 2006) ; contractuels non évalués."
CHEQ_S = [_src("Böhlmark, Lindahl, écoles indépendantes et chèque scolaire en Suède (IZA DP 6683, Economica 2015)", 2015, 'https://econpapers.repec.org/RePEc:iza:izadps:dp6683'),
          _src("Abdulkadiroglu, Pathak, Walters, chèque scolaire en Louisiane (NBER w21839, AEJ Applied 2018)", 2018, 'https://www.nber.org/papers/w21839'),
          _src("Hsieh, Urquiola, chèque scolaire généralisé au Chili (NBER w10008, Journal of Public Economics 2006)", 2006, 'https://www.nber.org/papers/w10008')]
PETITES = "Petites écoles : regroupements suivis d'une baisse passagère des résultats (Danemark, 2018) ou d'un léger gain (Pays-Bas, 2016)."
# lectures propres à un candidat, raccourcies sans changer leur contenu
MIXITE = "Mixité au privé : non évaluée ; secteurs communs à Paris : évitement du privé de 24 % à 16 % dans l'un (IPP, 2021)."
CARTE = "Carte scolaire assouplie : effet global faible, fuite des collèges défavorisés (DEPP, 2013)."
EX1 = EXAM[:EXAM.index(', mais')] + "."  # première moitié de EXAM, à l'identique
RED = "Redoublement : effet quasi nul, puis négatif à long terme (Cnesco, 2014)."
AUTO = "Autonomie : progrès de collèges en difficulté (Angleterre, 2019), aucun en primaire (2017)."
# Mélenchon : la note du 14/10 reprend la baisse des effectifs (19 élèves par classe en un mandat, « le secondaire public est prioritaire ») ;
# précise et de 2026, elle passe devant le transport scolaire (9/10) ; même date que Parcoursup (même note), qui garde sa place (registre S107)
OVR[('melenchon', 'ecole')]['proposals'] = [_p('Supprimer Parcoursup et MonMaster'),
    _p('Se rapprocher en un mandat de 19 élèves par classe (moyenne européenne), priorité au secondaire public'),
    _p('Transport scolaire limité à 15 minutes, écoles à classe unique maintenues'), _p("Scolarité obligatoire jusqu'à 18 ans", True, True)]
_ev('melenchon', 'ecole', PARC + " " + DD + " " + PETITES, add=[PARC_S])
_ev('glucksmann', 'ecole', DD + " " + SAL + " " + MIXITE + " " + PARC, add=[PARC_S])
_ev('retailleau', 'ecole', PARC + " " + EX1 + " " + RED + " " + AUTO + " " + INT, add=[PARC_S, INT_S])
_ev('lisnard', 'ecole', CHEQ + " " + EXAM + " " + SAL + " " + CARTE, add=CHEQ_S)
# économie : règle d'or (OR, Le Pen et Philippe ; mêmes études que le quiz attal.regle_or), code du travail réduit à des principes (CODE,
# Attal et Retailleau), stabilité fiscale (STAB, Attal et Lisnard), contrat unique (CU, Lisnard) ; impôts de production et heures sup :
# un seul texte pour tous les candidats qui les proposent (IPROD, TEPA)
OR = ("Règle d'or : effet modéré sur les déficits, plus faible avec les meilleures méthodes (30 études, ZEW, 2016) ; "
      "Allemagne, dette de 81 % à 58 % du PIB (2010-2019), 60 Md€ d'emprunts annulés (2023).")
OR_S = [_src("Heinemann, Moessinger, Yeter, règles budgétaires : méta-analyse de 30 études (ZEW DP 16-027)", 2016, 'https://www.zew.de/PU77836'),
        _src("Eurostat, dette publique en % du PIB (gov_10dd_edpt1), Allemagne", 2026, 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10dd_edpt1?geo=DE&unit=PC_GDP&sector=S13&na_item=GD&time=2010&time=2019&time=2024'),
        _src("Cour constitutionnelle fédérale allemande, communiqué n° 101/2023", 2023, 'https://www.bundesverfassungsgericht.de/SharedDocs/Pressemitteilungen/EN/2023/bvg23-101.html')]
IPROD = "Impôts de production : baisse de 2021 sans effet mesurable sur l'investissement (IPP, 2025)."
TEPA = "Heures sup défiscalisées (TEPA) : pas d'effet significatif sur les heures travaillées (IPP, 2012)."
CODE = "Code du travail réduit à des principes : non évalué ; ordonnances de 2017, effet sur l'emploi non mesuré (France Stratégie, 2021)."
CODE_S = [_src("France Stratégie, comité d'évaluation des ordonnances travail, rapport 2021 (présentation, via Le Monde du Droit)", 2021, 'https://www.lemondedudroit.fr/publications/248-etudes-et-documents/78930-comite-evaluation-des-ordonnances-travail-publie-aujourd-hui-son-rapport-d-evaluation-2021.html'),
          _src("France Stratégie, appel à projets de recherche pour évaluer l'effet des ordonnances travail sur l'emploi", 2022, 'https://www.strategie-plan.gouv.fr/files/2025-06/apr_-_ordonnances_travail-presentation_generale.pdf')]
STAB = "Incertitude politique : moins d'investissement et d'emploi (12 pays, 2016) ; règle de stabilité fiscale non évaluée."
STAB_S = _src("Baker, Bloom, Davis, Measuring Economic Policy Uncertainty (NBER w21633, QJE 2016)", 2016, 'https://www.nber.org/papers/w21633')
CU = "CDI à indemnités progressives (Italie, 2015) : 8 % des embauches en CDI dues au licenciement moins coûteux (2018) ; contrat unique non évalué."
CU_S = _src("Sestito, Viviano, coût du licenciement et embauches : la réforme italienne de 2015 (Economic Policy)", 2018, 'https://ideas.repec.org/a/oup/ecpoli/v33y2018i93p101-130..html')
_ev('le-pen', 'economie', RTE + " " + OR + " " + IPROD, add=OR_S)
_ev('philippe', 'economie', TEPA + " Chômage plus court de 12 %, mais emplois peu durables (Dares, 2025). " + OR + " " + IPROD, add=OR_S)
_ev('attal', 'economie', CODE + " " + STAB + " " + IA, add=CODE_S + [STAB_S], drop=['connaissancedesenergies.org/afp/programme-depr-'])  # EPR en « environnement » (S117)
_ev('retailleau', 'economie', IPROD + " " + CODE + " " + TEPA, add=CODE_S)
_ev('lisnard', 'economie', IPROD + " CEPII (2007) : TVA sociale, emplois modestes si ciblée sur les bas salaires, pouvoir d'achat réduit. " + CU + " " + STAB, add=[CU_S, STAB_S])
_ev('zemmour', 'economie', IA + " " + IPROD)
# rayonnement : droits de douane ciblés (mêmes études que le quiz glucksmann.industrie) ; Schengen ; contribution à l'UE (UEU, comme Le Pen) ;
# dépenses de défense (Banque de Finlande, même texte pour Lisnard et Zemmour)
DOUANE = "Droits de douane américains de 2018 : prix des lave-linge +12 %, emploi industriel −1,4 % avec les représailles (États-Unis, 2019)."
DOUANE_S = [_src("Université de Chicago, sur Flaaen, Hortaçsu et Tintelnot (étude publiée dans l'American Economic Review, 2020)", 2019, 'https://news.uchicago.edu/story/what-washing-machines-can-teach-us-about-cost-tariffs'),
            _src("Flaaen et Pierce, Réserve fédérale, FEDS n° 2019-086", 2019, 'https://www.federalreserve.gov/econres/feds/files/2019086pap.pdf')]
SCH = "Visa limité au pays qui le délivre : non évalué ; assouplir les visas accroît l'afflux de touristes de 5 à 25 % (France Stratégie, 2016)."
SCH_S = _src("France Stratégie, Note d'analyse n° 39, Les conséquences économiques d'un abandon des accords de Schengen", 2016, 'https://www.strategie-plan.gouv.fr/files/files/Publications/2016/NA%2039/note_danalyse_ndeg39.pdf')
FIN = "Banque de Finlande (2025) : multiplicateur des dépenses de défense d'environ 0,6 à 1,0 ; effets durables surtout si investissement et R&D."
_ev('attal', 'rayonnement', "Pas d'évaluation publique de cet objectif. " + IA + " " + DOUANE, add=DOUANE_S, level='mitigee')
_ev('retailleau', 'rayonnement', SCH + " " + UEU, add=[SCH_S])
_ev('lisnard', 'rayonnement', FIN)
_ev('zemmour', 'rayonnement', FIN + " " + VED)
# libertés : référendum (même texte pour Attal, Retailleau et Lisnard), seuil du RIP (Retailleau et Lisnard), discipline des magistrats
# (Retailleau et Philippe), droit à la sécurité (Retailleau), vote à 16 ans (Mélenchon), voile et dissolutions (Lisnard)
RIP = "RIP ADP (2019) : environ 1 million de soutiens pour 4,7 millions requis."
RIP_S = _src('Public Sénat – RIP ADP', 2019, 'https://www.publicsenat.fr/actualites/politique/referendum-sur-adp-le-cap-du-million-de-signatures-atteint-148123')
SUISSE = "Suisse : l'usage du référendum va de pair avec une satisfaction démocratique un peu plus forte, sans effet sur le bien-être (2012)."
SECU = "Sécurité : déjà « droit fondamental » dans la loi depuis 1995 (code de la sécurité intérieure) ; effet non évalué."
SECU_S = _src("Conseil constitutionnel, commentaire de la décision n° 2020-889 QPC (droit à la sécurité, loi du 21 janvier 1995)", 2021, 'https://www.conseil-constitutionnel.fr/sites/default/files/as/root/bank_mm/decisions/2020889qpc/2020889qpc_ccc.pdf')
CSM = "Discipline des magistrats : 254 plaintes de justiciables en 2025, une seule renvoyée devant le conseil de discipline (CSM, 2026)."
CSM_S = _src("Conseil supérieur de la magistrature, rapport d'activité 2025 (chiffres clés)", 2026, 'https://www.conseil-superieur-magistrature.fr/sites/default/files/pdf/CSM_RA_2025_Web_compress%C3%A9_0.pdf')
VOTE16 = "Vote à 16 ans : les 16-17 ans votent plus que les 18-20 ans en Autriche (Vienne 2010 : 64 % contre 56 %) et en Écosse (2014) ; effet durable peu mesuré."
VOTE16_S = [_src("Zeglovits, Aichholzer, vote à 16 ans en Autriche (Journal of Elections, Public Opinion and Parties)", 2014, 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4864896/'),
            _src("J. Curtice, What Scotland Thinks : participation des 16-17 ans au référendum de 2014 (sondage ICM pour la Commission électorale)", 2014, 'https://www.whatscotlandthinks.org/2014/12/many-16-17-year-olds-voted/')]
VOILE = ("Voile interdit à l'école : diplômes des filles de culture musulmane en hausse après 1994 (IZA, 2019) ; après 2004, effet nul ou négatif "
         "selon les études (APSR, 2020) ; aucune étude sur l'université ni sur les dissolutions.")
VOILE_S = [_src("Maurin, Navarrete, l'interdiction du voile à l'école (IZA DP 12645)", 2019, 'https://docs.iza.org/dp12645.pdf'),
           _src("Abdelgadir, Fouka, la loi de 2004 sur le voile et l'intégration (American Political Science Review)", 2020, 'https://ideas.repec.org/a/cup/apsrev/v114y2020i3p707-723_10.html')]
RIC = "RIC : peu d'études causales. En Suisse, initiatives rarement adoptées mais qui structurent le débat ; risque d'usage restrictif des libertés signalé (AMU, 2024)."
_ev('attal', 'libertes', SUISSE)
_ev('retailleau', 'libertes', RIP + " " + SUISSE + " " + SECU + " " + CSM, add=[SECU_S, CSM_S])
_ev('lisnard', 'libertes', RIP + " " + SUISSE + " " + VOILE, add=[RIP_S] + VOILE_S)
_ev('philippe', 'libertes', "Aucune évaluation empirique identifiée de l'effet des ordonnances ou du lien parquet-exécutif sur l'efficacité de l'action publique. " + CSM, add=[CSM_S])
_ev('melenchon', 'libertes', VOTE16 + " " + RIC, add=VOTE16_S)
# environnement : aides aux voitures électriques des ménages modestes (VE : Philippe, Attal, Glucksmann) ; SEQE 2 (Zemmour) ;
# lectures de la Cour des comptes (EPR) et de RTE : même texte pour tous les candidats qui proposent ce type de mesure
SEQE = "Marché carbone des carburants : +10 à 15 c€ par litre (Institut Montaigne, 2025) ; taxe carbone suédoise : émissions des transports −11 % (2019)."
SEQE_S = [_src("Institut Montaigne, Transition des mobilités : anatomie d'une impasse (note d'éclairage, octobre 2025)", 2025, 'https://institutmontaigne.org/ressources/pdfs/publications/note-transition-des-mobilites-anatomie-d-une-impasse.pdf'),
          _src("Andersson, Carbon Taxes and CO2 Emissions: Sweden as a Case Study (AEJ: Economic Policy)", 2019, 'https://www.aeaweb.org/articles?id=10.1257/pol.20170144')]
VE = ("Leasing social 2024 : 47 000 ménages aidés, sans bilan CO₂ publié. Aide aux ménages modestes pour un véhicule électrique neuf ou d'occasion : "
      "demande très sensible au prix (Californie, 2022).")
VE_S = [_src("Muehlegger, Rapson, aides aux véhicules électriques des ménages modestes en Californie (NBER w25359, Journal of Public Economics 2022)", 2022, 'https://www.nber.org/papers/w25359'),
        _src('Connaissance des énergies, bilan leasing', 2025, 'https://www.connaissancedesenergies.org/leasing-social-un-levier-perenne-pour-aider-les-menages-les-plus-modestes')]
_ev('zemmour', 'environnement', EPR + " " + SEQE + " " + RTE, add=SEQE_S)
_ev('philippe', 'environnement', "HCC 2026 : France « pas prête », plan d'adaptation sous-financé, risque de « maladaptation ». Aucune évaluation d'un fonds unique d'adaptation. " + VE,
    add=VE_S, level='mitigee')
_ev('attal', 'environnement', EPR + " HCC 2026 : émissions −2,1 % en 2025, un rythme qui doit au moins doubler ; leasing social et MaPrimeRénov' jugés sous-dimensionnés. " + VE, add=VE_S)
_ev('glucksmann', 'environnement', VE + " RTE : scénarios combinant nouveaux réacteurs et renouvelables les plus compétitifs.", add=VE_S[:1])
_ev('le-pen', 'environnement', RTE)
_ev('retailleau', 'environnement', EPR + " " + RTE)

# --- review 25 : veille d'actualité du 15 au 29/10 et registre du 29/10 (29/10/2026) ; registre S106, S107, S116, S130 et suivants
# Règles (décisions du porteur du 29/10) : seule une source qui parle pour le candidat compte (une seule reprise de presse sans citation :
# registre) ; une demande au Gouvernement en place d'utiliser un outil existant n'est pas une proposition de programme (Attal : garde statique
# des bâtiments publics retirée) ; au plus 5 propositions par thème, d'abord celles de 2026, puis les précises, puis les plus récentes,
# l'ordre affiché étant gardé à égalité ou à date inconnue (une proposition ajoutée prend sa place selon la règle, sans réordonner les autres) ;
# une proposition redite ou précisée remplace son texte. Même lecture pour un même type de proposition : voile (VOILE0), Parcoursup (PARC),
# groupes de niveau et fin du collège unique (GN, Attal, Retailleau, Lisnard, Zemmour), peines planchers (PP), règle d'or (OR),
# contribution à l'UE (UEU). Pas de lecture tant qu'aucune étude n'est vérifiée (exclusion d'élèves, régularisation, prix agricoles,
# garantie des loyers, prix de l'électricité, DPE, formation des médecins, évaluation des formations) : registre.
VOILE0 = VOILE[:VOILE.index(' ; aucune étude')]
assert VOILE0 + " ; aucune étude sur l'université ni sur les dissolutions." == VOILE
GN = "Groupes de niveau : pas d'amélioration des résultats, et les élèves faibles risquent de perdre l'effet des pairs selon l'OCDE (PISA 2022)."
GN_S = {'label': "L'Etudiant – groupes de niveau et recherche", 'year': 2024, 'url': 'https://www.letudiant.fr/educpros/enquetes/lefficacite-des-groupes-de-niveau-contestee-par-les-chercheurs.html'}
assert OVR[('zemmour', 'ecole')]['evidence'] == EXAM + " " + GN  # lecture déjà écrite chez Zemmour, reprise mot pour mot
EU1510 = 'https://www.europe1.fr/politique/en-direct-interdiction-du-voile-ia-exclusion-des-eleves-responsables-de-degradations-ce-quil-faut-retenir-de-linterview-de-marine-le-pen-dans-objectif-elysee-2027-1151948'
ATT_BB = 'https://attalpresident.fr/actualites/gabriel-attal-debat-avec-les-francais-a-blois-et-a-bourges'
# Le Pen : voile (15/10), exclusion des élèves qui dégradent et réforme de Parcoursup (15/10) ; indicateur de déficit précisé (S107, point 5)
_upd('le-pen', 'libertes', [_p('Élire les députés à la proportionnelle avec prime majoritaire'), _p('Inscrire la « communauté nationale » dans la Constitution'), _p("Interdire progressivement le voile, d'abord à l'université, dans les fédérations sportives et les bâtiments publics, par référendum"), _p("Instaurer le référendum d'initiative citoyenne", True, True)])
_ev('le-pen', 'libertes', VOILE0 + " ; aucune étude sur l'université, le sport ni les bâtiments publics. " + RIC, add=VOILE_S + [_s('Europe 1, Objectif Élysée 2027 (15/10)', EU1510)], level='mitigee')
_upd('le-pen', 'ecole', [_p('Exclure de leur lycée ou de leur université les élèves de plus de 16 ans qui dégradent ou menacent'), _p('Réformer Parcoursup : vœux à la fin du 2e trimestre, critères de chaque formation rendus publics'), _p('Uniforme obligatoire du primaire à la troisième', True, True), _p('Dédoublement étendu à tous les CP et grandes sections', True, True), _p('Salaires des enseignants +3 % par an', True, True)])
_ev('le-pen', 'ecole', PARC + " " + OVR[('le-pen', 'ecole')]['evidence'], add=[PARC_S, _s('Europe 1, Objectif Élysée 2027 (15/10)', EU1510),
    _s('CNews, Le Pen et la jeunesse (15/10)', 'https://www.cnews.fr/france/2026-10-15/parcoursup-aides-pour-les-transports-que-propose-concretement-marine-le-pen-en')])
o = OVR[('le-pen', 'economie')]; o['indicator'] = "Déficit public sous 3 % du PIB en 2030 (objectif ; plafond de sa règle d'or : 3,9 %)"
o['add'].append(_s('Europe 1, objectif de déficit (6/10)', 'https://www.europe1.fr/politique/budget-2027-marine-le-pen-promet-140-milliards-deuros-nets-deconomies-dici-2032-pour-eviter-a-la-france-le-defaut-de-paiement-1126400'))
# Mélenchon : contribution à l'UE comme levier (deux médias reconnus, sans citation : intention ; les 5 Md€ restent à confirmer, S001)
_upd('melenchon', 'rayonnement', [_p("Sortir de l'OTAN, en commençant par son commandement intégré"), _p("Créer un pôle public de l'armement, acheter du matériel français", False), _p("Aucune intervention militaire sans mandat de l'ONU", False), _p("Se servir de la contribution française au budget de l'UE comme levier de négociation", False)],
     add=[_s("LCP, contribution de la France à l'UE (24/10)", 'https://lcp.fr/actualites/taxer-les-multinationales-pour-financer-l-europe-le-debat-est-relance-444232'),
          _s("Toute l'Europe, futur budget de l'UE (16/10)", 'https://www.touteleurope.eu/fonctionnement-de-l-ue/chronique-radio-pourquoi-le-futur-budget-de-l-ue-suscite-t-il-autant-de-debats/')])
_ev('melenchon', 'rayonnement', VED + " " + UEU)
# Philippe : orientation et islamisme (site officiel) ; propositions de sécurité du 27/10 connues par une seule reprise sans citation : registre
_upd('philippe', 'ecole', [_p('+20 % de rémunération moyenne des enseignants sur le quinquennat'), _p('Réduire les effectifs des classes grâce à la baisse démographique', False), _p('Amende de responsabilisation scolaire des parents, prononcée par le maire'), _p("Refonder l'orientation en fin de collège et au lycée", False)],
     add=[_s('Site Édouard Philippe, « Pour une France plus attentive à ses enfants »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-attentive-a-ses-enfants')])
_upd('philippe', 'libertes', [_p("Une vingtaine d'ordonnances, session extraordinaire en juillet 2027"), _p('Instructions individuelles du garde des Sceaux aux procureurs'), _p('Réviser la composition du CSM, « devoir de redevabilité » envers les victimes', False), _p("Combattre l'islamisme et les organisations affiliées aux Frères musulmans", False)])
# Glucksmann : Parcoursup précisé (26/10) ; régularisation des travailleurs sans papiers des secteurs en tension (intention, sans nombre : S113)
_upd('glucksmann', 'ecole', [_p('Loi de programmation éducation sur cinq ans : bâti, salaires, effectifs'), _p('Conditionner les aides au privé (10 Md€/an) à la mixité sociale'), _p("Supprimer Parcoursup et le remplacer après des états généraux de l'orientation"), _p("Baisser le nombre d'élèves par classe en primaire", False)],
     add=[_s('LCP, Parcoursup et les candidats (26/10)', 'https://lcp.fr/actualites/parcoursup-suppression-remplacement-reforme-ce-que-proposent-les-candidats-a-la')])
_upd('glucksmann', 'economie', [_p('Taxer le 1 % des plus gros héritages pour hausser les salaires nets'), _p("État d'urgence industriel pour les secteurs menacés par la Chine", False), _p("Régulariser les travailleurs sans papiers des secteurs qui manquent de main-d'œuvre", False), _p('« Buy European Act » : préférence européenne dans les marchés publics', False, True)],
     add=[_s('France Inter, Franc-jeu (30/08)', 'https://www.radiofrance.fr/franceinter/podcasts/franc-jeu/franc-jeu-du-dimanche-30-aout-2026-6196033')])
# Attal : groupes de niveau ajoutés à la ligne du « Choc des savoirs », évaluation des formations du supérieur, Parcoursup (intention, 10/10),
# formation des médecins, garantie des loyers, prix de l'électricité, prix agricoles ; garde statique retirée (demande au Gouvernement en place)
_upd('attal', 'ecole', [_p('Moins de 20 élèves par classe en primaire'), _p("Enseignants : +200 € net par mois, jusqu'à 500 € en milieu de carrière"), _p("Groupes de niveau et méthode de Singapour ; certificat d'études pour entrer au collège, brevet obligatoire pour entrer au lycée"), _p('Évaluer licences et masters tous les trois ans (décrochage, insertion) ; réorienter ou fermer les filières les moins performantes'), _p('Réformer Parcoursup (mentorat, tutorat, stages), sans retour au tirage au sort', False)])
_ev('attal', 'ecole', DD + " " + SAL + " " + GN + " " + EXAM + " " + PARC, add=[GN_S, PARC_S,
    _s('attalpresident.fr, face aux lycéens (6/10)', 'https://attalpresident.fr/actualites/gabriel-attal-face-aux-lyceens-il-faut-un-president-qui-comprenne-la-jeunesse'),
    _s('attalpresident.fr, mesures pour la jeunesse (10/10)', 'https://attalpresident.fr/actualites/gabriel-attal-presente-ses-mesures-pour-la-jeunesse-et-l-avenir-de-la-france'),
    _s('attalpresident.fr, France Info (15/10)', 'https://attalpresident.fr/actualites/gabriel-attal-france-info-ecouter-la-jeunesse')])
_upd('attal', 'sante', [_p("Porter à 20 000 le nombre de médecins formés « dans les années qui viennent », sans régulation de l'installation"), _p('Élargir les compétences des pharmaciens et autres soignants non médecins', False), _p("Assistant médical fondé sur l'IA accessible à tous les Français", False), _p('Plan massif pour la santé mentale et la psychiatrie', False)],
     add=[_s('attalpresident.fr, Blois et Bourges (5/10)', ATT_BB)])
_upd('attal', 'logement', [_p('Loi de programmation sur cinq ans pour la rénovation énergétique'), _p('Intégrer le logement intermédiaire dans les quotas SRU des communes'), _p('Garantie universelle des loyers et nouvelles résidences universitaires pour les étudiants et les jeunes actifs'), _p('Simplifier le ZAN pour faciliter la construction', False)],
     add=[_s('attalpresident.fr, Blois et Bourges (5/10)', ATT_BB)])
_upd('attal', 'environnement', [_p('Sécuriser 14 EPR et viser un réacteur par an'), _p("Tripler le rythme de baisse des émissions : 5 % par an d'ici 2030"), _p("Leasing social étendu aux voitures électriques d'occasion"), _p("Garantir la stabilité des prix de l'électricité pendant dix ans", False)],
     add=[_s('attalpresident.fr, chez Mistral AI (28/10)', 'https://attalpresident.fr/actualites/gabriel-attal-recu-chez-mistral-ai-arthur-mensch-intelligence-artificielle')])
_upd('attal', 'economie', [_p('Remplacer le Code du travail par une « Constitution du travail » de quelques principes, le reste négocié par branche et par entreprise'), _p("Loi de stabilité fiscale et normative de dix ans votée dès l'été 2027 ; un quart de la charge administrative des entreprises supprimé"), _p("Former 20 millions de Français à l'IA d'ici 2030"), _p("Plan de 200 Md€ pour la puissance de calcul et l'IA"), _p('Prix agricoles : coûts de production établis et indexés par filière, vente en dessous interdite')],
     add=[_s('attalpresident.fr, Blois et Bourges (5/10)', ATT_BB)])
_upd('attal', 'securite', [_p("Faire payer les dégâts aux casseurs (« Tu casses, tu répares ») : responsabilité automatique des deux parents d'un mineur"), _p("Comparution immédiate dès 16 ans et fin de l'excuse de minorité automatique pour les mineurs récidivistes"), _p('Reconnaissance faciale et IA pour identifier les casseurs'), _p('Bloquer temporairement et de façon ciblée certains réseaux sociaux pendant les émeutes', False), _p("Supprimer le juge d'application des peines", True, True)])
# Retailleau : fin du collège unique (examen d'entrée et groupes de niveau, même mesure du programme), laïcité (programme constitutionnel
# présenté le 3/09 : la cour disciplinaire de la magistrature, 6/06, la moins récente, sort de l'affichage, S106), électricité, DPE,
# règle d'or de 2011 par référendum dans les cent jours (12/10) et négociations agricoles (11/09)
_upd('retailleau', 'ecole', [_p("Sélection à l'entrée de l'université et nouvelle plateforme d'admission au mérite à la place de Parcoursup"), _p("Fin du collège unique : examen d'entrée en sixième et groupes de niveau"), _p('Fin du passage automatique de classe, décidé par le conseil de classe'), _p('Créer 1 000 établissements publics « libres » autonomes'), _p('Au moins un internat disciplinaire par académie, affectation décidée par le rectorat après des exclusions répétées')])
_ev('retailleau', 'ecole', PARC + " " + EX1 + " " + GN + " " + RED + " " + AUTO + " " + INT, add=[GN_S,
    _s('Public Sénat, HEC Débats (27/10)', 'https://www.publicsenat.fr/actualites/politique/nous-allons-vivre-un-moment-historique-bruno-retailleau-appelle-la-jeunesse-a-prendre-part-a-la-pre')])
_upd('retailleau', 'libertes', [_p('Référendum législatif étendu à tout le champ de la loi (article 11)'), _p('Seuil du RIP abaissé à environ 2,5 millions de signatures'), _p('Surmonter une censure du Conseil constitutionnel par référendum ou Congrès'), _p('Inscrire le droit à la sécurité dans la Constitution, à égalité avec les libertés fondamentales'), _p('Laïcité définie dans la Constitution ; neutralité du service public étendue aux usagers par la loi')])
_ev('retailleau', 'libertes', RIP + " " + SUISSE + " " + SECU, drop=[CSM_S['url'], 'republicains.fr/actualites/2026/06/06/il-faut-creer-une-cour-disciplinaire'],
    add=[_s('avecretailleau.fr, laïcité dans la Constitution', 'https://www.avecretailleau.fr/projet/mesure/inscrire-la-laicite-et-nos-racines-dans-la-constitution')])
_upd('retailleau', 'environnement', [_p('Commander huit EPR2 supplémentaires dans les deux premières années'), _p('Fin des subventions aux nouvelles installations éoliennes et photovoltaïques'), _p("Mobiliser jusqu'à 4 GW de nouvelles capacités hydroélectriques"), _p("Prix de l'électricité indexé sur les coûts du nucléaire : contrat pour différence entre EDF et les fournisseurs (prix fixé par la CRE)")],
     add=[_s("avecretailleau.fr, prix de l'électricité", 'https://www.avecretailleau.fr/projet/mesure/stabiliser-le-prix-de-l-electricite')])
_upd('retailleau', 'logement', [_p('Un million de logements supplémentaires en cinq ans'), _p("Intérêts d'emprunt déductibles à 50, 75 ou 100 % selon le nombre d'enfants"), _p("Supprimer le ZAN et l'encadrement des loyers"), _p('Supprimer les interdictions de louer liées au DPE (classes G, F puis E), le DPE devenant informatif')],
     add=[_s('avecretailleau.fr, interdictions de louer liées au DPE', 'https://www.avecretailleau.fr/projet/mesure/lever-les-interdictions-de-louer-liees-au-dpe')])
_upd('retailleau', 'economie', [_p('Supprimer les impôts de production, dans 30 Md€ de baisses pour les entreprises'), _p("Code du travail refondé sur 50 principes, le reste supplétif et renvoyé aux accords d'entreprise ou de branche"), _p("Référendum dans les cent jours sur la règle d'or de 2011 : plafond de dépenses annuel inscrit dans la Constitution"), _p("Négociations agricoles : part des matières premières non négociable, date butoir au 31 décembre, enseignes responsables de leurs centrales d'achat"), _p('Exonérer de cotisations sociales les heures supplémentaires', False)])
_ev('retailleau', 'economie', IPROD + " " + CODE + " " + OR + " " + TEPA, add=OR_S + [
    _s('Fiches presse « Rétablir l\'ordre dans les comptes publics » (12/10), fiche 15', 'https://www.avecretailleau.fr/api/media/file/20261011_Fiches_presse_comptes_publics_mise_en_page%20(1).pdf'),
    _s('avecretailleau.fr, négociations commerciales agricoles', 'https://www.avecretailleau.fr/projet/mesure/encadrer-les-negociations-et-controler-les-importations')])
# Lisnard : peines planchers (23/10 ; « Perpétuité réelle et fin du non-cumul des peines », la moins récente, sort de l'affichage, S106),
# préambule de la Constitution (citation directe, Europe 1, 27/10 : S107, point 3), collège unique (intention, même lecture GN), Mercosur
_upd('lisnard', 'securite', [_p('Majorité pénale à 16 ans, excuse de minorité réduite (de 50 % à 20 % de la peine), établissements disciplinaires fermés'), _p("Faire payer les dégâts aux casseurs : déduits de leurs aides sociales s'ils ne sont pas solvables"), _p('Fichier des casseurs avec obligation de pointer pendant les manifestations ; cagoule interdite, circonstance aggravante'), _p('Rétablir les peines planchers pour les récidivistes'), _p('Construire 20 000 places de prison')])
_ev('lisnard', 'securite', MIN + " " + CEF + " " + CASSE + " " + FICH + " " + PP + " " + PLACES, add=[IPP_PP,
    _s('Nouvelle Énergie, entretien au Figaro Magazine (23/10)', 'https://www.unenouvelleenergie.fr/stop-a-lincompetence-et-a-la-pretention-dune-technocratie-depassee')])
_upd('lisnard', 'libertes', [_p('Rétablir le septennat'), _p("Article 11 sans limite thématique et référendum d'initiative populaire à seuil atteignable"), _p("Interdire les Frères musulmans et le voile à l'université"), _p("Le préambule de la Constitution ne pourrait plus servir à censurer une loi ; s'il est invoqué, référendum")],
     add=[_s('Europe 1, loi « casseurs-payeurs » (27/10)', 'https://www.europe1.fr/politique/loi-casseurs-payeurs-la-societe-na-plus-a-subventionner-ceux-qui-la-detruisent-fustige-david-lisnard-1187322')])
_upd('lisnard', 'ecole', [_p('Chèque-éducation progressif (même financement public, école publique ou privée) ; nouveaux enseignants recrutés comme contractuels'), _p("Certificat de fin de primaire conditionnant l'entrée au collège"), _p('Hausse de 20 % des salaires enseignants en cinq ans, contre réorganisation'), _p('Supprimer la carte scolaire'), _p("Revenir sur le collège unique et repenser l'orientation", False)])
_ev('lisnard', 'ecole', CHEQ + " " + EXAM + " " + SAL + " " + CARTE + " " + GN, add=[GN_S])
_upd('lisnard', 'rayonnement', [_p("Réviser l'article 55 de la Constitution sur la primauté du droit européen"), _p('Hausser le budget des armées, combat aérien souverain autour du Rafale F5', False), _p("Revenir sur l'accord franco-algérien de 1968"), _p("Accord UE-Mercosur : en exclure l'élevage ou imposer des clauses miroirs", False)],
     add=[_s("Nouvelle Énergie, grand entretien de l'écologie (27/10)", 'https://www.unenouvelleenergie.fr/lenergie-doit-reconcilier-lindustrie-et-lecologie/')])
# Zemmour : examens d'entrée en sixième et en seconde (13/10, version de 2026 du certificat de fin de primaire), exclusion des élèves violents
_upd('zemmour', 'ecole', [_p("Examen d'entrée en sixième et en seconde ; « véritable baccalauréat »"), _p("Exclure les élèves violents, sans obligation pour l'État de les rescolariser"), _p("Retour à la dictée, au calcul mental et à la récitation ; autonomie des chefs d'établissement ; concurrence entre public et privé", False), _p('Classes de niveau au collège', True, True), _p("Interdire toute propagande idéologique à l'école", False, True)],
     add=[_s('CNews, Zemmour et le niveau scolaire (13/10)', 'https://www.cnews.fr/france/2026-10-13/niveau-scolaire-francais-que-propose-eric-zemmour-pour-retablir-la-meilleure')])
# S130 : leasing social, chiffre officiel du Gouvernement (« environ 50 000 commandes ») à la place des 47 000 ménages d'un site d'information,
# même phrase pour Philippe, Attal et Glucksmann
VE0 = VE; VE = VE.replace("47 000 ménages aidés", "environ 50 000 voitures commandées"); assert VE != VE0
LEAS_S = _src("Assemblée nationale, question écrite n° 810, réponse du Gouvernement (JO, 15/07/2025)", 2025, 'https://www.assemblee-nationale.fr/dyn/17/questions/QANR5L17QE810')
for _c in ('philippe', 'attal', 'glucksmann'):
    _e = OVR[(_c, 'environnement')]['evidence']; assert _e.count(VE0) == 1, _c
    _ev(_c, 'environnement', _e.replace(VE0, VE), add=[LEAS_S], drop=['connaissancedesenergies.org/leasing-social'])

# --- review 30 : registre du 31/10 (31/10/2026) ; décisions du porteur du 31/10, chaque étude et chaque citation relues à la source le 31/10
# Propositions ajoutées (règle d'ordre : celles de 2026 d'abord, les précises avant les intentions, puis les plus récentes ; 5 au plus par thème ;
# ce qui sort : registre S106) : Glucksmann, plan de sortie de crise du 22/10 (document du candidat publié par le compte officiel de Place
# publique) ; Philippe, interdiction de paraître et pointage, reconnaissance faciale (deux sources chacune, S136) ; Le Pen, allocations familiales
# des familles de délinquants récidivistes (pétition du RN, octobre 2026). Attal : blocage des réseaux sociaux retiré (demande d'utiliser un outil
# présenté par le camp comme existant, règle S134 ; S135) ; la reconnaissance faciale, qui exige une loi nouvelle, reste, avec la même lecture que
# chez Philippe. Lectures nouvelles, le même texte pour toutes les propositions du même type : Egalim (Attal, Retailleau), formation des médecins
# (Attal, Lisnard, Philippe), orientation (Philippe, Lisnard), régularisation par le travail (Glucksmann), SMIC (Glucksmann, comme Mélenchon),
# pointage (Philippe, Lisnard), services numériques (Glucksmann). Lectures corrigées après lecture du texte intégral (S128 : STAB, OR, VOILE ;
# S127 : INT « mitigés »), sources primaires (GN : OCDE ; CODE : rapport de France Stratégie ; DD : document de travail de la DEPP ; CEF, SECU).
def _jev(cid, th):
    """Texte « évidence » d'un thème tel que lu dans data/life-*.json (dernier fichier qui le contient, comme merge)."""
    ev = None
    for f in ('life-a.json', 'life-b.json', 'life-eco.json'):
        for t in J(f)['life'].get(cid, []):
            if t['theme'] == th: ev = html.unescape(t.get('evidence') or '')
    assert ev, (cid, th); return ev
def _rep(cid, th, old, new):
    o = OVR[(cid, th)]; assert o['evidence'].count(old) == 1, (cid, th, old); o['evidence'] = o['evidence'].replace(old, new)
GPLAN_S = _s('Place publique, plan de sortie de crise du candidat (22/10)', 'https://bsky.app/profile/placepublique.bsky.social/post/3myhxt47cic2k')
# sécurité
POINT = "Pointage lors des manifestations : non évalué."
FICH2 = "Cagoule en manifestation : délit depuis 2019. " + POINT  # FICH coupée en deux phrases, même contenu ; la seconde vaut aussi pour Philippe
assert FICH == "Cagoule en manifestation : délit depuis 2019 ; pointage non évalué."
_rep('lisnard', 'securite', FICH, FICH2)
CEF_S2 = _src("Cour des comptes, Les centres éducatifs fermés et les établissements pénitentiaires pour mineurs (observations définitives S2023-0733)", 2023, 'https://www.ccomptes.fr/sites/default/files/2023-10/20231016-S2023-0733-Centres-educatifs-fermes-etablissements-penitentiaires-pour-mineurs.pdf')
_ev('lisnard', 'securite', OVR[('lisnard', 'securite')]['evidence'], add=[CEF_S2])
o = OVR[('philippe', 'securite')]; assert [p['text'] for p in o['proposals']][-1] == "Supprimer le juge d'application des peines"
o['proposals'] = o['proposals'][:-1] + [_p("Interdire à des casseurs de paraître dans certains lieux et les obliger à pointer au commissariat avant les manifestations"),
                                        _p("Autoriser la reconnaissance faciale et des techniques de marquage pour identifier les casseurs")]
_ev('philippe', 'securite', o['evidence'] + " " + POINT + " " + RECO, add=[RECO_S,
    _s("Site Édouard Philippe, réaction aux émeutes (BFMTV-Le Figaro, 19/10)", 'https://www.edouardphilippe.fr/actualites/edouard-philippe-reagit-aux-emeutes-sur-bfmtv'),
    _s('Journal du Net, Philippe à Charleville-Mézières (22/10)', 'https://www.journaldunet.com/business/action-publique/1557005-edouard-philippe-presente-ses-propositions-pour-les-familles-et-defend-ses-positions-securitaires/')])
o = OVR[('attal', 'securite')]; t0 = [p['text'] for p in o['proposals']]
assert t0[3] == 'Bloquer temporairement et de façon ciblée certains réseaux sociaux pendant les émeutes' and t0[2] == 'Reconnaissance faciale et IA pour identifier les casseurs'
o['proposals'] = o['proposals'][:3] + o['proposals'][4:]
_rep('attal', 'securite', " " + RESEAUX, "")
_ev('attal', 'securite', o['evidence'], drop=['lesactusdunet.com', 'papers.ssrn.com/abstract=3330413', 'next.ink/178412'])
o = OVR[('le-pen', 'securite')]; assert len(o['proposals']) == 4 and o['proposals'][2]['old'] and not o['proposals'][1]['old']
o['proposals'] = o['proposals'][:2] + [_p('Suspendre les allocations familiales des familles de délinquants récidivistes')] + o['proposals'][2:]
o['add'].append(_s('Rassemblement national, pétition « Face au chaos, la France en ordre » (octobre)', 'https://rassemblementnational.fr/petition/face-au-chaos-la-france-en-ordre'))
DSA = "Plateformes : amendes jusqu'à 6 % du chiffre d'affaires mondial et suspension temporaire du service déjà prévues par le règlement européen sur les services numériques ; effet non évalué."
DSA_S = _src("Commission européenne, le cadre d'application de la législation sur les services numériques (règlement de 2022)", 2022, 'https://digital-strategy.ec.europa.eu/fr/policies/dsa-enforcement')
assert OVR[('glucksmann', 'securite')]['evidence'] == GILL + " Vidéosurveillance : utile dans 1,1 % des enquêtes (Gormand, gendarmerie)."
_upd('glucksmann', 'securite', [_p("Mettre fin aux armes mutilantes dans les manifestations et réformer la doctrine du maintien de l'ordre"),
                                _p("Plateformes : retrait en temps réel des contenus appelant à la destruction, sous peine d'amendes jusqu'à 6 % du chiffre d'affaires ou de suspension"),
                                _p("Responsabilité de l'État pour les dégâts, avec recours contre les auteurs ; indemnisation accélérée des commerçants, artisans et particuliers"),
                                _p('Police de proximité modernisée, équipes mobiles de prévention', False, True), _p('Doubler les Maisons du droit et de la justice', True, True)])
_ev('glucksmann', 'securite', DSA + " " + CASSE + " " + GILL, add=[GPLAN_S, DSA_S] + CASSE_S, drop=['police.be/5337/node/19373'])
# santé : formation des médecins (MED) ; Glucksmann, dépistage (plan du 22/10, sans étude)
MED = "Former plus de médecins : des études qui durent jusqu'à 12 ans, et une hausse qui ne garantit pas leur répartition sur le territoire (Cour des comptes, 2024)."
MED_S = _src("Cour des comptes, L'accès aux études de santé, quatre ans après la réforme", 2024, 'https://www.ccomptes.fr/sites/default/files/2024-12/20241211-Lacces-aux-%C3%A9tudes-de-sante.pdf')
_ev('attal', 'sante', MED + " " + _jev('attal', 'sante'), add=[MED_S])
_ev('lisnard', 'sante', MED + " " + _jev('lisnard', 'sante'), add=[MED_S])
_ev('philippe', 'sante', _jev('philippe', 'sante').replace(" Propositions non chiffrées.", " " + MED + " Propositions non chiffrées."), add=[MED_S])
assert MED in OVR[('philippe', 'sante')]['evidence']
_upd('glucksmann', 'sante', [_p('Consultations gratuites de dépistage en santé à 16 et à 20 ans'),
                             _p('Maisons de santé, permanences mobiles, centres de petites urgences', False, True),
                             _p('Fin de la T2A : financement hospitalier global pluriannuel', True, True),
                             _p('Plan de prévention hors ONDAM : cancers, cardiovasculaire, diabète', True, True)], add=[GPLAN_S])
# école : orientation (ORIENT, Philippe et Lisnard) ; groupes de niveau (GN) : source primaire de l'OCDE à la place de la reprise de presse ;
# classes dédoublées (DD) : document de travail officiel de la DEPP ajouté ; internats disciplinaires (INT) : « mitigés », texte des inspections
ORIENT = "Orientation : des réunions avec le chef d'établissement pour les élèves faibles de 3e et leurs parents ont réduit redoublement et décrochage de 25 à 40 % (essai aléatoire, France, 2017)."
ORIENT_S = _src("Goux, Gurgand, Maurin, réunions d'orientation en fin de collège, essai aléatoire dans l'académie de Versailles (Economic Journal)", 2017, 'https://www.parisschoolofeconomics.eu/publications-hal/adjusting-your-dreams-high-school-plans-and-dropout-behaviour')
_ev('philippe', 'ecole', OVR[('philippe', 'ecole')]['evidence'] + " " + ORIENT, add=[ORIENT_S])
_ev('lisnard', 'ecole', OVR[('lisnard', 'ecole')]['evidence'] + " " + ORIENT, add=[ORIENT_S])
GN_S2 = _src("OCDE, Résultats du PISA 2022 (volume II), chapitre 4, p. 158-159 : groupes de niveau", 2023, 'https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/12/pisa-2022-results-volume-ii_222a5ef6/a97db61c-en.pdf')
for _c in ('attal', 'retailleau', 'lisnard', 'zemmour'):
    assert GN in OVR[(_c, 'ecole')]['evidence'], _c
    _ev(_c, 'ecole', OVR[(_c, 'ecole')]['evidence'], add=[GN_S2], drop=['letudiant.fr/educpros/enquetes/lefficacite-des-groupes-de-niveau'])
DD_DT = _src("DEPP, document de travail n° 2026-E01, effets à long terme des classes réduites, première cohorte (p. 9)", 2026, 'https://www.education.gouv.fr/sites/default/files/document/les-effets-long-terme-de-la-r-duction-de-la-taille-de-classe-en-ducation-prioritaire-sur-les-performances-des-l-ves-478865.pdf')
_dd = [c for (c, th), o in OVR.items() if th == 'ecole' and DD in o.get('evidence', '')]
assert sorted(_dd) == ['attal', 'glucksmann', 'le-pen', 'melenchon', 'philippe'], _dd
for _c in _dd: _ev(_c, 'ecole', OVR[(_c, 'ecole')]['evidence'], add=[DD_DT])
INT2 = "Établissements pour élèves exclus (2010) : résultats mitigés, un quart des élèves sans solution en 2012, abandonnés (inspections, 2012)."
_rep('retailleau', 'ecole', INT, INT2)
_ev('retailleau', 'ecole', OVR[('retailleau', 'ecole')]['evidence'], add=[_src("Inspections générales (IGEN-IGAENR), Rapport annuel 2012, « Les établissements de réinsertion scolaire : bilan et perspectives » (p. 41-47)", 2012, 'https://www.vie-publique.fr/files/rapport/pdf/144000010.pdf')])
# économie : SMIC (même lecture que Mélenchon) et régularisation par le travail (Glucksmann) ; Egalim (Attal, Retailleau) ;
# règle d'or (OR : chiffre au lieu de « modéré ») ; incertitude politique (STAB : 12 pays, production et chômage, sans preuve causale)
SMICX = "Experts SMIC (2025) : risque pour l'emploi peu qualifié, SMIC à 62,5 % du médian."
assert _jev('melenchon', 'economie').startswith(SMICX)
SMICX_S = _src("Groupe d'experts sur le SMIC, rapport 2025", 2025, 'https://www.vie-publique.fr/files/rapport/pdf/301429_0.pdf')
REGUL = ("Régularisation liée à un contrat de travail (Espagne, 2005, ≈ 600 000 personnes) : cotisations +4 000 € par personne et par an, salaires des natifs "
         "peu qualifiés du secteur déclaré en hausse, pas d'afflux d'immigration mesuré, retour partiel au travail non déclaré (2025) ; délinquance des régularisés −0,6 point (Italie, 2017).")
REGUL_S = [_src("Elias, Monras, Vázquez-Grenno, titres de travail accordés aux sans-papiers en Espagne en 2005 (Journal of Labor Economics ; présentation de l'université de Barcelone)", 2025, 'https://www.ub.edu/school-economics/news/understanding-the-effects-of-granting-work-permits-to-undocumented-immigrants/'),
           _src("Pinotti, régularisation des immigrés et délinquance en Italie (American Economic Review ; présentation de l'université Bocconi)", 2017, 'https://clean.unibocconi.eu/research/criminal-and-illegal-behavior/clicking-on-heaven-door.-the-effect-of-immigrant-legalization-on-crime')]
o = OVR[('glucksmann', 'economie')]; assert [p['text'] for p in o['proposals']][0] == 'Taxer le 1 % des plus gros héritages pour hausser les salaires nets' and len(o['proposals']) == 4
o['proposals'] = [_p('Porter le SMIC à 1 700 € net')] + o['proposals']
_ev('glucksmann', 'economie', SMICX + " " + _jev('glucksmann', 'economie') + " " + REGUL, add=[GPLAN_S, SMICX_S] + REGUL_S, level='mitigee')
EGALIM = "Lois Egalim : efficacité économique difficile à établir, contrats écrits peu appliqués ; part agricole du prix au détail en hausse en 2021-2023 (Assemblée nationale, 2025)."
EGALIM_S = _src("Assemblée nationale, rapport d'information n° 1014 sur l'évaluation de la loi Egalim 2 (commission des affaires économiques)", 2025, 'https://www.assemblee-nationale.fr/dyn/17/rapports/cion-eco/l17b1014_rapport-information.pdf')
OR2 = ("Règle d'or : déficit réduit de 1,2 à 1,5 point de PIB selon un sous-groupe d'études, effet plus faible avec les meilleures méthodes (30 études, ZEW, 2016) ; "
       "Allemagne, dette de 81 % à 58 % du PIB (2010-2019), 60 Md€ d'emprunts annulés (2023).")
STAB2 = "Incertitude politique : suivie de moins d'investissement (États-Unis), de production et d'emploi (12 pays), sans preuve de causalité (2016) ; règle de stabilité fiscale non évaluée."
for _c in ('le-pen', 'philippe', 'retailleau'): _rep(_c, 'economie', OR, OR2)
for _c in ('attal', 'lisnard'): _rep(_c, 'economie', STAB, STAB2)
_rep('retailleau', 'economie', OR2 + " " + TEPA, OR2 + " " + EGALIM + " " + TEPA)
_ev('retailleau', 'economie', OVR[('retailleau', 'economie')]['evidence'], add=[EGALIM_S])
_ev('attal', 'economie', OVR[('attal', 'economie')]['evidence'] + " " + EGALIM, add=[EGALIM_S])
CODE_S2 = _src("France Stratégie, comité d'évaluation des ordonnances travail, rapport 2021 (p. 17 et 24)", 2021, 'https://www.vie-publique.fr/files/rapport/pdf/283002.pdf')
for _c in ('attal', 'retailleau'):
    _ev(_c, 'economie', OVR[(_c, 'economie')]['evidence'], add=[CODE_S2], drop=['lemondedudroit.fr/publications/248-etudes-et-documents/78930'])
# libertés : voile (« nul » : IZA 2019 ; « négatif » : APSR 2020) ; droit à la sécurité : texte de l'article L. 111-1 attesté par le dossier officiel
_vo, _vn = "après 2004, effet nul ou négatif selon les études (APSR, 2020)", "après 2004, aucun gain de plus (IZA, 2019) ou scolarité des filles en baisse (APSR, 2020)"
for _c in ('lisnard', 'le-pen'): _rep(_c, 'libertes', _vo, _vn)
_ev('retailleau', 'libertes', OVR[('retailleau', 'libertes')]['evidence'], add=[_src("Conseil constitutionnel, dossier documentaire de la décision n° 2020-889 QPC (texte de l'article L. 111-1 du code de la sécurité intérieure)", 2021, 'https://www.conseil-constitutionnel.fr/sites/default/files/as/root/bank_mm/decisions/2020889qpc/2020889qpc_doc.pdf')])
# environnement : SEQE 2 en place en 2028 (Commission européenne) ; Glucksmann, marges des carburants (plan du 22/10, sans coût public direct)
_rep('zemmour', 'environnement', SEQE, "Marché carbone des carburants (en place en 2028) : +10 à 15 c€ par litre à son entrée en vigueur (Institut Montaigne, 2025) ; taxe carbone suédoise : émissions des transports −11 % (2019).")
_ev('zemmour', 'environnement', OVR[('zemmour', 'environnement')]['evidence'], add=[_src("Commission européenne, ETS2 : bâtiments, transport routier et autres secteurs (en place en 2028)", 2026, 'https://climate.ec.europa.eu/eu-action/carbon-markets/ets2-buildings-road-transport-and-additional-sectors_en')])
_upd('glucksmann', 'environnement', [_p('Leasing social : 1 million de voitures électriques à 100 €/mois'),
                                     _p('Encadrer les marges de raffinage et de distribution des carburants pour baisser de 20 centimes le prix à la pompe'),
                                     _p("Loi climat : −90 % d'émissions en 2040", True, True),
                                     _p('Garder le nucléaire, construire de nouvelles unités, plan régional renouvelables', False)], add=[GPLAN_S])

# --- review 32 : simulateur et affichage, relecture du 31/10 (31/10/2026)
# (18) Nucléaire neuf : les deux lectures, Cour des comptes (EPR) et RTE, pour toute proposition de nouveaux réacteurs, chez tous (Le Pen,
# Glucksmann, Attal, Retailleau, Lisnard, Zemmour) ; dans l'ordre des propositions affichées. Mélenchon (sortie du nucléaire) garde la lecture
# RTE des scénarios sans nouveau nucléaire.
_ev('le-pen', 'environnement', RTE + " " + EPR, add=[EPR_S, RTE_S])
assert OVR[('attal', 'environnement')]['evidence'].startswith(EPR + " HCC 2026")
_ev('attal', 'environnement', EPR + " " + RTE + OVR[('attal', 'environnement')]['evidence'][len(EPR):], add=[RTE_S])
_ev('lisnard', 'environnement', EPR + " " + RTE, add=[RTE_S])
GLU_RTE = "RTE : scénarios combinant nouveaux réacteurs et renouvelables les plus compétitifs."
assert OVR[('glucksmann', 'environnement')]['evidence'] == VE + " " + GLU_RTE
_ev('glucksmann', 'environnement', VE + " " + EPR + " " + RTE, add=[EPR_S, RTE_S])
# (17) AME supprimée (Zemmour, santé) : même texte que l'état des études du quiz pour toutes les fiches AME (Le Pen, Retailleau, Lisnard, Zemmour)
_QE = J('quiz_effets.json')
AME = _QE['zemmour.ame']['etudes']
assert all(_QE[k]['etudes'] == AME for k in ('le-pen.ame', 'retailleau.ame', 'lisnard.ame'))
AME_S = [_src(s['l'], s['a'], s['u']) for s in _QE['zemmour.ame']['src'] if any(x in s['u'] for x in ('271649', 'eecrev', 'journal.pone'))]
assert len(AME_S) == 3
_ev('zemmour', 'sante', OVR[('zemmour', 'sante')]['evidence'] + " " + AME, add=AME_S)
# (2, 20) Contribution à l'UE : la lecture UEU s'appuie sur la source primaire (art. 311 du traité sur le fonctionnement de l'UE, décrit par le
# rapport de l'Assemblée nationale n° 3781 : décision « adoptée à l'unanimité par le Conseil […] puis approuvée par les États membres »),
# la même chez les trois candidats qui ont cette lecture ; chez Retailleau, la page d'un agrégateur (PGE) sur le contre-budget du RN est retirée.
UEU_S = _src("Assemblée nationale, rapport n° 3781 sur la décision relative aux ressources propres de l'UE (art. 311 du traité sur le fonctionnement de l'UE)", 2021,
             'https://www.assemblee-nationale.fr/dyn/15/rapports/cion_afetr/l15b3781_rapport-fond.pdf')
for _c in ('le-pen', 'melenchon', 'retailleau'):
    assert UEU in OVR[(_c, 'rayonnement')]['evidence'], _c
    _ev(_c, 'rayonnement', OVR[(_c, 'rayonnement')]['evidence'], add=[UEU_S], drop=(['planetegrandesecoles.com'] if _c == 'retailleau' else []))
# (29) Retailleau : heures supplémentaires = seuil « zéro cotisation » chiffré (1 623 h par an, livret « Le travail gagnant », p. 20) : précise
_p0 = OVR[('retailleau', 'economie')]['proposals']
assert _p0[-1] == _p('Exonérer de cotisations sociales les heures supplémentaires', False)
_p0[-1] = _p("Seuil « zéro cotisation » : heures travaillées au-delà de 1 623 h par an exonérées de toutes les cotisations sociales")
OVR[('retailleau', 'economie')]['add'].append(_src("Livret « Le travail gagnant »", 2026, 'https://www.avecretailleau.fr/api/media/file/Livret_Travail.pdf'))
# (32) Une année (de publication) et un titre par source, chez tous : article de Public Sénat du 6/11/2025 sur le « deal » de Philippe ;
# page de PGE sur le contre-budget du RN (même titre que dans la fiche de Le Pen)
TITRE_S = {'https://www.publicsenat.fr/actualites/economie/entreprises-un-deal-a-250-milliards-deuros-sur-un-quinquennat-que-represente-la-proposition-dedouard-philippe': ('Public Sénat / Rexecode', 2025),
           'https://www.planetegrandesecoles.com/budget-marine-le-pen-2027-mesures-contre-budget-rn': ('Planète Grandes Écoles (contre-budget RN)', 2026)}

# --- review 33 : liens rouverts le 31/10 (31/10/2026) ; registre S027, S193
# PDF du discours de Saint-Raphaël de D. Lisnard : fichier retiré du stockage du parti → compte rendu officiel du meeting là où il dit la même
# chose (20 000 places de prison ; collège unique et carte scolaire) ; logement : le compte rendu ne détaille pas l'article 55 de la loi SRU,
# le ZAN ni les terrains publics, le lien mort est seulement retiré (source officielle à retrouver, S193).
STR_OLD = 'Discours-de-David-Lisnard-a-Saint-Raphael.pdf'
STR_CR = _src('Nouvelle Énergie, compte rendu du meeting de Saint-Raphaël (3/07/2026)', 2026, 'https://www.unenouvelleenergie.fr/a-saint-raphael-david-lisnard-lance-sa-campagne-pour-faire-gagner-la-france-qui-fait/')
for _th, _add in (('securite', [STR_CR]), ('ecole', [STR_CR]), ('logement', [])):
    _o = OVR.setdefault(('lisnard', _th), {})
    _o['drop'] = _o.get('drop', []) + [STR_OLD]
    _o['add'] = [s for s in _o.get('add', []) if STR_OLD not in s['url']] + _add

# --- review 34 : une source qui parle pour le candidat, chaque proposition (31/10/2026) ; registre S193
# Règle d'attribution (la même pour les 8, décisions du porteur du 31/10) : une proposition affichée est attribuée au candidat par au moins une
# source qui parle pour lui : lui-même (discours, entretien, tribune, réseau officiel) ou son site de campagne ; un document officiel de son parti
# ou de son groupe publié après sa désignation, ou repris par lui ; une personne au rôle officiel dans sa campagne ; un média reconnu qui le cite
# (citation, ou propos rapportés précisément et datés), ou deux médias reconnus indépendants qui rapportent la même proposition ; pour une
# proposition de 2022, une analyse d'une institution reconnue (Institut Montaigne) ou d'un média reconnu qui décrit son programme officiel.
# Ne suffisent pas seuls : un agrégateur, un site non officiel, une seule reprise de presse sans citation, une étude. Une source qui parle pour le
# candidat remplace l'agrégateur ou le site non officiel qui portait la même proposition (sinon il reste, signalé) ; un lien mort est retiré.
# Reconfirmation : une proposition est « de 2026 » si une source qui parle pour le candidat la porte en 2026 (site de campagne, document du parti
# publié après la désignation, entretien cité) ; sinon elle est marquée « non reconfirmée », chez tous ; une page sans date ne reconfirme pas,
# sauf sur le site de campagne du candidat, ouvert pour cette élection (pétition contre le SEQE 2 : non). Une proposition dont une partie
# seulement est redite en 2026 est scindée (la partie de 2026, la partie non reconfirmée), et la règle d'ordre (2026 d'abord, précises, plus
# récentes, 5 au plus) s'applique ; une proposition sans source qui parle pour le candidat sort de l'affichage (registre S106), et une lecture
# d'étude ne sort que si plus aucune proposition de ce type n'est affichée dans le thème.
# Contrôle (merge) : chaque proposition affichée a, dans data/life-attribution.json, au moins une source qui parle pour le candidat, affichée
# dans le thème, qui n'est ni un agrégateur ni un site non officiel (même test de nom d'hôte que l'app) ni une étude (ATTR_OK ci-dessous).
def _cur(cid, th):
    """Propositions d'un thème telles qu'elles seraient affichées : liste réécrite plus haut (OVR), sinon dernier fichier data/life-*.json."""
    o = OVR.get((cid, th))
    if o and 'proposals' in o: return [dict(p) for p in o['proposals']]
    ps = None
    for f in ('life-a.json', 'life-b.json', 'life-eco.json'):
        for t in J(f)['life'].get(cid, []):
            if t['theme'] == th: ps = [norm_prop(p) for p in t.get('proposals', []) if (p['text'] if isinstance(p, dict) else p).strip()]
    assert ps is not None, (cid, th); return ps
def _put(cid, th, ps): OVR.setdefault((cid, th), {})['proposals'] = ps
def _rem(cid, th, *texts):
    """Retire de l'affichage (registre S106, avec la raison)."""
    ps = _cur(cid, th); T = [p['text'] for p in ps]
    for t in texts: assert t in T, (cid, th, t)
    _put(cid, th, [p for p in ps if p['text'] not in texts])
def _txt(cid, th, old, new=None, v=None, o=None):
    """Texte corrigé à la source, test « précis » (v) ou marque « non reconfirmée » (o), à sa place."""
    ps = _cur(cid, th); T = [p['text'] for p in ps]; assert old in T, (cid, th, old); i = T.index(old)
    ps[i] = dict(ps[i], text=new or old, **({} if v is None else {'verifiable': v}), **({} if o is None else {'old': o}))
    _put(cid, th, ps)
def _so(cid, th, add=(), drop=()):
    """Sources : retire (sous-chaîne de l'adresse, dans les données comme dans les ajouts) puis ajoute."""
    o = OVR.setdefault((cid, th), {})
    if drop:
        o['drop'] = o.get('drop', []) + list(drop)
        o['add'] = [s for s in o.get('add', []) if not any(d in s['url'] for d in drop)]
    if add: o['add'] = o.get('add', []) + [s for s in add if s['url'] not in {x['url'] for x in o.get('add', [])}]
AGG = ['votons-2027.fr', 'repere2027.fr', 'monvote2027.fr', 'france-vote.fr', 'planetegrandesecoles.com', 'lisnard.cards', 'wikiglucksmann.fr']

# Le Pen : sources officielles du RN (22 mesures pour 2022, livret « L'école » 2022) à la place de Votons 2027 ; peines planchers redites en 2026
# (« des peines minimales », pétition du RN d'octobre) séparées des remises de peine (2022 seulement, non reconfirmées) : la présomption de
# légitime défense (2022), 6e et à égalité avec les remises de peine, sort de l'affichage (S106) ; montants alignés sur le contre-budget
# (5,6 Md€ en 2027) et sur la candidate (contribution « nette », 14/10) ; FED, EDIP, SAFE : aucune source qui parle pour la candidate (S106).
RN22 = _src('Rassemblement national, « 22 mesures pour 2022 » (programme présidentiel de 2022)', 2022, 'https://rassemblementnational.fr/22-mesures')
RN_ECOLE = _src("Rassemblement national, livret « L'école » (programme présidentiel de 2022)", 2022, 'https://rassemblementnational.fr/documents/projet/projet-l-ecole.pdf')
LCP2410 = _s("LCP, contribution de la France à l'UE (24/10)", 'https://lcp.fr/actualites/taxer-les-multinationales-pour-financer-l-europe-le-debat-est-relance-444232')
assert [p['text'] for p in _cur('le-pen', 'securite')][3:] == ['Rétablir les peines planchers, supprimer les remises de peine', "Présomption de légitime défense pour les forces de l'ordre"]
_put('le-pen', 'securite', _cur('le-pen', 'securite')[:3] + [_p('Peines minimales (peines planchers) et comparution immédiate des interpellés'),
     _p('Supprimer les remises de peine', True, True)])
_so('le-pen', 'securite', add=[RN22], drop=AGG)
for _th in ('sante', 'environnement', 'libertes'): _so('le-pen', _th, add=[RN22], drop=AGG)
_so('le-pen', 'ecole', add=[RN22, RN_ECOLE], drop=AGG)
_so('le-pen', 'environnement', drop=['Les-Echos-11-02-2026-Page-7.pdf'], add=[_s('Les Echos, RN et PPE (11/02), copie du Syndicat des énergies renouvelables', 'https://www.syndicat-energies-renouvelables.fr/wp-content/uploads/2026/02/Les-Echos-11-02-2026-Page-7.pdf')])
_txt('le-pen', 'economie', 'Supprimer les subventions aux renouvelables : 5 Md€ dès la 1re année', 'Supprimer les tarifs préférentiels des renouvelables intermittentes : 5,6 Md€ en 2027')
_so('le-pen', 'economie', drop=AGG, add=[_s('Acteurs publics, contre-budget du RN (6/10)', 'https://acteurspublics.fr/articles/la-reforme-de-letat-et-des-collectivites-au-coeur-des-economies-programmees-par-le-rn/')])
_txt('le-pen', 'rayonnement', "Plafonner la contribution française au budget de l'UE à 5 Md€", "Plafonner la contribution nette de la France au budget de l'UE à 5 Md€ par an")
_rem('le-pen', 'rayonnement', 'Refuser les instruments européens de défense : FED, EDIP, SAFE')
_so('le-pen', 'rayonnement', drop=AGG + ['institut-sciences-strategiques.org'], add=[
    _s('Euronews, conférence de presse à Bruxelles (14/10)', 'https://www.euronews.com/2026/10/14/le-pen-lands-in-brussels-lashing-out-at-the-european-commission'), LCP2410,
    _s('Reuters via The Star, entretien sur BFMTV (22/05)', 'https://www.thestar.com.my/news/world/2026/05/23/le-pen-says-france-should-quit-nato-command-structure')])
del TITRE_S['https://www.planetegrandesecoles.com/budget-marine-le-pen-2027-mesures-contre-budget-rn']  # plus citée dans la Vie quotidienne

# Mélenchon (désigné le 3/05/2026) : documents de son site de campagne publiés depuis (synthèse des contributions du 17/07, plan « BTP et
# logement » du 24/09) → police de proximité, « sécurité sociale intégrale », 200 000 logements publics et meublés touristiques à 60 jours sont de
# 2026 ; le démantèlement des BAC (programme de 2022) n'y est pas redit : séparé, non reconfirmé. Propositions de 2022 : fiches de l'Institut
# Montaigne (programme officiel, « rendre public un bilan annuel » compris), profession de foi, amendement cosigné (2021). Livre-programme de 2025
# (lien mort, renvoie à l'accueil) retiré ; scolarité obligatoire à 18 ans : rien dans le programme de 2022 consultable (S106). Police de
# proximité seule : intention, même test que chez Glucksmann (« Police de proximité modernisée ») ; démantèlement des BAC : précis.
MONT_JLM = _src('Institut Montaigne, propositions du candidat (présidentielle 2022)', 2022, 'https://www.institutmontaigne.org/presidentielle-2022/jean-luc-melenchon')
SYN = 'https://melenchon2027.fr/programme/synthese-des-contributions/'
_put('melenchon', 'securite', [_p('Rétablir la police de proximité', False), _p("Dissoudre la BRAV-M, interdire LBD et grenades, remplacer l'IGPN"), _p('Démanteler les BAC', True, True),
                               _p('Mécanisme contraignant de régulation carcérale contre la surpopulation', True, True)])
_so('melenchon', 'securite', drop=AGG, add=[_s('Mélenchon 2027, synthèse des contributions, chapitre 4 (17/07)', SYN + 'chapitre-4-etendre-le-domaine-de-la-liberte/'),
    _s('Mélenchon 2027, synthèse des contributions, chapitre 7 (17/07)', SYN + 'chapitre-7-la-force-de-lentraide-2/'), MONT_JLM,
    _src('Assemblée nationale, amendement n° 23 du groupe LFI cosigné par J.-L. Mélenchon (16/03/2021)', 2021, 'https://www.assemblee-nationale.fr/dyn/15/amendements/3973/AN/23.pdf')])
_txt('melenchon', 'sante', '« 100 % Sécu » : soins prescrits remboursés intégralement', o=False)
_so('melenchon', 'sante', drop=AGG, add=[_s('Mélenchon 2027, synthèse des contributions (17/07)', 'https://melenchon2027.fr/synthese-des-contributions/'),
    _src('Profession de foi du candidat, version FALC (présidentielle 2022)', 2022, 'https://melenchon.fr/wp-content/uploads/2022/04/PF_Jean-Luc-Melenchon_FALC.pdf')])
_rem('melenchon', 'ecole', "Scolarité obligatoire jusqu'à 18 ans")
_so('melenchon', 'ecole', drop=AGG)
_so('melenchon', 'environnement', drop=AGG, add=[MONT_JLM])
for _t in ('200 000 logements publics par an pendant cinq ans', 'Plafonner les meublés touristiques à 60 jours par an'): _txt('melenchon', 'logement', _t, o=False)
_so('melenchon', 'logement', add=[_s('Mélenchon 2027, plan « BTP et logement » (24/09)', 'https://melenchon2027.fr/programme/plans-investissement/btp-logement/')])
_so('melenchon', 'libertes', drop=AGG + ['melenchon2027.fr/programme2025/livre/'], add=[_s('Mélenchon 2027, synthèse des contributions, chapitre 1 (17/07)', SYN + 'chapitre-1-le-pouvoir-au-peuple/'), MONT_JLM])

# Philippe : site de campagne à la place de Repère 2027 et de Votons 2027 ; Echos Plus (site non identifié comme média) retiré ; pays sûrs : même
# texte que ses deux sources (liste votée chaque année par le Parlement, site du candidat ; liste commune de l'UE, Euronews, 9/10).
_so('philippe', 'sante', drop=AGG, add=[_s('Site Édouard Philippe, « Pour une France plus prospère »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-prospere')])
_so('philippe', 'environnement', add=[_s('Site de campagne, France plus sûre', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-sure')])
_so('philippe', 'logement', drop=['echosplus.com'], add=[_s('Site Édouard Philippe, « Pour une France plus attentive à ses enfants »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-attentive-a-ses-enfants')])
_so('philippe', 'libertes', drop=AGG)
_txt('philippe', 'rayonnement', "Liste européenne commune de pays sûrs, sans droit d'asile", "Liste de pays sûrs votée chaque année par le Parlement et liste commune de l'UE, sans droit d'asile pour leurs ressortissants", v=True)
_so('philippe', 'rayonnement', add=[_s('Site de campagne, France plus sûre', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-sure')])

# Glucksmann (candidature déclarée le 23/08/2026) : « Acte I » de Place publique (juin 2025, co-dirigé et présenté par lui) à la place de
# WikiGlucksmann (non officiel) ; ses propositions restent non reconfirmées, sauf l'encadrement des loyers, redit dans son plan du 22/10 ;
# nouveau nucléaire redit en 2026 (LCP, 25/08), plans régionaux pour les renouvelables seulement dans l'Acte I : séparés, non reconfirmés.
# Aides au privé : « 10 Md€/an » n'est attribué au candidat que par WikiGlucksmann → retiré, la proposition devient une intention.
ACTE1 = _src('Place publique, « Acte I : notre vision pour la France » (juin 2025)', 2025, 'https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf')
for _th in ('securite', 'sante', 'environnement', 'logement', 'libertes', 'economie'): _so('glucksmann', _th, drop=AGG, add=[ACTE1])
_txt('glucksmann', 'ecole', 'Conditionner les aides au privé (10 Md€/an) à la mixité sociale', 'Conditionner les aides au privé sous contrat à la mixité sociale', v=False)
_so('glucksmann', 'ecole', drop=AGG, add=[_s('LCP, premières lignes du programme', 'https://lcp.fr/actualites/presidentielle-raphael-glucksmann-devoile-les-premieres-lignes-de-son-possible-programme'),
    _s('France Inter, Franc-jeu (30/08)', 'https://www.radiofrance.fr/franceinter/podcasts/franc-jeu/franc-jeu-du-dimanche-30-aout-2026-6196033'),
    _s('LCP, dernier débat de la primaire (5/10)', 'https://lcp.fr/actualites/glucksmann-face-a-royal-divisions-sur-lfi-lycees-ce-qu-il-faut-retenir-du-dernier-debat'), GPLAN_S])
_put('glucksmann', 'environnement', [p if not p['text'].startswith('Garder le nucléaire') else _p('Garder le nucléaire, construire de nouvelles unités', False)
                                     for p in _cur('glucksmann', 'environnement')] + [_p('Plans régionaux d\'investissement dans les renouvelables', False, True)])
assert [p['text'] for p in OVR[('glucksmann', 'environnement')]['proposals']].count('Garder le nucléaire, construire de nouvelles unités') == 1
_so('glucksmann', 'environnement', add=[_s('LCP, « les 100 jours de la révolution écologique » (25/08)', 'https://lcp.fr/actualites/presidentielle-2027-s-il-gagne-raphael-glucksmann-engagera-les-100-jours-de-la')])
_txt('glucksmann', 'logement', 'Encadrement des loyers en zones tendues', o=False)
_so('glucksmann', 'logement', add=[GPLAN_S])
_so('glucksmann', 'rayonnement', drop=AGG)

# Attal : pages de son site à la place de MonVote2027 et de Votons 2027 ; suppression du JAP redite en 2026 (JDD, 2/08) ; prix de l'électricité
# stables cinq ans (et non dix) ; délai de deux mois pour répondre aux porteurs de projets. Logement intermédiaire dans les quotas SRU et ZAN
# simplifié : une seule reprise sans citation (Batirama ; Investies est un blog, pas un média reconnu), rien sur son site → S106.
_txt('attal', 'securite', "Supprimer le juge d'application des peines", o=False)
_so('attal', 'securite', drop=AGG, add=[_s('attalpresident.fr – réforme institutionnelle', 'https://attalpresident.fr/actualites/dans-le-jdd-gabriel-attal-veut-proposer-la-plus-grande-reforme-institutionnelle-depuis-1958')])
_so('attal', 'sante', drop=AGG, add=[_s('attalpresident.fr, mesure « assistant médical IA »', 'https://attalpresident.fr/programme/mesures/assistant-medical-ia'),
    _s('attalpresident.fr, mesures pour la jeunesse (10/10)', 'https://attalpresident.fr/actualites/gabriel-attal-presente-ses-mesures-pour-la-jeunesse-et-l-avenir-de-la-france')])
_txt('attal', 'environnement', "Garantir la stabilité des prix de l'électricité pendant dix ans", "Garantir la stabilité des prix de l'électricité pendant cinq ans")
_so('attal', 'environnement', drop=AGG, add=[_s('attalpresident.fr, mesure « plan Messmer II »', 'https://attalpresident.fr/programme/mesures/plan-messmer-2'),
    _s('attalpresident.fr, chantier « Dette écologique »', 'https://attalpresident.fr/programme/dette-ecologique'),
    _s("attalpresident.fr, prix de l'électricité stables pendant cinq ans (17/06)", 'https://attalpresident.fr/programme/mesures/stabilite-prix-electricite')])
_rem('attal', 'logement', 'Intégrer le logement intermédiaire dans les quotas SRU des communes', 'Simplifier le ZAN pour faciliter la construction')
_so('attal', 'logement', drop=['investies.fr'], add=[_s('attalpresident.fr, logement et bâtiment (29/09)', 'https://attalpresident.fr/actualites/gabriel-attal-veut-liberer-l-acces-au-logement-et-relancer-le-secteur-du-batiment')])
_txt('attal', 'libertes', 'Délai de réponse administrative de deux mois maximum inscrit dans la Constitution', 'Délai maximal de deux mois pour répondre aux porteurs de projets, inscrit dans la Constitution')

# Retailleau : pages de son site à la place de Repère 2027, Votons 2027 et MonVote2027 ; huit EPR2 conditionnés à l'avancement des six premiers ;
# déchéance de nationalité pour les pilleurs (franceinfo) : « violences contre les forces de l'ordre » ne se lit que sur un site non reconnu ;
# suppression du JAP (Public Sénat seul, sans citation) et contribution à l'UE, dépenses de défense comprises (Business AM seul, payant, sans
# citation) : S106 ; la lecture « contribution à l'UE » (UEU) sort de son thème « rayonnement », où plus aucune proposition de ce type n'est affichée.
FICHES_R = 'https://www.avecretailleau.fr/api/media/file/20261011_Fiches_presse_comptes_publics_mise_en_page%20(1).pdf'
TITRE_S[FICHES_R] = ("avecretailleau.fr, fiches presse « Rétablir l'ordre dans les comptes publics » (12/10)", 2026)  # un titre pour les deux thèmes qui la citent
_txt('retailleau', 'securite', "Déchéance de nationalité des binationaux auteurs de pillages ou de violences contre les forces de l'ordre", 'Déchéance de nationalité des binationaux auteurs de pillages')
_rem('retailleau', 'securite', "Suppression du juge d'application des peines")
_so('retailleau', 'securite', drop=['presidentielle-jirai-jusquau-bout'])
_so('retailleau', 'sante', drop=AGG, add=[_s("avecretailleau.fr, fiches presse « Rétablir l'ordre dans les comptes publics » (12/10)", FICHES_R)])
_txt('retailleau', 'environnement', 'Commander huit EPR2 supplémentaires dans les deux premières années', 'Commander huit EPR2 supplémentaires dans les deux premières années, si les six premiers avancent comme prévu')
_so('retailleau', 'environnement', drop=AGG, add=[_s('avecretailleau.fr, construire les EPR2 dans les coûts et délais prévus', 'https://www.avecretailleau.fr/projet/mesure/construire-les-epr2-dans-les-couts-et-delais-prevus'),
    _s('avecretailleau.fr, fin des subventions aux éoliennes et au solaire', 'https://www.avecretailleau.fr/projet/mesure/cesser-de-subventionner-ce-qui-fait-monter-la-facture-les'),
    _s('avecretailleau.fr, hydroélectricité', 'https://www.avecretailleau.fr/projet/mesure/produire-et-stocker-plus-d-electricite-grace-aux-barrages')])
_so('retailleau', 'logement', drop=AGG, add=[_s('avecretailleau.fr, thème « Logement »', 'https://www.avecretailleau.fr/projet/theme/logement'),
    _s("avecretailleau.fr, intérêts d'emprunt déductibles", 'https://www.avecretailleau.fr/projet/mesure/reduire-le-cout-du-credit-des-familles'),
    _s('avecretailleau.fr, abroger le ZAN', 'https://www.avecretailleau.fr/projet/mesure/abroger-le-zan')])
_rem('retailleau', 'rayonnement', "Réduire la contribution française au budget de l'UE par la négociation", 'Intégrer les dépenses de défense dans le calcul de cette contribution')
_rep('retailleau', 'rayonnement', " " + UEU, "")
_so('retailleau', 'rayonnement', drop=AGG + ['businessam.be', UEU_S['url']])

# Lisnard : programme et pages de Nouvelle Énergie à la place de lisnard.cards (non officiel), Votons 2027, Repère 2027 et France-Vote ; article 55
# de la loi SRU (programme), ZAN « tel qu'il est conçu » (tribune du 9/05/2025, redit à Cannes le 29/08/2026), foncier public (seul entretien du
# 5/12/2025) non reconfirmé ; exonération de CFE pour les médecins libéraux ; article 55 de la Constitution visant la CEDH, dérogation « à la
# danoise » pour le droit de l'UE (Bayeux, 17/06). TVA unique à 25 % : seul lisnard.cards, son programme dit la question « pas tranchée » → S106,
# avec la lecture « TVA sociale » (CEPII), seule proposition de ce type du thème. Rayonnement : lectures du même type que chez les autres candidats
# (primauté de la loi nationale, comme Zemmour ; accord de 1968, comme Philippe).
_so('lisnard', 'securite', drop=AGG)
_txt('lisnard', 'sante', "Liberté d'installation, exonération de CFE pour libéraux en zone sous-dense", "Liberté d'installation, exonération de CFE pour les médecins libéraux en zone sous-dense")
_so('lisnard', 'sante', drop=AGG, add=[_s('Nouvelle Énergie, programme « Santé »', 'https://www.unenouvelleenergie.fr/notre-programme/sante/'),
    _s('Nouvelle Énergie, Livret Santé (6/05)', 'https://nouvelle-energie-media-prod.s3.fr-par.scw.cloud/media/legacy/2026/05/Livret-Sante-Nouvelle-Energie.pdf')])
_so('lisnard', 'ecole', drop=AGG)
_so('lisnard', 'libertes', drop=AGG)
_so('lisnard', 'environnement', drop=AGG, add=[_s("Nouvelle Énergie, grand entretien de l'écologie (27/10)", 'https://www.unenouvelleenergie.fr/lenergie-doit-reconcilier-lindustrie-et-lecologie/'),
    _s('Nouvelle Énergie, « Quel candidat veut construire de nouveaux réacteurs nucléaires ? »', 'https://www.unenouvelleenergie.fr/questions/quel-candidat-veut-construire-de-nouveaux-reacteurs-nucleaires/'),
    _s('Nouvelle Énergie, « Que pense David Lisnard du réchauffement climatique ? »', 'https://www.unenouvelleenergie.fr/questions/que-pense-david-lisnard-du-rechauffement-climatique/')])
_txt('lisnard', 'logement', "Supprimer l'objectif zéro artificialisation nette (ZAN)", "Supprimer l'objectif zéro artificialisation nette (ZAN) tel qu'il est conçu")
_txt('lisnard', 'logement', 'Mettre en vente ou à disposition des terrains publics', o=True)
_so('lisnard', 'logement', drop=AGG, add=[_s('Nouvelle Énergie, programme « Réussir une nouvelle ambition française »', 'https://www.unenouvelleenergie.fr/notre-programme/reussir-une-nouvelle-ambition-francaise/'),
    _src('Nouvelle Énergie, tribune « Quand le bâtiment ne va plus, rien ne va plus » (9/05/2025)', 2025, 'https://www.unenouvelleenergie.fr/quand-le-batiment-ne-va-plus-rien-ne-va-plus/'),
    _s('Nouvelle Énergie, « Quel candidat veut réindustrialiser la France ? » (rentrée de Cannes, 29/08)', 'https://www.unenouvelleenergie.fr/questions/quel-candidat-veut-reindustrialiser-la-france/'),
    _src('Nouvelle Énergie, entretien au Figaro sur le logement (5/12/2025)', 2025, 'https://www.unenouvelleenergie.fr/david-lisnard-face-a-la-crise-du-logement-il-est-temps-de-briser-cette-spirale-infernale/')])
_rem('lisnard', 'economie', 'TVA unique à 25 % en douze ans pour baisser les charges')
CEPII = "CEPII (2007) : TVA sociale, emplois modestes si ciblée sur les bas salaires, pouvoir d'achat réduit."
_rep('lisnard', 'economie', " " + CEPII, "")
_so('lisnard', 'economie', drop=['cepii.fr/PDF_PUB/lettre/2007/let269.pdf'], add=[_s('Nouvelle Énergie, « David Lisnard veut-il baisser les impôts ? »', 'https://www.unenouvelleenergie.fr/questions/david-lisnard-veut-il-baisser-les-impots/')])
_txt('lisnard', 'rayonnement', "Réviser l'article 55 de la Constitution sur la primauté du droit européen",
     "Réviser l'article 55 de la Constitution pour faire primer la loi sur la CEDH ; pour le droit de l'UE, une dérogation à la danoise sur l'asile et l'immigration")
PRIM0 = "Aucune évaluation publique de l'effet d'une sortie de la CEDH ou d'une primauté constitutionnelle de la loi nationale sur le droit européen."
PRIM = "Aucune évaluation publique de l'effet d'une primauté de la loi nationale sur la CEDH ou sur le droit européen."
ALG = "Pas d'évaluation publique de l'effet d'une dénonciation de l'accord de 1968 sur les relations ou l'influence de la France."
assert _jev('philippe', 'rayonnement') == ALG and _jev('zemmour', 'libertes') == PRIM0 and OVR[('lisnard', 'rayonnement')]['evidence'] == FIN
_ev('lisnard', 'rayonnement', PRIM + " " + FIN + " " + ALG, drop=AGG, add=[_s('Discours de Bayeux', 'https://nouvelle-energie-media-prod.s3.fr-par.scw.cloud/media/legacy/2026/06/Discours-de-David-Lisnard-a-Bayeux-17062026.pdf'),
    _s('Nouvelle Énergie, programme « Immigration »', 'https://www.unenouvelleenergie.fr/notre-programme/immigration/')])

# Zemmour : entretien du 25/10 (Les Incorrectibles, vidéo du candidat ; cité sans guillemets, transcription automatique non réécoutée) pour les
# méthodes traditionnelles ; Entrevue rapporte LCI, pas CNews. Programme des européennes de 2024 (document de parti antérieur à la désignation,
# règle S133) : chaque proposition cherchée dans le programme de 2022 (Institut Montaigne, entretiens de 2022) ou une source de 2026 qui parle pour
# lui. Article 55 : programme de 2022 (« toute nouvelle loi nationale »), non reconfirmé ; éolien : version de 2026 dans le plan de 140 Md€ repris
# le 17/09 (« fin de l'engagement de soutien public aux énergies renouvelables intermittentes ») ; voitures thermiques : entretien de 2022
# (« renégocier ce calendrier européen »), non reconfirmé ; directive sur la performance énergétique des bâtiments, sortie de la CEDH, loi Avia :
# rien en 2022 ni en 2026 → S106, comme la vente de HLM, le Livret A à 20 % (2022 : « livret innovation ») et les 40 000 soldats (agrégateurs
# seuls). Pétition contre le SEQE 2 sans date : non reconfirmée en 2026. Aucune proposition ne revient à leur place.
MONT_ZEM = _src('Institut Montaigne, propositions du candidat (présidentielle 2022)', 2022, 'https://www.institutmontaigne.org/presidentielle-2022/eric-zemmour')
INCORR = _s('Les Incorrectibles, émission du 25/10', 'https://lesincorrectibles.substack.com/p/eric-zemmour-la-france-face-au-chaos-1')
_so('zemmour', 'securite', drop=AGG + ['une-horde-de-barbares-maghrebins'], add=[_s('Entrevue, déclarations sur LCI (18/10)', 'https://entrevue.fr/medias/une-horde-de-barbares-maghrebins-et-africains-eric-zemmour-provoque/'),
    _s('Europe 1, « La France en face » (19/05)', 'https://www.europe1.fr/politique/en-direct-immigration-pouvoir-dachat-narcotrafic-ce-quil-faut-retenir-de-linterview-deric-zemmour-dans-la-france-en-face-936419')])
_so('zemmour', 'sante', drop=AGG, add=[_src('Le Quotidien du médecin, réponses écrites du candidat (1/04/2022)', 2022, 'https://www.lequotidiendumedecin.fr/actus-medicales/politique-de-sante/eric-zemmour-reconquete-un-conventionnement-preferentiel-pourra-etre-mis-en-place'), MONT_ZEM])
_so('zemmour', 'ecole', drop=AGG, add=[INCORR])
_ze = {p['text']: p for p in _cur('zemmour', 'environnement')}
_put('zemmour', 'environnement', [_ze["Six EPR d'ici 2035 et quatorze d'ici 2045"], _p('Mettre fin au soutien public aux énergies renouvelables intermittentes'),
     dict(_ze['Abroger le marché carbone européen sur les carburants et le chauffage (SEQE 2) avant 2028'], old=True),
     _p('Renégocier le calendrier européen de fin des voitures thermiques neuves en 2035', False, True)])
assert set(_ze) == {"Six EPR d'ici 2035 et quatorze d'ici 2045", 'Abroger le marché carbone européen sur les carburants et le chauffage (SEQE 2) avant 2028',
                    "Fin des financements français et européens à l'éolien", "Abroger l'interdiction des voitures thermiques neuves en 2035"}
_SQ = "Marché carbone des carburants (en place en 2028) : +10 à 15 c€ par litre à son entrée en vigueur (Institut Montaigne, 2025) ; taxe carbone suédoise : émissions des transports −11 % (2019)."
assert OVR[('zemmour', 'environnement')]['evidence'] == EPR + " " + _SQ + " " + RTE
_ev('zemmour', 'environnement', EPR + " " + RTE + " " + _SQ, drop=AGG, add=[_s('budget2027.fr, plan de 140 Md€ repris par le candidat (17/09)', 'https://www.budget2027.fr/'),
    _src("Le Journal de l'Automobile, entretien avec le candidat (24/03/2022)", 2022, 'https://journalauto.com/services/presidentielle-2022-eric-zemmour-r-jai-lintime-conviction-que-la-voiture-va-evoluer-avec-son-temps-et-perdurer/')])
OVR[('zemmour', 'logement')] = {'proposals': [], 'indicator': None, 'evidence': 'Pas de proposition publiée sur ce thème.', 'drop': ['http'], 'add': []}
_put('zemmour', 'libertes', [_p('Article 55 révisé : toute nouvelle loi nationale au-dessus du droit européen existant', True, True)])
_ev('zemmour', 'libertes', PRIM, drop=AGG, add=[MONT_ZEM])
_rem('zemmour', 'economie', "Orienter 20 % du Livret A vers l'investissement stratégique")
_so('zemmour', 'economie', drop=AGG, add=[MONT_ZEM])
_rem('zemmour', 'rayonnement', '40 000 soldats professionnels supplémentaires')
_so('zemmour', 'rayonnement', drop=AGG, add=[MONT_ZEM])

# Contrôle d'attribution (merge) : data/life-attribution.json donne, pour chaque proposition affichée (texte exact), les adresses des sources
# qui parlent pour le candidat ; chacune doit être affichée dans le thème et passer ATTR_OK. Une source parle pour le candidat si son adresse est
# (1) sur un domaine du candidat, de sa campagne ou de son parti, pour ce candidat seulement (le site d'un camp n'est jamais une source sur un
# autre) ; (2) sur un média reconnu ; (3) une fiche de programme d'une institution reconnue (Institut Montaigne, présidentielle 2022), un
# amendement signé ou la copie d'un article de presse nommé. Les études s'en distinguent de deux façons : leurs éditeurs (Cour des comptes, Insee,
# IPP, DEPP, Sénat et Assemblée pour leurs rapports, universités, revues, organismes internationaux) ne figurent dans aucune de ces listes, et
# aucune adresse citée pour une lecture (constantes ci-dessous) ni dans le quiz (quiz_effets.json, où ne figurent que des études et des
# statistiques) ne peut servir d'attribution. Agrégateurs et sites non officiels : refusés par le même test de nom d'hôte que l'app (NOFF).
OFFICIEL = {'le-pen': ('rassemblementnational.fr', 'deputes-rn.fr'), 'melenchon': ('melenchon2027.fr', 'melenchon.fr'), 'philippe': ('edouardphilippe.fr',),
            'glucksmann': ('place-publique.eu',), 'attal': ('attalpresident.fr',), 'retailleau': ('avecretailleau.fr', 'republicains.fr'),
            'lisnard': ('unenouvelleenergie.fr', 'nouvelle-energie-media-prod.s3.fr-par.scw.cloud'),
            'zemmour': ('parti-reconquete.fr', 'stop-hausse-carburant.fr', 'budget2027.fr')}
OFFICIEL_U = {'glucksmann': ('https://bsky.app/profile/placepublique.bsky.social/',)}  # compte officiel du parti
MEDIAS = ('franceinfo.fr', 'capital.fr', 'europe1.fr', 'lcp.fr', 'publicsenat.fr', 'cnews.fr', 'sudradio.fr', 'lalibre.be', 'actu.orange.fr', 'euronews.com',
          'thestar.com.my', 'acteurspublics.fr', 'lequotidiendumedecin.fr', 'journaldunet.com', 'lagazettefrance.fr', 'radiofrance.fr', 'touteleurope.eu',
          'lemoniteurdespharmacies.fr', 'batirama.com', 'journaldelagence.com', 'sfen.org', 'entrevue.fr', 'lesincorrectibles.substack.com', 'journalauto.com')
PROGRAMME_U = ('https://www.institutmontaigne.org/presidentielle-2022/', 'https://www.assemblee-nationale.fr/dyn/15/amendements/',
               'https://www.syndicat-energies-renouvelables.fr/wp-content/uploads/2026/02/Les-Echos-')
ETUDES = {s['url'] for s in [IPP_PP, HEN_S, EPR_S, MAINT_S, HCC_S, RTE_S, IA_S, MIN_S, CEF_S, CEF_S2, DECH_S, FICH_S, RECO_S, PARC_S, INT_S, STAB_S, CU_S,
                             SCH_S, RIP_S, SECU_S, CSM_S, GN_S, GN_S2, DD_DT, MED_S, ORIENT_S, SMICX_S, EGALIM_S, DSA_S, UEU_S, LEAS_S, CODE_S2, *DD_S, *SAL_S,
                             *EXAM_S, *CASSE_S, *CHEQ_S, *OR_S, *CODE_S, *DOUANE_S, *VOTE16_S, *VOILE_S, *SEQE_S, *VE_S, *REGUL_S, *AME_S]}
ETUDES |= {s['u'] for v in _QE.values() if isinstance(v, dict) for s in v.get('src', []) if isinstance(s, dict)}
def ATTR_OK(cid, u):
    return (host_in(u, OFFICIEL[cid]) or u.startswith(OFFICIEL_U.get(cid, ('\0',))) or host_in(u, MEDIAS) or u.startswith(PROGRAMME_U)) and u not in ETUDES

# --- review 37 : veille du 31/10 au 1/11 et propositions non affichées (01/11/2026) ; registre S195, S113
# Décisions du porteur du 1/11 ; chaque citation relue à la source le 1/11. Règle d'ordre commune (2026 d'abord, précises avant intentions, puis
# les plus récentes ; à égalité ou à date inconnue, ordre affiché gardé ; 5 au plus) : aucune proposition ne sort (S106).
# (1) Régularisation (S113) : chez Glucksmann, la version précise (≈ 300 000 ; titre de séjour après six mois de travail sur les deux dernières
# années), rapportée par deux médias reconnus indépendants (RTL, 28/10 ; franceinfo, 29/10 ; règle S136), remplace l'intention du 30/08 ; la
# réserve de RTL (« avant même une éventuelle intégration au programme ») est dans le titre de la source. La proposition de loi n° 3253 (déposée le
# 6/10, avant la désignation du candidat) ne vaut pas source seule (règle S133).
# (2) Même recherche chez les 8 (sources de 2026 qui parlent pour le candidat), même thème (économie) et même lecture (REGUL) : Le Pen, « zéro
# régularisation » (L. Jacobelli, l'un des porte-parole de campagne nommés les 3/07 et 14/09, cité par RTL le 28/10 ; précise : cible chiffrée) ;
# Mélenchon, « régulariser les travailleurs, étudiants, parents d'enfants scolarisés », déjà dans son programme selon la synthèse des contributions
# de son site (17/07/2026 ; intention : ni nombre ni critère) ; Philippe, « verrou Schengen » (site de campagne : aucun État européen ne doit
# pouvoir engager seul une régularisation massive au-delà d'un seuil défini collectivement ; intention : seuil non défini). Attal, Retailleau,
# Lisnard, Zemmour : aucune position de 2026 trouvée (sites de campagne et presse, 1/11 ; registre).
# (3) Le Pen : loi Hulot (Europe 1, 25/10, discours d'Orléans, sans l'adjectif de la candidate ; précise : loi nommée), sans étude vérifiée
# (S141) ; soins dentaires à 100 % de la base (contre-budget du groupe RN, 13/10 ; fiche « dentaire » déjà comptée), avec la même lecture que le
# « 100 % Sécu » de Mélenchon (une lecture par type : remboursement intégral par la Sécurité sociale ; rapport du Sénat sur l'enquête de la Cour
# des comptes, mêmes faits que le quiz de la fiche).
# (4) Zemmour : programme présidentiel de 2022 (PDF du candidat, 25/03/2022, 73 p.) = source de ses propositions de 2022 (non reconfirmées) :
# loi SRU abrogée (p. 44 ; logement, précise, lecture SRU comme Le Pen et Lisnard), loi Pleven abrogée et retour à la loi de 1881 (p. 62 ;
# libertés, précise), Livret Innovation (p. 37 ; économie, précise : avantage fiscal et usage publiés, « sans aucune fiscalité » dans « les
# start-ups et entreprises innovantes »), et source ajoutée aux propositions de 2022 déjà affichées qu'il contient (article 55 p. 6, impôts de
# production p. 25, prime « zéro charges » p. 28, 1 000 médecins salariés p. 53, AME p. 8, classes de niveau p. 22, propagande à l'école p. 21,
# défense à 70 Md€ p. 17, OTAN p. 16). Pleven et Livret Innovation : pas d'étude vérifiée (S141).
# (5) Retailleau : mesure n° 71 « Mettre fin aux quotas SRU » (site de campagne, mise à jour le 12/09/2026 ; précise), 5e (date non plus récente
# que les autres), lecture SRU (même type : fin du quota de l'article 55 ; objectifs gardés en volume en zone tendue, dit dans le texte).
# (6) Lisnard : « Simplifier les taux de TVA » (tribune du 16/04/2026 ; intention), 4e ; pas d'étude du même type (la lecture « TVA sociale »
# portait sur la TVA unique à 25 %, retirée le 31/10).
def _evc(cid, th):
    """Texte « évidence » courant d'un thème : réécrit plus haut (OVR), sinon celui de data/life-*.json."""
    return OVR.get((cid, th), {}).get('evidence') or _jev(cid, th)
MEDIAS += ('rtl.fr',)
RTL2810 = _s("RTL, régularisation de 300 000 travailleurs sans papiers par R. Glucksmann, « avant même une éventuelle intégration au programme » ; "
             "réponse de L. Jacobelli, porte-parole de campagne de M. Le Pen (28/10)",
             'https://www.rtl.fr/actu/politique/presidentielle-2027-raphael-glucksmann-promet-de-regulariser-300-000-sans-papiers-s-il-est-elu-le-ps-pousse-la-mesure-a-l-assemblee-7900690049')
FI2910 = _s('franceinfo, la campagne de R. Glucksmann et la régularisation de 300 000 travailleurs sans papiers (29/10)',
            'https://www.franceinfo.fr/politique/raphael-glucksmann/on-est-obliges-de-faire-attention-comment-raphael-glucksmann-cherche-la-parade-face-a-l-hostilite-des-insoumis-sur-le-terrain_8257408.html')
SYN_JLM = _s('Mélenchon 2027, synthèse des contributions (17/07)', 'https://melenchon2027.fr/synthese-des-contributions/')
SURE_EP = _s('Site de campagne, France plus sûre', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-sure')
CB_RN = _s('Contre-budget 2027 du groupe RN', 'https://back.deputes-rn.fr/wp-content/uploads/2026/10/GRN-CONTRE-BUDGET-2027-DOSSIER.pdf')
E1_2510 = _s("Europe 1, premier discours de campagne à Orléans (25/10)", 'https://www.europe1.fr/politique/congres-du-rn-a-orleans-ce-quil-faut-retenir-du-premier-discours-de-campagne-de-marine-le-pen-1181118')
SRU_S = _src('Banque des Territoires – étude CGDD SRU', 2014, 'https://www.banquedesterritoires.fr/la-loi-sru-ca-sert-creer-du-logement-social')
R71 = _s('avecretailleau.fr, mesure n° 71 « Mettre fin aux quotas SRU » (12/09)', 'https://www.avecretailleau.fr/projet/mesure/construire-des-logements-sociaux-selon-les-besoins-locaux')
Z22 = _src("Programme présidentiel d'Éric Zemmour, « Pour que la France reste la France » (25/03/2022)", 2022,
           'https://assets.nationbuilder.com/themes/61c071ce4764e8b1483d1a8c/attachments/original/1648220408/programme_eric_zemmour_presidentielle_2022.pdf')
OFFICIEL_U['zemmour'] = (Z22['url'],)  # document du candidat, pour lui seul
DENT = ("Soins dentaires : 30,5 % des personnes sans complémentaire qui en avaient besoin n'ont pas pu les payer, 11,2 % avec (Drees, 2019) ; reste à charge "
        "supprimé sur une partie des prothèses : 92 % des patients avaient déjà consulté un dentiste, surtout plus de prothèses par patient (Cour des comptes, 2022) ; "
        "prise en charge intégrale par la Sécurité sociale non évaluée.")
DENT_S = _src("Sénat, rapport d'information n° 832 (2021-2022) sur l'enquête de la Cour des comptes sur la réforme du 100 % santé", 2022, 'https://www.senat.fr/rap/r21-832/r21-8321.pdf')
assert DENT_S['url'] in ETUDES  # étude (quiz de la fiche « dentaire »), jamais une attribution
# (1) Glucksmann : version précise en tête (2026, précise, la plus récente), lecture REGUL en premier (ordre des propositions)
_GR0 = "Régulariser les travailleurs sans papiers des secteurs qui manquent de main-d'œuvre"
_ps = _cur('glucksmann', 'economie'); assert [p['text'] for p in _ps].count(_GR0) == 1 and len(_ps) == 5
_put('glucksmann', 'economie', [_p("Régulariser environ 300 000 travailleurs sans papiers : titre de séjour après six mois de travail sur les deux dernières années")]
     + [p for p in _ps if p['text'] != _GR0])
_e = _evc('glucksmann', 'economie'); assert _e.endswith(" " + REGUL), _e
_ev('glucksmann', 'economie', REGUL + " " + _e[:-len(REGUL) - 1], add=[RTL2810, FI2910])
# (2) Le Pen (en tête : 2026, précise, la plus récente), Mélenchon (4e, intention), Philippe (5e, intention) : même lecture REGUL
_ps = _cur('le-pen', 'economie'); assert len(_ps) == 4 and not any(p['old'] for p in _ps)
_put('le-pen', 'economie', [_p("Zéro régularisation d'étrangers en situation irrégulière")] + _ps)
_ev('le-pen', 'economie', REGUL + " " + _evc('le-pen', 'economie'), add=[RTL2810, _s("Rassemblement national, nominations dans l'équipe de campagne (porte-parole, 27/10)",
    'https://rassemblementnational.fr/communiques/communique-de-presse-de-julien-sanchezdirecteur-de-campagne-de-marine-le-pen')] + REGUL_S)
_ps = _cur('melenchon', 'economie'); assert len(_ps) == 3 and all(p['verifiable'] and not p['old'] for p in _ps)
_put('melenchon', 'economie', _ps + [_p("Régulariser les travailleurs, les étudiants et les parents d'enfants scolarisés sans papiers", False)])
_ev('melenchon', 'economie', _evc('melenchon', 'economie') + " " + REGUL, add=[SYN_JLM] + REGUL_S)
_ps = _cur('philippe', 'economie'); assert len(_ps) == 4 and all(p['verifiable'] and not p['old'] for p in _ps)
_put('philippe', 'economie', _ps + [_p("« Verrou Schengen » : aucun État européen ne régularise massivement seul au-delà d'un seuil commun, sans l'accord de ses partenaires", False)])
_ev('philippe', 'economie', _evc('philippe', 'economie') + " " + REGUL, add=[SURE_EP] + REGUL_S)
# (3) Le Pen : environnement (loi Hulot en tête, puis la PPE de 2026, puis les propositions de 2022), santé (soins dentaires en tête)
_ps = _cur('le-pen', 'environnement')
assert [p['old'] for p in _ps] == [True, True, False] and _ps[2]['text'].startswith("S'opposer à la PPE 2026"), _ps
_put('le-pen', 'environnement', [_p("Abroger la loi Hulot de 2017, qui interdit la recherche d'hydrocarbures en France"), _ps[2], _ps[0], _ps[1]])
_so('le-pen', 'environnement', add=[E1_2510])
_ps = _cur('le-pen', 'sante'); assert len(_ps) == 3 and all(p['old'] for p in _ps)
_put('le-pen', 'sante', [_p('Rembourser à 100 % les soins dentaires, sur la base de la Sécurité sociale')] + _ps)
_ev('le-pen', 'sante', DENT + " " + _evc('le-pen', 'sante'), add=[CB_RN, DENT_S])
assert [p['text'] for p in _cur('melenchon', 'sante')][2] == '« 100 % Sécu » : soins prescrits remboursés intégralement'
_ev('melenchon', 'sante', _evc('melenchon', 'sante') + " " + DENT, add=[DENT_S])
# (4) Zemmour : propositions de 2022 (non reconfirmées), programme du candidat
OVR[('zemmour', 'logement')].update(proposals=[_p('Abroger la loi SRU, qui impose aux communes un quota de logements sociaux', True, True)], evidence=SRU, add=[Z22, SRU_S])
_ps = _cur('zemmour', 'libertes'); assert len(_ps) == 1
_put('zemmour', 'libertes', _ps + [_p('Abroger la loi Pleven de 1972 et revenir à la loi de 1881 sur la liberté de la presse', True, True)])
_ps = _cur('zemmour', 'economie'); assert len(_ps) == 3 and [p['old'] for p in _ps] == [False, True, True]
_put('zemmour', 'economie', _ps + [_p('Créer un Livret Innovation : épargne investie sans impôt dans les start-ups et entreprises innovantes', True, True)])
for _th in ('sante', 'ecole', 'libertes', 'economie', 'rayonnement'): _so('zemmour', _th, add=[Z22])
# (5) Retailleau : fin des quotas SRU, 5e ; lecture SRU après celle des intérêts d'emprunt (ordre des propositions)
_ps = _cur('retailleau', 'logement'); assert len(_ps) == 4 and all(p['verifiable'] and not p['old'] for p in _ps)
_put('retailleau', 'logement', _ps + [_p("Mettre fin aux quotas SRU : objectifs de logements sociaux en volume, fixés par contrat entre le préfet et l'intercommunalité, "
                                          "aucun en zone non tendue ; plus d'aides publiques au-delà de 30 % de logements sociaux")])
_ev('retailleau', 'logement', _evc('retailleau', 'logement') + " " + SRU, add=[R71, SRU_S])
# (6) Lisnard : simplification des taux de TVA, 4e (2026, intention) ; source déjà affichée dans le thème (tribune du 16/04)
_ps = _cur('lisnard', 'economie'); assert len(_ps) == 3 and all(p['verifiable'] and not p['old'] for p in _ps)
_put('lisnard', 'economie', _ps + [_p('Simplifier les taux de TVA', False)])

# (30) Même test « précis » pour une même formulation, appliqué à toutes les propositions affichées (y compris celles réécrites plus haut) :
# un changement de droit nommé (sortie du commandement intégré de l'OTAN, fin du droit de veto, mandat de l'ONU obligatoire, instrument ou
# accord nommé et ce qui y change) est précis ; un objectif, une orientation ou une création sans paramètre (plan, pôle, fonds) reste une intention.
# Chaque entrée doit servir (merge échoue sinon) : review 34, entrées des propositions retirées ou réécrites ôtées (blocage des réseaux sociaux
# et contrôle du Conseil constitutionnel, déjà hors affichage ; FED-EDIP-SAFE, contribution à l'UE de Retailleau : S106 ; pays sûrs : texte réécrit).
VFLIP = {'Assistant médical fondé sur l': False, 'Police de proximité modernisée': False, "Fonds national d'acquisition foncière": False,
         "commandement intégré de l'OTAN": True, "Sortir de l'OTAN": True,
         "Supprimer le droit de veto au sein de l'UE": True, "Aucune intervention militaire sans mandat de l'ONU": True,
         "Accord UE-Mercosur : en exclure l'élevage": True}

# (17) Étiquette d'efficacité calculée à partir des lectures : chaque lecture (texte exact, partagé par tous les candidats qui ont ce type de
# proposition) a un niveau, au regard de l'effet recherché par ce type de proposition : « prouvee » (les évaluations montrent l'effet recherché),
# « mitigee » (effet partiel, faible ou contrasté, obtenu avec un effet contraire notable, ou montré seulement pour une mesure voisine),
# « non_demontree » (pas d'effet, effet inverse, ou seulement un coût mesuré), « pas_d_etude » (ABSENT : la lecture constate l'absence
# d'évaluation) ; None : la lecture ne donne qu'un fait (droit existant, situation de départ). Étiquette d'un thème : aucune lecture d'étude
# ni constat d'absence → « pas d'étude » ; toutes les lectures au même niveau → ce niveau ; sinon « mitigée » (preuves partielles ou contrastées).
# Décision du 31/10 (option b, symétrique) : une étiquette extrême, « prouvée » comme « non démontrée », ne tient pas sur une seule lecture
# quand une autre lecture du même thème constate l'absence d'évaluation.
PROUV, MITIG, NONDEM, ABSENT = 'prouvee', 'mitigee', 'non_demontree', 'pas_d_etude'
NIV = {
 # sécurité
 PP: MITIG, PLACES: NONDEM, CASSE: ABSENT, HEN.strip(): NONDEM, MIN: NONDEM, CEF: ABSENT, DECH: ABSENT, RECO: ABSENT, EXPUL: NONDEM, GILL: MITIG,
 "Régulation carcérale : pas d'évaluation française identifiée.": ABSENT,
 "Cagoule en manifestation : délit depuis 2019.": None,
 "Pointage lors des manifestations : non évalué.": ABSENT,
 "Plateformes : amendes jusqu'à 6 % du chiffre d'affaires mondial et suspension temporaire du service déjà prévues par le règlement européen sur les services numériques ; effet non évalué.": ABSENT,
 # santé
 "Incitations financières à l'installation : effet modéré à court terme, très faible à long terme (Irdes). Aides jugées mal ciblées (Cour des comptes, 2024).": MITIG,
 "Restrictions d'installation des infirmières en zones sur-denses : meilleure répartition (Irdes, 2022). Régulation des médecins non évaluée en France ; la Cour des comptes la juge faisable.": MITIG,
 "Prévention : résultats français « médiocres » malgré des dépenses comparables à celles des voisins (Cour des comptes, 2021).": None,
 "Propositions non chiffrées.": None,
 "Former plus de médecins : des études qui durent jusqu'à 12 ans, et une hausse qui ne garantit pas leur répartition sur le territoire (Cour des comptes, 2024).": MITIG,
 "Maisons de santé : +3,4 jeunes généralistes pour 100 000 habitants par rapport aux territoires témoins (Irdes, 2020).": PROUV,
 "Fin de la T2A : pas d'évaluation identifiée.": ABSENT,
 "Coopération médecin-infirmière Asalée : patientèle +6,6 %, consultations inchangées, qualité non mesurée (Irdes, 2019). La délégation aux pharmaciens est peu évaluée.": MITIG,
 "Jour de carence (fonction publique, 2012-2013) : absences de deux jours −50 %, absences d'une semaine à trois mois +25 %, total inchangé (Insee, 2017).": NONDEM,
 "Aides à l'installation : au moins 15 dispositifs, 205 M€ en 2023 ; plusieurs jugées coûteuses et inefficaces, d'autres utiles (Cour des comptes, 2025).": MITIG,
 "Médecins salariés par l'État et obligation de garde : pas d'évaluation française identifiée.": ABSENT,
 AME: NONDEM,
 DENT: MITIG,  # review 37 : renoncement plus fréquent sans complémentaire, peu de nouveaux patients quand le reste à charge disparaît
 # école
 PARC: MITIG, DD: MITIG, SAL: MITIG, EXAM: MITIG, EX1: PROUV, GN: NONDEM, RED: NONDEM, AUTO: MITIG, CHEQ: MITIG, CARTE: MITIG, MIXITE: MITIG, PETITES: MITIG,
 "Uniforme : climat amélioré selon 36% des directeurs, effet quasi nul sur les résultats (ministère, 2026).": MITIG,
 "Établissements pour élèves exclus (2010) : résultats mitigés, un quart des élèves sans solution en 2012, abandonnés (inspections, 2012).": MITIG,
 "Orientation : des réunions avec le chef d'établissement pour les élèves faibles de 3e et leurs parents ont réduit redoublement et décrochage de 25 à 40 % (essai aléatoire, France, 2017).": PROUV,
 "Amendes aux parents d'absentéistes : sans lien avec le niveau d'absences (pays de Galles, 2018) ; pas d'évaluation française.": NONDEM,
 # environnement
 EPR: MITIG, RTE: MITIG, VE: MITIG,
 "Marché carbone des carburants (en place en 2028) : +10 à 15 c€ par litre à son entrée en vigueur (Institut Montaigne, 2025) ; taxe carbone suédoise : émissions des transports −11 % (2019).": MITIG,
 "RTE : scénarios sans nouveau nucléaire plus coûteux, de l'ordre de 10 Md€/an (jusqu'à 20 dans certaines variantes).": MITIG,
 "HCC 2026 : baisse requise >4 %/an, contre −2,1 % en 2025.": None,
 "HCC 2026 : France « pas prête », plan d'adaptation sous-financé, risque de « maladaptation ». Aucune évaluation d'un fonds unique d'adaptation.": ABSENT,
 "HCC 2026 : émissions −2,1 % en 2025, un rythme qui doit au moins doubler ; leasing social et MaPrimeRénov' jugés sous-dimensionnés.": None,
 # logement
 RENO: MITIG, SRU: NONDEM,
 "Cour des comptes : la crise exige d'accroître durablement l'offre.": None,
 "Aides à l'accession : environ 15 % de ménages réellement déclenchés, forte aubaine ; PTZ associé à +7 % sur le prix des terrains (IPP, 2016).": NONDEM,
 "Encadrement des loyers : loyers −2 à −4 %. Effet sur l'offre non documenté en France, négatif à moyen terme dans la littérature internationale (Cour des comptes, 2026).": MITIG,
 "Crédit d'impôt sur les intérêts d'emprunt (TEPA, 2007) : 1,1 Md€ en 2009, « peu d'effets sur l'accession à la propriété » (Sénat, 2010).": NONDEM,
 # libertés
 "Voile interdit à l'école : diplômes des filles de culture musulmane en hausse après 1994 (IZA, 2019) ; après 2004, aucun gain de plus (IZA, 2019) ou scolarité des filles en baisse (APSR, 2020) ; aucune étude sur l'université, le sport ni les bâtiments publics.": MITIG,
 "Voile interdit à l'école : diplômes des filles de culture musulmane en hausse après 1994 (IZA, 2019) ; après 2004, aucun gain de plus (IZA, 2019) ou scolarité des filles en baisse (APSR, 2020) ; aucune étude sur l'université ni sur les dissolutions.": MITIG,
 RIC: MITIG, VOTE16: MITIG, SUISSE: MITIG, RIP: None, SECU: ABSENT, CSM: None,
 "Aucune évaluation empirique identifiée de l'effet des ordonnances ou du lien parquet-exécutif sur l'efficacité de l'action publique.": ABSENT,
 "Convention climat : 10 % des propositions reprises telles quelles, 53 % rejetées (Courant, 2021).": MITIG,
 "Proportionnelle : pas d'évaluation française récente identifiée.": ABSENT,
 PRIM: ABSENT,
 # économie
 IPROD: NONDEM, TEPA: NONDEM, CODE: ABSENT, CU: MITIG, IA: NONDEM,
 "Règle d'or : déficit réduit de 1,2 à 1,5 point de PIB selon un sous-groupe d'études, effet plus faible avec les meilleures méthodes (30 études, ZEW, 2016) ; Allemagne, dette de 81 % à 58 % du PIB (2010-2019), 60 Md€ d'emprunts annulés (2023).": MITIG,
 "Incertitude politique : suivie de moins d'investissement (États-Unis), de production et d'emploi (12 pays), sans preuve de causalité (2016) ; règle de stabilité fiscale non évaluée.": MITIG,
 "Lois Egalim : efficacité économique difficile à établir, contrats écrits peu appliqués ; part agricole du prix au détail en hausse en 2021-2023 (Assemblée nationale, 2025).": MITIG,
 "Régularisation liée à un contrat de travail (Espagne, 2005, ≈ 600 000 personnes) : cotisations +4 000 € par personne et par an, salaires des natifs peu qualifiés du secteur déclaré en hausse, pas d'afflux d'immigration mesuré, retour partiel au travail non déclaré (2025) ; délinquance des régularisés −0,6 point (Italie, 2017).": MITIG,
 "Chômage plus court de 12 %, mais emplois peu durables (Dares, 2025).": MITIG,
 "Experts SMIC (2025) : risque pour l'emploi peu qualifié, SMIC à 62,5 % du médian.": MITIG,
 "Bozio-Wasmer (2024) : supprimer ces exonérations sans recyclage coûterait ~61 000 emplois.": MITIG,
 "CAE (2021) : héritage très concentré, 35-40 % échappe à l'impôt, ~12 Md€ récupérables ; effets économiques non évalués faute de données fiables.": ABSENT,
 # rayonnement
 VED: MITIG, UEU: None, FIN: MITIG, DOUANE: NONDEM, SCH: NONDEM,
 "Pas d'évaluation publique de cet objectif.": ABSENT,
 "Pas d'évaluation publique de l'effet d'une dénonciation de l'accord de 1968 sur les relations ou l'influence de la France.": ABSENT,
 "Cour des comptes européenne (2024), plan de relance commun : absorption en retard, 24 % des résultats attendus manquants ; France au-dessus de la moyenne.": MITIG,
}
LECT = sorted(NIV, key=len, reverse=True)
def niveau(ev, ou):
    """Étiquette d'un thème à partir de ses lectures : chaque morceau du texte doit être une lecture connue (sinon le pipeline échoue)."""
    i, lv = 0, []
    while i < len(ev):
        if ev[i] == ' ': i += 1; continue
        k = next((k for k in LECT if ev.startswith(k, i)), None)
        assert k, f"life.py : lecture sans niveau ({ou}) : {ev[i:i + 90]!r}"
        if NIV[k]: lv.append(NIV[k])
        i += len(k)
    return 'pas_d_etude' if not lv else lv[0] if len(set(lv)) == 1 else 'mitigee'

CAMP = {'melenchon': 'melenchon2027.fr', 'philippe': 'edouardphilippe.fr', 'attal': 'attalpresident.fr', 'lisnard': 'lisnard.cards'}

def merge(D):
    parts = [f for f in ('life-a.json', 'life-b.json', 'life-eco.json') if os.path.exists(os.path.join(H, 'data', f))]
    if not parts: return D
    ev = J('evidence_levels.json') if os.path.exists(os.path.join(H, 'data', 'evidence_levels.json')) else {}
    WEAKD[:] = D.get('weak_domains', [])
    # étiquetage des sites faibles (la Vie quotidienne peut ne plus en citer aucun : le mécanisme est vérifié ici, review 34)
    assert (NOFF('https://votons-2027.fr/x', 'x'), NOFF('https://www.wikiglucksmann.fr/x', 'x'), NOFF('https://www.franceinfo.fr/x', 'x'), NOFF('https://votons-2027.fr/x', 'x (agrégateur)')) \
        == (' (agrégateur)', ' (non officiel)', '', ''), "life.py : étiquetage des agrégateurs et des sites non officiels"
    life = {}; used = set(); vused = set()
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
                if o:
                    th.update({k: v for k, v in o.items() if k not in ('add', 'drop')})
                    th['sources'] = [x for x in th['sources'] if not any(d in x['url'] for d in o.get('drop', []))]
                    th['sources'] += [s for s in o.get('add', []) if s['url'] not in {x['url'] for x in th['sources']}]
                # test « précis » appliqué après les réécritures (review 32) : toutes les propositions affichées
                th['proposals'] = [dict(p) for p in th['proposals']]
                for p in th['proposals']:
                    for k0, v0 in VFLIP.items():
                        if k0 in p['text']: p['verifiable'] = v0; vused.add(k0)
                olds = [d for d in ORIG if any(d in x['url'] for x in th['sources'])]
                if olds:
                    used.update(olds)
                    th['sources'] = [x for x in th['sources'] if not any(d in x['url'] for d in olds)]
                    th['sources'] += [dict(s) for s in {ORIG[d]['url']: ORIG[d] for d in olds}.values() if s['url'] not in {x['url'] for x in th['sources']}]
                # une année et un titre par source (review 32) ; étiquette des sites non officiels et des agrégateurs sur toutes les sources
                th['sources'] = [dict(x, label=TITRE_S[x['url']][0], year=TITRE_S[x['url']][1]) if x['url'] in TITRE_S else x for x in th['sources']]
                th['sources'] = [dict(x, label=x['label'] + NOFF(x['url'], x['label'])) for x in th['sources']]
                # étiquette d'efficacité calculée à partir des lectures (review 32) ; aucune proposition → pas d'étiquette
                th['evidence_level'] = niveau(th['evidence'], f"{cid}.{th['theme']}") if th['proposals'] else None
                life.setdefault(cid, {})[th['theme']] = th
        if 'baseline' in x: D.setdefault('baseline', {}).update({k: [dict(i, label=html.unescape(i['label'])) for i in v] for k, v in x['baseline'].items()})
    assert used == set(ORIG), f"ORIG sans effet : {set(ORIG) - used}"
    morte = [k for k in NIV if not any(k in th['evidence'] for v in life.values() for th in v.values())]
    assert not morte, f"life.py : lecture de NIV qui ne sert plus (texte réécrit ?) : {morte[0][:80]!r}"
    assert vused == set(VFLIP), f"life.py : entrée de VFLIP qui ne sert plus (proposition retirée ou réécrite ?) : {sorted(set(VFLIP) - vused)}"
    # une source qui parle pour le candidat, pour chaque proposition affichée (review 34 ; règle et ATTR_OK plus haut)
    A, vus = J('life-attribution.json'), set()
    for cid, v in life.items():
        for th, t in v.items():
            aff = {x['url'] for x in t['sources']}
            for p in t['proposals']:
                us = A.get(cid, {}).get(th, {}).get(p['text'])
                assert us, f"life-attribution.json : proposition sans source qui parle pour le candidat ({cid}.{th}) : {p['text']!r}"
                vus.add((cid, th, p['text']))
                for u in us:
                    assert u in aff, f"life-attribution.json : source non affichée dans le thème ({cid}.{th}) : {u}"
                    assert not host_in(u, NONOFF) and not host_in(u, WEAKD), f"life-attribution.json : agrégateur ou site non officiel ({cid}.{th}) : {u}"
                    assert ATTR_OK(cid, u), f"life-attribution.json : ni le candidat ou son parti, ni un média reconnu, ni une fiche de programme, ou bien une étude ({cid}.{th}) : {u}"
    reste = [f"{c}.{th} : {x!r}" for c, v in A.items() for th, w in v.items() for x in w if (c, th, x) not in vus]
    assert not reste, f"life-attribution.json : proposition qui n'est plus affichée (texte réécrit ?) : {reste[:3]}"
    ids = [c['id'] for c in D['candidates']]
    themes = [t for t in THEMES if any(t in v for v in life.values())]
    D['life_themes'] = themes
    D['life'] = {cid: [life.get(cid, {}).get(t) or {'theme': t, 'proposals': [], 'indicator': None, 'evidence': 'Pas de proposition publiée sur ce thème.', 'sources': [], 'evidence_level': None} for t in themes] for cid in ids}
    b = J('baseline.json'); b.update(D.get('baseline', {})); D['baseline'] = b
    return D
