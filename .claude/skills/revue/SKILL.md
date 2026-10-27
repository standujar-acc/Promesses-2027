---
name: revue
description: Passage de revue de Promesses 2027 — traite le registre de suivi (pipeline/data/suivi.json), fait la veille des 8 candidats, corrige ou complète les données avec la même règle pour tous, puis ouvre une PR. À utiliser pour « lance la revue », une routine programmée, ou après une annonce de campagne.
---

# Revue Promesses 2027

Un passage de revue fait avancer le registre `pipeline/data/suivi.json` et met les données à jour. Il ne publie jamais directement : il se termine par une **PR** que le porteur du projet relit et fusionne (la fusion sur `main` redéploie le site).

Lire d'abord `CLAUDE.md` (règles de neutralité et de chiffrage) et `METHODOLOGIE.md`.

## Règles non négociables
- **Même traitement pour les 8 candidats**, dans l'ordre de `ORD` (`pipeline/corrections.py`). Même effort de recherche pour chacun. Avant de changer une mesure, chercher les mesures du même type chez les autres et appliquer la même règle.
- Le site de campagne d'un candidat n'est une source que sur ses propres propositions. Agrégateurs et sites non officiels : signalés (`weak_domains`, mention « agrégateur » ou « non officiel » dans le libellé).
- Pas d'adjectif de jugement, pas de formulation sévère réservée à un camp.
- Ne jamais inventer un chiffre ou une URL : toute URL ajoutée est ouverte et vérifiée. Si une source manque, le point reste ouvert.
- Un changement de **verdict**, de **total** ou de **règle commune** se fait seulement avec une source vérifiée. S'il demande un arbitrage (méthode, neutralité, interprétation), ne pas trancher : créer un point `a_trancher` et le signaler dans la PR.

