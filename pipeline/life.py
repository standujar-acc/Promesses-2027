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
# --- review 23 : « casseur-payeur » et propositions oubliées (29/10/2026) ; registre S097 à S119
# Règle d'ordre, la même pour tous, quand un thème dépasse 3 propositions : d'abord celles de 2026 (les non reconfirmées passent après),
# parmi elles les précises avant les intentions, puis les plus récentes ; à égalité ou à date inconnue, l'ordre déjà affiché est gardé
# (une page de programme mise à jour n'est pas une nouvelle annonce). Les propositions retirées de l'affichage sont notées au registre (S106).
# Les listes ci-dessous remplacent celles de data/life-*.json pour ces thèmes (même forme que norm_prop : text, verifiable, old).
CASSE = ("Casseur-payeur : l'auteur et les parents d'un mineur doivent déjà réparer ; recours de l'État (loi de 2019) jamais utilisé ; "
         "dégâts à sa charge : 4,1 M€ par an en moyenne ; effet dissuasif non évalué ; projet de loi voté au Sénat le 28/10.")
CASSE_S = [{'label': "Sénat, projet de loi n° 952 sur la réparation des dommages (exposé des motifs, étude d'impact)", 'year': 2026, 'url': 'https://www.senat.fr/leg/pjl25-952.pdf'},
           {'label': 'LCP, adoption du projet de loi au Sénat', 'year': 2026, 'url': 'https://lcp.fr/actualites/projet-de-loi-casseurs-payeurs-le-texte-transmis-a-l-assemblee-apres-son-adoption-au'}]
PLACES = "Nouvelles places de prison vite comblées (Sénat, 2023)."
IA = "DG Trésor (2024) : aucun effet macroéconomique significatif de l'IA mesuré à ce stade."
IA_S = {'label': "DG Trésor, enjeux de l'IA", 'year': 2024, 'url': 'https://www.tresor.economie.gouv.fr/Articles/65035441-140e-4e2f-b1a0-2c5abceb6cc7/files/337f850a-3329-4803-b509-e5276c04ab30'}
# RTE_S : source officielle (résumé exécutif), définie plus haut avec les originaux des reprises d'agence (registre S027)
def _p(t, v=True, old=False): return {'text': t, 'verifiable': v, 'old': old}
def _s(label, url): return {'label': label, 'year': 2026, 'url': url}
def _upd(cid, th, props, add=(), drop=(), **kw):
    o = OVR.setdefault((cid, th), {}); o['proposals'] = props; o.update(kw)
    if add: o['add'] = o.get('add', []) + [s for s in add if s['url'] not in {x['url'] for x in o.get('add', [])}]
    if drop: o['drop'] = o.get('drop', []) + list(drop)
# sécurité : casseur-payeur (même texte « évidence » pour tous, CASSE) et propositions ajoutées
OVR[('le-pen', 'securite')] = {'evidence': PP + " " + PLACES + " " + CASSE, 'evidence_level': 'mitigee', 'add': [IPP_PP] + CASSE_S + [
    _s('franceinfo, Le Pen et les casseurs (21/10)', 'https://www.franceinfo.fr/politique/marine-le-pen/nous-sommes-confrontes-a-un-etat-qui-s-effondre-estime-marine-le-pen_8246899.html'),
    _s('Capital, Le Pen et les casseurs (21/10)', 'https://www.capital.fr/economie-politique/marine-le-pen-veut-faire-payer-a-vie-les-casseurs-et-solidairement-ceux-qui-ne-partent-pas-apres-les-sommations-1531173')],
  'proposals': [_p('Faire payer les dégâts aux casseurs : responsabilité solidaire, prélèvement sur allocations ou salaire, parents pour les mineurs'),
                _p('Rétablir les peines planchers, supprimer les remises de peine', True, True), _p('Porter le parc à 85 000 places de prison', True, True)]}
