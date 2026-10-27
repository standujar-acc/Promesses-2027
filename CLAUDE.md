# Promesses 2027

App de fact-checking et de chiffrage des programmes de la présidentielle 2027 (1er tour 18 avril 2027, 2d tour 2 mai 2027). 8 candidats : Le Pen, Mélenchon, Glucksmann, Philippe, Retailleau, Attal, Lisnard, Zemmour (ordre = moyenne des sondages, voir `ORD` dans `pipeline/corrections.py`). Interface et contenus en français, mobile d'abord. Le porteur du projet écrit en français familier ; répondre en français.

## Règle n°1 : neutralité
Même traitement pour tous les candidats, toujours. Avant toute modification d'une mesure, d'un verdict, d'un texte ou d'une étude, chercher les mesures du même type chez les autres candidats et appliquer la même règle. Pas d'adjectifs de jugement, pas d'obstacle ou de formulation sévère réservé à un seul camp. Le site de campagne d'un candidat n'est jamais une source sur un autre. Agrégateurs et sites non officiels : marqués comme tels (`weak_domains`, `NOFF` dans `life.py`).

## Pipeline (source de vérité : `pipeline/`)
```
python3 pipeline/run.py     # corrections → totaux → build → public/index.html, public/data/promesses-2027.json
python3 tests/smoke.py      # Playwright + Chromium
```
- Ne jamais éditer `public/` ni le tableau du README à la main (générés par `run.py`) ; la CI vérifie qu'ils correspondent aux sources.
- **Guide de développement : [DEVELOPPER.md](DEVELOPPER.md)** (circuit d'une modification, où modifier quoi, liste de contrôle).
- **À chaque changement**, dans le même commit : registre `pipeline/data/suivi.json` (ajouter les manques et points à trancher, fermer ce qui est réglé ; ne jamais supprimer un point), historique `D.changelog` (une entrée par sujet et par jour, ajoutée après les autres car la dernière s'affiche en haut), date `D['asof']` dans le bloc daté de `corrections.py`. Un arbitrage (méthode, interprétation, changement important d'un total) se tranche en appliquant les règles communes aux faits vérifiés (délégation du porteur du projet, 27/10/2026) : la décision, la règle appliquée et les sources sont notées dans le registre et signalées dans la PR. Seul un choix sans règle applicable ni fait décisif reste un point `a_trancher`.
- `pipeline/base.json` : base fusionnée d'origine. `corrections.py` : toutes les corrections, datées par bloc (« review 2 », « review 3 »…), puis **les totaux sont calculés en dernier** (ne rien modifier après le bloc `# --- totaux`).
- `build.py` : textes de la méthode (`D.method`, à garder identique à METHODOLOGIE.md) et historique (`D.changelog`, voir ci-dessus).
- `life.py` : volet vie quotidienne. `OVR` = même lecture d'une étude pour un même type de mesure ; `VFLIP` = même test « précis / intention ».
- `data/quiz_plain.json` : textes du quiz en langage courant (`[texte, concrètement]`) ; pas de coût, pas de faisabilité, pas de chiffre qui trahit le candidat. Une mesure sans entrée n'apparaît pas dans le quiz. Les propositions « Vie quotidienne » précises et reconfirmées y entrent aussi : clé `candidat.thème.n` (n-ième proposition du thème), valeur `[texte, concrètement, texte publié]` ; le pipeline échoue si la proposition publiée change.
- `data/quiz_effets.json` : par proposition du quiz, un **constat** (la réalité française mesurée que la proposition veut traiter : le dernier chiffre officiel disponible et son évolution en %, même forme pour toutes, sans cause ni jugement ; pas d'« actualité » au cas par cas : un événement récent compte quand il entre dans les statistiques officielles ; les problèmes réels, violences, dégâts, pénuries, sont dits clairement, avec la même règle pour toutes les propositions), puis « Pour » et « Contre » = le meilleur argument réel de chaque côté, en mots simples (100 caractères environ, sans pays ni étude), la force des preuves de chacun (`solide | mitigé | faible | pas d'étude`), 0 à 3 cas réels sourcés par côté (le fait observé, puis source, lieu et année entre parenthèses), l'état des études et les sources vérifiées (format dans `pipeline/quizfx.py`). **Même méthode et même exigence pour toutes les mesures, mais pas de fausse symétrie** : on n'invente ni argument ni cas pour équilibrer, on montre où penchent les faits et on laisse le lecteur juger ; un cas n'est retenu que s'il est pertinent (même type de mesure, contexte comparable), observé, de source reconnue et non isolé : mieux vaut aucun exemple qu'un exemple faible ou obscur ; mêmes cas et mêmes niveaux de preuve pour les mesures du même type ; le « Contre » tient compte du reste du programme (si une autre mesure du même candidat répond à la critique principale, elle est signalée et le « Contre » porte sur ce qui reste) ; sans nom, coût, faisabilité ni morale. Les sources qui nomment un candidat ne sont pas affichées. Le test vérifie que chaque proposition du quiz a son Pour et son Contre.
- `template.html` : toute l'app (HTML/CSS/JS sans dépendance). Fonctionne en artifact claude.ai (`window.claude`) et en site autonome (`WEB` : fonctions `/api/report`, `/api/reports`).

## Règles de chiffrage (résumé ; détail dans `D.method` et METHODOLOGIE.md)
- Md€/an, effet sur le solde public, année pleine 2030, euros 2026 ; + améliore le solde.
- Médiane des chiffrages crédibles, sinon calcul ascendant ; pas d'effets macro de bouclage.
- Valeurs communes : retour à 62 ans = 11,8 Md€ (13,6 − 1,8 de suspension) ; Zucman = +5 ; poste public = 61,6 k€, moitié rendue aux agents, 70 % du plan en 2030 ; enseignants = 3,3 Md€ par +10 % ; AME → aide d'urgence = +0,7 ; cumulé sur 5 ans → flux 2030 = 3,5/15 ; CVAE déjà supprimée ; SMIC juin 2026 = 1 477,93 € net.
- Hors total : mesures non reconfirmées en 2026 (`a_confirmer`), paramètre clé non publié (`claude.nc`, fourchette indicative en note), doublons (`claude.exclude`).
- Verdicts : faisable / sous_conditions / tres_difficile / bloque (« Exige une révision », avec le chemin). Une mesure « bloque » est comptée « si elle passe » ; `realsum` montre le total sans elles.
- Simulateur : aucun gain pour une mesure non financée ou non confirmée ; mêmes hypothèses pour une même mesure.

## À surveiller
- LFI : programme « L'avenir en commun » le 6 novembre 2026, convention le 7.
- RN : réforme des retraites détaillée le 17 novembre 2026.
- Zemmour : programme 2026 attendu (CSG, successions aujourd'hui hors total, non reconfirmées).
- Sondages (`poll`) : Ipsos-BVA 21-22/10/2026 ; masqués automatiquement les 17-18 avril et 1er-2 mai 2027 (`D.blackout`).

## Déploiement
Cloudflare Pages, sortie `public/` + `functions/`, pas de build côté Cloudflare, pas de wrangler.toml (liaisons et secrets réglés dans le tableau de bord). Déploiement : `npx wrangler pages deploy public --project-name promesses-2027`, ou automatique via `.github/workflows/deploy.yml` une fois les secrets posés. Voir DEPLOY.md. Pas d'assistant IA (retiré le 27/10/2026). Secrets : `ADMIN_TOKEN`, `SALT` ; KV : `LIMITS`, `REPORTS`.
