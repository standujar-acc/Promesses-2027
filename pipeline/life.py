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