OVR[('philippe', 'securite')] = {'evidence': PP + HEN + " " + CASSE, 'evidence_level': 'mitigee', 'add': [IPP_PP] + CASSE_S + [
    _s('Capital, plan contre les casseurs (29/10)', 'https://www.capital.fr/economie-politique/prison-des-la-premiere-casse-et-salaire-ponctionne-le-plan-dedouard-philippe-contre-les-casseurs-1531388'),
    _s("L'Express via Orange, entretien au Point (27/10)", 'https://actu.orange.fr/politique/presidentielle-2027-edouard-philippe-veut-diviser-l-immigration-legale-par-deux-face-a-l-echec-de-l-integration-l-express-via-6medias-CNT000002tpDKM.html')],
  'proposals': [_p('Courtes peines de prison dès la première infraction'), _p("Peines planchers pour violences contre dépositaires de l'autorité publique et professeurs"),
                _p('Faire payer les dégâts aux casseurs : prélèvement sur leurs salaires ou prestations sociales')]}
OVR[('retailleau', 'securite')] = {'evidence': HEN.strip() + " " + CASSE, 'evidence_level': 'mitigee', 'drop': ['souhaite-instaurer-des-peines-minimales', 'Note_IPP_105'], 'add': [HEN_S] + CASSE_S + [
    _s('Capital, Retailleau et les casseurs (RCF, 27/10)', 'https://www.capital.fr/economie-politique/les-aides-ce-nest-pas-un-du-bruno-retailleau-veut-saisir-le-rsa-les-apl-et-les-allocations-des-casseurs-1531316'),
    _s('franceinfo, déchéance de nationalité (19/10)', 'https://www.franceinfo.fr/societe/mobilisation-du-17-octobre/violences-du-17-octobre-bruno-retailleau-denonce-une-convergence-entre-l-extreme-gauche-et-des-racailles-issues-de-l-immigration_8245450.html')],
  'proposals': [_p('Faire payer les dégâts aux casseurs : présomption de responsabilité dans un attroupement violent, aides sociales remises en cause'),
                _p('Majorité pénale abaissée à 15 ans, courtes peines de 15 jours en centres dédiés'),
                _p("Déchéance de nationalité des binationaux auteurs de pillages ou de violences contre les forces de l'ordre")]}
OVR[('zemmour', 'securite')] = {'evidence': PP + " " + CASSE, 'evidence_level': 'mitigee', 'drop': ['chicagounbound.uchicago.edu/jle/vol57'], 'add': [IPP_PP] + CASSE_S + [
    _s('Europe 1, Zemmour et les casseurs (7/10)', 'https://www.europe1.fr/politique/blocus-des-lycees-eric-zemmour-veut-faire-payer-les-casseurs-et-leurs-parents-jusqua-la-nuit-des-temps-1129292'),
    _s('Entrevue, déclarations sur CNews (18/10)', 'https://entrevue.fr/medias/une-horde-de-barbares-maghrebins-et-africains-eric-zemmour-provoque/'),
    _s('Entrevue, émission du 25/10', 'https://entrevue.fr/politique/on-va-vers-une-guerre-civile-eric-zemmour-alerte-sur-le-chaos-en-france/')],
  'proposals': [_p("Rétablir les peines planchers, supprimer le juge de l'application des peines"),
                _p('Faire payer les dégâts aux casseurs et à leurs parents, y compris sur leurs allocations ; rétablir la loi anticasseurs de 1970'),
                _p('Déchéance de nationalité puis départ des binationaux auteurs des violences')]}
OVR[('attal', 'securite')] = {'evidence': CASSE, 'evidence_level': 'pas_d_etude',
  'drop': ['lesactusdunet.com', 'je-propose-de-supprimer-le-juge', 'plus-grande-reforme-institutionnelle', 'ssrn.com/abstract=3330413', 'next.ink/178412'], 'add': CASSE_S + [
    _s("attalpresident.fr, rétablir l'ordre (BFM TV, 19/10)", 'https://attalpresident.fr/actualites/gabriel-attal-retablir-ordre-mettre-fin-impunite'),
    _s('attalpresident.fr, entretien sur RTL (19/10)', 'https://attalpresident.fr/actualites/gabriel-attal-rtl-retablir-ordre-jeunesse-avenir-france'),
    _s('attalpresident.fr, France 2 (23/10)', 'https://attalpresident.fr/actualites/gabriel-attal-retablir-ordre-pacte-avenir-jeunesse'),
    _s('RFI, porte-parole de campagne (22/10)', 'https://www.rfi.fr/fr/podcasts/invit%C3%A9-politique/20261022-manifestations-il-faut-faire-payer-ceux-qui-cassent-soutient-c%C3%A9line-g%C3%A9raud-porte-parole-de-gabriel-attal')],
  'proposals': [_p('Faire payer les dégâts aux casseurs (« Tu casses, tu répares ») : responsabilité automatique des deux parents d\'un mineur'),
                _p("Comparution immédiate dès 16 ans et fin de l'excuse de minorité automatique pour les mineurs récidivistes"),
                _p('Reconnaissance faciale et IA pour identifier les casseurs ; militaires et réservistes pour la garde statique des bâtiments publics')]}
