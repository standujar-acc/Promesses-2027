# Faire évoluer Promesses 2027

Guide pratique pour toute modification du site, qu'elle soit faite par une personne ou par Claude. Les règles de fond (neutralité, chiffrage) sont dans [CLAUDE.md](CLAUDE.md) et [METHODOLOGIE.md](METHODOLOGIE.md) ; la revue périodique suit [.claude/skills/revue/SKILL.md](.claude/skills/revue/SKILL.md).

## 1. Le circuit d'une modification

1. Partir de `main` à jour et créer une branche : `git checkout -b sujet/court`.
2. Modifier **uniquement les sources** (`pipeline/`, `tests/`, documentation). Jamais `public/` ni le tableau du README à la main : ils sont générés.
3. Reconstruire et tester :
   ```
   python3 pipeline/run.py     # régénère public/ et le tableau du README
   python3 tests/smoke.py      # Playwright + Chromium
   ```
   Dans un conteneur Claude Code : `pip install playwright==$(node -e "console.log(require('playwright/package.json').version)")` puis lancer avec `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
4. Mettre à jour **les trois fichiers de suivi** (section 2), dans le même commit que le changement.
5. Commit, push, PR vers `main`. La CI vérifie que `public/` et le README correspondent aux sources. La fusion sur `main` redéploie le site (Cloudflare Pages).

Pour un changement de fond (chiffre, verdict, texte qui compare des candidats), faire relire la PR par une seconde personne ou une session Claude indépendante avant de fusionner.

## 2. À chaque changement : registre, historique, date

### Registre des manques et des points à trancher : `pipeline/data/suivi.json`
C'est la liste de ce qui manque, reste incertain ou attend une décision. Une routine (ou une personne) la reprend à chaque revue.

- **Ajouter un point** dès qu'on découvre un manque qu'on ne règle pas tout de suite : lien mort, source faible, mesure à reconfirmer, paramètre non publié, annonce attendue à une date, nouvelle mesure à chiffrer, ou **décision à prendre** (`a_trancher`).
- **Fermer un point** quand il est réglé : `statut: "resolu"`, `resolution` (ce qui a été fait, PR ou commit), `maj` à la date du jour. On ne supprime jamais un point : on le passe en `resolu` ou `abandonne`.
- **Mettre `derniere_revue`** à la date du jour après une revue.

Types : `lien_mort`, `source_faible`, `a_confirmer`, `non_chiffrable`, `annonce_attendue`, `a_ajouter`, `a_verifier`, `a_trancher`. Format complet : section « Format du registre » de la [skill revue](.claude/skills/revue/SKILL.md).

Règle d'or : **un changement qui demande un arbitrage** (méthode, interprétation, neutralité, changement important d'un total) **se tranche en appliquant les règles communes aux faits vérifiés** (délégation du porteur du projet, 27/10/2026). La décision, la règle appliquée et les sources sont notées dans le registre (`resolution`) et signalées dans la PR. Seul un choix sans règle applicable ni fait décisif reste un point `a_trancher`.

### Historique affiché sur le site : `D['changelog']` dans `pipeline/build.py`
- Tout changement **visible** sur le site (chiffre, texte, fonctionnalité) a une entrée.
- Une nouvelle entrée s'ajoute **après les autres lignes `D['changelog'].insert(0, …)`** : la dernière ajoutée s'affiche en haut.
- **Une seule entrée par sujet et par jour** : si le quiz change trois fois dans la journée, on complète l'entrée existante au lieu d'en empiler trois.
- Format : `{'date':'JJ/MM/AAAA','text':"Phrase courte, ce qui change pour le lecteur."}`. Pas de jargon interne, pas de nom de fichier.

### Date « Mis à jour le »
`D['asof']`, fixée dans le bloc daté de `pipeline/corrections.py` (ex. `D['asof']='27 octobre 2026'`). À changer dès que les données ou les textes changent. Elle alimente l'en-tête du site et le README.

## 3. Où modifier quoi

| Je veux… | Fichier | Règle |
|---|---|---|
| Corriger un chiffre, un verdict, une source, un texte de mesure | `pipeline/corrections.py`, **nouveau bloc daté** `# --- review N : objet (JJ/MM/AAAA)` placé avant `# --- quiz` | Jamais après `# --- totaux` (sauf les résumés, bloc `# --- résumés gabarit`). Chercher les mesures du même type chez les autres candidats et appliquer la même règle. |
| Remplacer un lien mort | `URLFIX` dans le bloc daté | Le pipeline échoue si un remplacement ne sert pas. Une copie archivée est signalée « (copie archivée) ». |
| Volet vie quotidienne | `pipeline/data/life-*.json`, `pipeline/life.py` (`OVR`, `VFLIP`) | Même lecture d'une étude pour un même type de mesure. |
| Quiz : texte d'une proposition | `pipeline/data/quiz_plain.json` (`[texte, concrètement]`) | Pas de coût, pas de faisabilité, pas de chiffre qui trahit le candidat. Sans entrée, la mesure n'est pas dans le quiz. Proposition « Vie quotidienne » (précise et reconfirmée seulement) : clé `candidat.thème.n`, valeur `[texte, concrètement, texte publié]`. |
| Quiz : « Pour » et « Contre » | `pipeline/data/quiz_effets.json` (format dans `pipeline/quizfx.py`) | Un constat (la réalité française mesurée visée par la proposition, chiffre officiel, sans cause ni jugement), puis le meilleur argument réel de chaque côté (100 caractères environ, sans pays), la force des preuves de chacun, 0 à 3 cas réels sourcés par côté. Même méthode pour toutes les mesures, sans fausse symétrie : rien d'inventé pour équilibrer, aucun exemple faible ou obscur (pertinent, observé, source reconnue, non isolé). Mêmes cas pour les mesures du même type ; aucune source qui nomme un candidat (titre, adresse ou contenu). |
| Simulateur : paramètres d'un candidat | clé `sim` du candidat, dans `pipeline/corrections.py` (blocs « simulateur ») | Aucun gain pour une mesure non chiffrée ou non confirmée ; mêmes hypothèses pour une même mesure ; les pertes comptées comme les gains. |
| Simulateur : droit actuel | `D['statu_quo']` (`SQ`) dans `pipeline/corrections.py` | Valeur et source officielle (service-public.gouv.fr, Insee…). |
| Simulateur ou quiz : calcul, affichage | `pipeline/template.html` | Ajouter un contrôle dans `tests/smoke.py` pour tout nouveau réglage ou toute nouvelle règle. |
| Texte de méthode | `D['method']` dans `pipeline/build.py` **et** `METHODOLOGIE.md` | Les deux disent la même chose. |
| Déploiement | `DEPLOY.md` | — |