## Déroulé
1. **Préparer.** `git pull` sur `main`, puis créer la branche `revue/AAAA-MM-JJ`. Lancer `python3 pipeline/run.py` puis `python3 tests/smoke.py` : tout doit passer avant de commencer.
   Dans un conteneur Claude Code où Playwright Python manque : `pip install playwright==$(node -e "console.log(require('playwright/package.json').version)")`, puis lancer avec `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
2. **Lire le registre.** Dans `pipeline/data/suivi.json`, traiter d'abord les points dont l'`echeance` est passée ou proche, puis les autres points `ouvert`.
3. **Contrôles.** Sur `pipeline/promesses-2027-data.json` (généré par le pipeline) :
   - liens morts (404/410 ; un 403 ou une connexion coupée est souvent une protection anti-robots, à revérifier dans un navigateur avant de conclure) ;
   - mesures dont toutes les sources sont faibles ;
   - site de campagne cité chez un autre candidat (domaines : rassemblementnational.fr ; melenchon2027.fr, lafranceinsoumise.fr ; place-publique.eu, raphaelglucksmann.kessel.media ; edouardphilippe.fr, horizonsleparti.fr ; republicains.fr ; attalpresident.fr, parti-renaissance.fr ; unenouvelleenergie.fr, lisnard.cards ; parti-reconquete.fr — compléter si besoin) ;
   - mesures `a_confirmer` et non chiffrables faute de paramètre (`claude.nc`) ;
   - totaux recalculés à partir des mesures comptées ;
   - quiz (`data/quiz_plain.json`, `data/quiz_effets.json`) : pas de coût, pas de verdict, pas de chiffre qui trahit le candidat ; deux effets factuels, sans morale, propres à chaque mesure (pas de formule passe-partout) ; toute mesure ajoutée au quiz reçoit ses deux effets.
   Chaque problème nouveau devient un point du registre.
   Une annonce nouvelle qui demande un chiffrage devient un point `a_ajouter` (pour chaque candidat, même s'il n'y a « rien de nouveau ») ; elle n'entre dans les données qu'avec le même niveau de chiffrage pour tous.
4. **Veille.** Pour chaque candidat, chercher depuis `derniere_revue` : nouvelles mesures, chiffres modifiés, mesures abandonnées, documents de programme, nouveaux chiffrages indépendants (Institut Montaigne, iFRAP, IPP, OFCE, Fipeco, Cour des comptes, CAE…). Noter aussi tout nouveau sondage national (ne mettre à jour `poll` qu'avec un institut et une date).
5. **Corriger ou compléter.**
   - Mesures, chiffrages, verdicts, sources : un **nouveau bloc daté** dans `pipeline/corrections.py`, `# --- review N : objet (JJ/MM/AAAA)`, placé avant `# --- quiz` (le texte du quiz est appliqué après toutes les corrections, pour que les mesures ajoutées y entrent). Ne rien écrire après `# --- totaux`, sauf dans le bloc `# --- résumés gabarit` pour mettre à jour un résumé.
   - Un remplacement de lien passe par `URLFIX` dans le bloc daté, avec le contrôle qui fait échouer le pipeline si un remplacement ne sert pas ; un remplacement de texte est précédé d'un `assert` sur le texte attendu.
   - Vie quotidienne : `pipeline/data/life-*.json` et `pipeline/life.py` (`OVR`, `VFLIP`).
   - Quiz : `pipeline/data/quiz_plain.json` et `pipeline/data/quiz_effets.json`.
   - Texte de méthode : `D.method` dans `pipeline/build.py` et `METHODOLOGIE.md`.
   - Tout changement visible sur le site : une entrée datée dans `D.changelog` (`pipeline/build.py`), **ajoutée après les autres** (la dernière ajoutée s'affiche en haut) ; une seule entrée par sujet et par jour, à compléter plutôt qu'à empiler.
   - Date « Mis à jour le » : `D['asof']` dans le bloc daté de `corrections.py`.
   - Jamais d'édition à la main de `public/`.
6. **Mettre à jour le registre.** Passer en `resolu` les points réglés (avec `resolution` et `maj`), ajouter les nouveaux points (identifiant suivant), mettre `derniere_revue` à la date du jour.
7. **Vérifier.** `python3 pipeline/run.py` puis `python3 tests/smoke.py` : tout passe. Relire le diff en cherchant toute asymétrie entre candidats.
8. **PR.** Commit, push de la branche, PR vers `main` intitulée « Revue du JJ/MM/AAAA ». Corps de la PR : ce qui a changé, candidat par candidat, toujours dans le même ordre ; les sources ajoutées ; les points `a_trancher` ; les points encore ouverts avec leur échéance. Ne jamais fusionner soi-même.

Si rien n'a changé, la PR ne contient que la mise à jour de `derniere_revue` et des points vérifiés.

## Format du registre (`pipeline/data/suivi.json`)
```json
{
  "derniere_revue": "AAAA-MM-JJ",
  "points": [
    {
      "id": "S001",
      "type": "lien_mort | source_faible | a_confirmer | non_chiffrable | annonce_attendue | a_ajouter | a_verifier | a_trancher",
      "candidats": ["le-pen"],
      "mesure": "enr ou [\"enr\", \"energie\"]",
      "sujet": "Une phrase : ce qui manque ou reste incertain",
      "detail": "Ce qu'on sait, ce qu'il faut trouver, où chercher",
      "echeance": "AAAA-MM-JJ ou null",
      "statut": "ouvert | resolu | abandonne",
      "cree": "AAAA-MM-JJ",
      "maj": "AAAA-MM-JJ",
      "resolution": "Ce qui a été fait (commit/PR), ou null"
    }
  ]
}
```
- `candidats` : liste vide pour un point général ; tous les candidats concernés pour une règle commune.
- `mesure` : l'`id` de la mesure (ou une liste d'`id` quand le point vise plusieurs candidats), `life:<thème>` pour la vie quotidienne, ou `null`.
- On ne supprime pas un point : on le passe en `resolu` ou `abandonne`, pour garder l'historique.