OVR[('lisnard', 'securite')] = {'evidence': CASSE, 'evidence_level': 'pas_d_etude', 'drop': ['lisnard.cards', 'r23-037_mono', 'Discours-de-David-Lisnard-a-Saint-Raphael'], 'add': CASSE_S + [
    _s('Europe 1, Objectif Élysée 2027 (27/10)', 'https://www.europe1.fr/politique/en-direct-emeutes-parcoursup-primaire-a-droite-ce-quil-faut-retenir-de-linterview-de-david-lisnard-dans-objectif-elysee-2027-1186743'),
    _s('Nouvelle Énergie, programme « Sécurité »', 'https://www.unenouvelleenergie.fr/notre-programme/securite/'),
    _s('Nouvelle Énergie, entretien au Point (23/10)', 'https://www.unenouvelleenergie.fr/quand-macron-a-parle-pas-un-casseur-na-tremble/')],
  'proposals': [_p('Majorité pénale à 16 ans, excuse de minorité réduite (de 50 % à 20 % de la peine), établissements disciplinaires fermés'),
                _p("Faire payer les dégâts aux casseurs : déduits de leurs aides sociales s'ils ne sont pas solvables"),
                _p('Fichier des casseurs avec obligation de pointer pendant les manifestations ; cagoule interdite, circonstance aggravante')]}
# libertés
_upd('le-pen', 'libertes', [_p('Élire les députés à la proportionnelle avec prime majoritaire'), _p('Inscrire la « communauté nationale » dans la Constitution'),
                            _p("Instaurer le référendum d'initiative citoyenne", True, True)],
     add=[_s("Europe 1, discours d'Orléans (25/10)", 'https://www.europe1.fr/politique/congres-du-rn-a-orleans-ce-quil-faut-retenir-du-premier-discours-de-campagne-de-marine-le-pen-1181118')])
_upd('melenchon', 'libertes', [_p('Convoquer une Constituante pour une 6e République'), _p('Droit de vote à 16 ans'), _p("Proportionnelle à l'Assemblée et RIC", True, True)],
     add=[_s("L'Express via Orange, meeting de Clermont-Ferrand (11/10)", 'https://actu.orange.fr/politique/presidentielle-2027-suppression-de-parcoursup-droit-de-vote-a-16-ans-jean-luc-melenchon-multiplie-les-propositions-pour-les-jeunes-magic-CNT000002sCYOg.html')])
_upd('lisnard', 'libertes', [_p('Rétablir le septennat'), _p("Article 11 sans limite thématique et référendum d'initiative populaire à seuil atteignable"),
                             _p("Interdire les Frères musulmans et le voile à l'université")],
     add=[_s('Nouvelle Énergie, programme « Sécurité »', 'https://www.unenouvelleenergie.fr/notre-programme/securite/')])
# école
OVR[('melenchon', 'ecole')] = {'evidence': "Petites écoles : regroupements suivis d'une baisse passagère des résultats (Danemark, 2018) ou d'un léger gain (Pays-Bas, 2016).",
  'add': [x for x in OVR[('melenchon', 'ecole')]['add'] if x not in DD_S] + [
    _s('LFI, note sur les comptes publics (14/10)', 'https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf'),
    _s("L'Express via Orange, meeting de Clermont-Ferrand (11/10)", 'https://actu.orange.fr/politique/presidentielle-2027-suppression-de-parcoursup-droit-de-vote-a-16-ans-jean-luc-melenchon-multiplie-les-propositions-pour-les-jeunes-magic-CNT000002sCYOg.html')],
  'drop': NOAEF, 'proposals': [_p('Supprimer Parcoursup et MonMaster'), _p('Transport scolaire limité à 15 minutes, écoles à classe unique maintenues'), _p("Scolarité obligatoire jusqu'à 18 ans", True, True)]}
