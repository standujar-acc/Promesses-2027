# Promesses 2027

Les programmes des candidats à la présidentielle française de 2027 (1er tour le 18 avril 2027), chiffrés mesure par mesure avec une méthode unique, confrontés aux estimations indépendantes publiées et aux obstacles juridiques. Simulateur personnel, quiz à l'aveugle, faisabilité, et un volet « vie quotidienne » (sécurité, santé, école, environnement, logement, libertés, économie, rayonnement).

Données à jour au 26 octobre 2026 : 8 candidats, 76 mesures.

| Candidat | Parti | Mesures chiffrées | Effet sur le déficit en 2030 (Md€/an) | Fourchette à 80 % |
| --- | --- | --- | --- | --- |
| Marine Le Pen | RN | 10 | −31,7 | −50,3 à −11,2 |
| Jean-Luc Mélenchon | LFI | 7 | −77,6 | −108,0 à −46,0 |
| Raphaël Glucksmann | PS-Place publique | 5 | −36,5 | −44,4 à −30,2 |
| Édouard Philippe | Horizons | 9 | −9,2 | −43,2 à −2,0 |
| Bruno Retailleau | LR | 9 | +13,5 | +4,2 à +23,7 |
| Gabriel Attal | Renaissance | 4 | +4,0 | +0,7 à +6,3 |
| David Lisnard | Nouvelle Énergie | 6 | −16,0 | −59,9 à −11,4 |
| Éric Zemmour | Reconquête | 4 | +21,5 | +13,8 à +27,0 |

Un montant négatif creuse le déficit. Ces totaux supposent que toutes les mesures passent, y compris celles qui exigent une révision de la Constitution ou des traités. Les mesures non reconfirmées en 2026 et celles dont un paramètre clé n'est pas publié sont hors total.

## Structure

```
public/            le site, tel qu'il est servi (index.html autonome + data/promesses-2027.json)
functions/api/     fonctions Cloudflare Pages : ask (assistant), report (signalements), reports (lecture admin)
lib/               code partagé des fonctions ; lib/context.js est généré
pipeline/          la source de vérité
  base.json        base fusionnée des programmes (avant corrections)
  corrections.py   règles communes, corrections datées, totaux (simulation à 20 000 tirages), résumés
  life.py          volet « vie quotidienne » : fusion, test « précis / intention », lecture commune des études
  build.py         méthode, historique, injection des données dans le gabarit
  template.html    l'app (HTML, CSS, JS sans dépendance)
  data/            fichiers de travail par candidat, vie quotidienne, quiz, repères officiels
  run.py           lance tout et écrit public/ et lib/context.js
tests/smoke.py     test de bout en bout (Playwright)
```

## Construire

```
python3 pipeline/run.py        # reconstruit public/ et lib/context.js
python3 tests/smoke.py         # vérifie l'app (Playwright + Chromium)
```

Rien n'est à modifier à la main dans `public/` ni dans `lib/context.js` : on modifie `pipeline/`, puis on relance `run.py`. La CI GitHub vérifie que le site versionné correspond aux sources.

## Déployer

Voir [DEPLOY.md](DEPLOY.md) (Cloudflare Pages, déploiement automatique à chaque push).

## Méthode

Voir [METHODOLOGIE.md](METHODOLOGIE.md) et l'onglet « Méthode » de l'app.

## Contester un chiffre

Voir [CONTRIBUER.md](CONTRIBUER.md), ou le bouton « Signaler une erreur » sur chaque fiche. Toute correction acceptée est datée dans l'historique de l'app.

## Licences

Code : MIT. Données : CC BY 4.0 (citer « Promesses 2027 »). Les sources citées restent la propriété de leurs auteurs.