## 4. Avant de pousser : liste de contrôle

- [ ] `python3 pipeline/run.py` et `python3 tests/smoke.py` passent.
- [ ] Même règle appliquée aux mesures du même type chez tous les candidats ; aucun mot de jugement ; le site d'un candidat n'est source que sur lui-même.
- [ ] Toute URL ajoutée a été ouverte et dit bien ce qu'on lui fait dire.
- [ ] Registre `suivi.json` à jour (points ouverts, résolus, à trancher).
- [ ] Entrée d'historique (une par sujet et par jour, ajoutée en dernier) et date `asof` à jour.
- [ ] Méthode (site et METHODOLOGIE.md) à jour si une règle change.
- [ ] Rien d'édité à la main dans `public/` ni dans le tableau du README.

## 5. Tests automatiques (`tests/smoke.py`)

Ils vérifient notamment : pas d'erreur JS ni de débordement à 360 px (clair et sombre) ; quiz équilibré (20 duels, 5 apparitions par candidat), sans proposition répétée, chaque proposition avec ses deux explications ; résultat du quiz (une pastille par proposition vue, chiffre et classement identiques au calcul, thème marqué compté double, égalités jamais départagées, texte copié fidèle, pas de débordement) ; thèmes choisis à l'accueil plus présents sans casser l'équilibre ; simulateur sans montant absurde ni texte invalide, chaque réglage qui change au moins un résultat, pas de saut brutal pour +100 € de salaire. Un nouveau comportement s'accompagne d'un nouveau contrôle.