_upd('glucksmann', 'ecole', [_p('Loi de programmation éducation sur cinq ans : bâti, salaires, effectifs'), _p('Conditionner les aides au privé (10 Md€/an) à la mixité sociale'), _p('Abroger Parcoursup')],
     add=[_s('franceinfo, propositions à Matignon (22/10)', 'https://www.franceinfo.fr/societe/mobilisation-du-17-octobre/reunion-des-partis-a-matignon-sebastien-lecornu-a-fait-perdre-du-temps-au-pays-denonce-manuel-bompard_8249335.html')])
OVR[('retailleau', 'ecole')] = {'evidence': "Examen de fin de cycle : un tiers d'année gagné en maths (Allemagne, 2005). Redoublement : effet proche de zéro à court terme, négatif à long terme, chances de diplôme réduites (Cnesco, 2014).",
  'evidence_level': 'mitigee', 'add': EXAM_S[:1] + [_s("Public Sénat, sélection à l'université (14/10)", 'https://www.publicsenat.fr/actualites/politique/crise-lyceenne-bruno-retailleau-veut-une-selection-a-luniversite')],
  'proposals': [_p("Sélection à l'entrée de l'université et nouvelle plateforme d'admission au mérite à la place de Parcoursup"),
                _p("Rétablir un examen d'entrée en sixième"), _p('Fin du passage automatique de classe, décidé par le conseil de classe')]}
_upd('zemmour', 'ecole', [_p("Retour à la dictée, au calcul mental et à la récitation ; autonomie des chefs d'établissement ; concurrence entre public et privé", False),
                          _p("Certificat d'études en fin de primaire", True, True), _p('Classes de niveau au collège', True, True)],
     add=[_s('Entrevue, émission du 25/10', 'https://entrevue.fr/politique/on-va-vers-une-guerre-civile-eric-zemmour-alerte-sur-le-chaos-en-france/')])
# environnement
_upd('zemmour', 'environnement', [_p("Six EPR d'ici 2035 et quatorze d'ici 2045"), _p('Abroger le marché carbone européen sur les carburants et le chauffage (SEQE 2) avant 2028'),
                                  _p("Fin des financements français et européens à l'éolien", True, True)],
     add=[_s('Reconquête, pétition sur les carburants', 'https://www.stop-hausse-carburant.fr/')])
# économie
OVR[('le-pen', 'economie')] = {'evidence': RTE, 'evidence_level': 'mitigee', 'drop': ['FS_ImpotsProductions'], 'add': [RTE_S,
    _s("LCP, règle d'or (tribune du 1/10)", 'https://lcp.fr/actualites/budget-comment-fonctionnerait-la-regle-d-or-que-marine-le-pen-veut-faire-adopter-par')],
  'proposals': [_p('Supprimer les subventions aux renouvelables : 5 Md€ dès la 1re année'), _p('Supprimer plus de 120 taxes'),
                _p("Règle d'or budgétaire par référendum : déficit de 4,9 % du PIB en 2027 à 2,4 % en 2033")]}
OVR[('philippe', 'economie')] = {'evidence': "Heures sup défiscalisées (TEPA) : pas d'effet significatif sur les heures travaillées (IPP, 2012). Chômage plus court de 12 %, mais emplois peu durables (Dares, 2025).",
  'evidence_level': 'mitigee', 'drop': ['face-au-delire-fiscal', 'FS_ImpotsProductions'], 'add': [_s('Site Édouard Philippe, « Pour une France plus prospère »', 'https://www.edouardphilippe.fr/priorites/pour-une-france-plus-prospere')],
  'proposals': [_p('Heures au-delà de 35 h défiscalisées, zéro cotisation au-delà de 37 h'), _p('Indemnisation chômage ramenée de 18 à 12 mois avant 50 ans'),
                _p("Règle d'or budgétaire par référendum : déficit à 2 % du PIB en fin de quinquennat")]}
_upd('glucksmann', 'economie', [_p('Taxer le 1 % des plus gros héritages pour hausser les salaires nets'), _p("État d'urgence industriel pour les secteurs menacés par la Chine", False),
                                _p('« Buy European Act » : préférence européenne dans les marchés publics', False, True)],
     add=[_s('LCP, premier meeting (13/06)', 'https://lcp.fr/actualites/gagner-en-2027-raphael-glucksmann-lance-sa-campagne-et-veut-ramener-la-gauche-au-pouvoir')])
OVR[('attal', 'economie')] = {'evidence': "Cour des comptes (2025) : coûts EPR2 inconnus, risque d'échec du programme.", 'evidence_level': 'mitigee',
  'drop': ['tresor.economie.gouv.fr', 'rupture-economique-dans-les-echos'], 'add': [
    _s('attalpresident.fr, programme « Travail & salaires »', 'https://attalpresident.fr/programme/travail-salaires'),
    _s('AFP via Orange, conférence économique (28/10)', 'https://actu.orange.fr/politique/attal-veut-une-economie-quot-liberale-quot-mais-quot-planifiee-quot-pour-financer-un-quot-capitalisme-de-l-innovation-quot-CNT000002tqRW2.html'),
    _s('attalpresident.fr, lettre aux Français (15/10)', 'https://attalpresident.fr/actualites/gabriel-attal-lettre-aux-francais-plan-finances-publiques')],
  'proposals': [_p('Remplacer le Code du travail par une « Constitution du travail » de quelques principes, le reste négocié par branche et par entreprise'),
                _p("Loi de stabilité fiscale et normative de dix ans votée dès l'été 2027 ; un quart de la charge administrative des entreprises supprimé"),
                _p('Construire 14 nouveaux réacteurs nucléaires, puis un par an')]}
_upd('retailleau', 'economie', [_p('Supprimer les impôts de production, dans 30 Md€ de baisses pour les entreprises'),
                                _p("Code du travail refondé sur 50 principes, le reste supplétif et renvoyé aux accords d'entreprise ou de branche"),
                                _p('Exonérer de cotisations sociales les heures supplémentaires', False)],
     add=[_s('avecretailleau.fr, code du travail sur 50 principes', 'https://www.avecretailleau.fr/projet/mesure/refonder-le-code-du-travail-sur-50-principes-rendre-le')])
_upd('zemmour', 'economie', [_p("Former à l'IA dès l'école ; faire de la France la troisième puissance mondiale de l'IA", False),
                             _p('Baisser de 30 Md€ supplémentaires les impôts de production', True, True), _p("Prime « zéro charge » jusqu'à trois mois de salaire", True, True)],
     evidence="IPP (2025) : la baisse des impôts de production de 2021 n'a eu aucun effet mesurable sur l'investissement et un impact limité sur la masse salariale. " + IA,
     add=[IA_S, _s('CNews, discours de rentrée (13/09)', 'https://www.cnews.fr/france/2026-09-13/presidentielle-2027-remigration-intelligence-artificielle-ce-quil-faut-retenir-du')])
# rayonnement
_upd('attal', 'rayonnement', [_p('Part européenne du calcul mondial : de 3 % à 20 %'),
                              _p("Taxes ciblées sur l'acier, les voitures électriques et les panneaux solaires chinois vendus à perte ; contrôle strict des investissements chinois dans les ports, télécoms et centres de données")],
     add=[_s('attalpresident.fr, programme « Frontières »', 'https://attalpresident.fr/programme/frontieres')])
_upd('retailleau', 'rayonnement', [_p('Schengen réservé aux Européens : visas limités au pays qui les délivre, comme règle de droit commun'),
                                   _p("Réduire la contribution française au budget de l'UE par la négociation", False), _p('Intégrer les dépenses de défense dans le calcul de cette contribution', False)],
     add=[_s('Les Républicains, entretien au JDD (2/08)', 'https://republicains.fr/actualites/2026/08/02/lespace-schengen-doit-etre-reserve-aux-europeens/')])

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
