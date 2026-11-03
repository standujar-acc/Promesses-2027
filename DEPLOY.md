# Déployer sur le projet Cloudflare Pages existant

Site : https://p2027.org. Projet Pages : `promesses-2027`, adresse technique : https://promesses-2027.pages.dev.

Le site statique (`public/`) et les deux fonctions (`functions/api/`) sont publiés ensemble. Le pipeline Python construit les fichiers avant leur envoi : aucun build côté Cloudflare. Le retour du dépôt vers `standujar/Promesses-2027` conserve ce projet, ses domaines, ses liaisons KV et ses secrets. **Ne pas recréer le projet ni les espaces KV pour ce transfert.**

## Publication par GitHub Actions

Le circuit de publication est `.github/workflows/deploy.yml` → Wrangler Direct Upload → projet Pages `promesses-2027`. Ne pas ajouter d'intégration Git native Cloudflare en parallèle.

Dans les paramètres GitHub du dépôt transféré, vérifier ces noms, sans exposer leurs valeurs secrètes :

| Type | Nom | Usage |
| --- | --- | --- |
| Variable du dépôt | `CF_PAGES_PROJECT` | `promesses-2027` ; sa présence active le job de déploiement |
| Secret GitHub Actions | `CLOUDFLARE_API_TOKEN` | Publication dans le projet Pages existant |
| Secret GitHub Actions | `CLOUDFLARE_ACCOUNT_ID` | Compte Cloudflare qui contient ce projet |

Un push sur `main` déclenche la reconstruction avec Python 3.12 et vérifie que `public/`, `README.md` et `METHODOLOGIE.md` sont à jour, puis publie avec `--branch=main`. Une exécution manuelle de ce workflow publie également en production : sélectionner `main` et vérifier le SHA avant de la lancer.

Le workflow `.github/workflows/build.yml` vérifie la construction sur les pushes et les PR ; il ne publie pas. Conserver les protections de branche et les contrôles requis après le transfert.

## Liaisons et secrets conservés dans Cloudflare

Les réglages sont portés par le projet Pages, sans `wrangler.toml` dans ce dépôt :

| Type | Nom de liaison ou secret | Ressource ou rôle |
| --- | --- | --- |
| KV | `LIMITS` | Espace existant `promesses-limits`, quotas |
| KV | `REPORTS` | Espace existant `promesses-reports`, signalements |
| Secret | `ADMIN_TOKEN` | Lecture administrative des signalements |
| Secret | `SALT` | Hachage des IP pour les quotas |

Vérifier les liaisons de production et leurs identifiants dans le tableau de bord. Ne pas recréer les espaces, vider leurs données ou renouveler les secrets pour un simple changement de propriétaire GitHub. Aucun assistant IA n'est déployé.

## Transfert du dépôt et vérifications

1. Transférer le dépôt GitHub lui-même pour préserver historique, branches, PR et issues. Un push seul ne transfère pas ces métadonnées. En cas de collision de nom, conserver le dépôt existant : aucun écrasement ni suppression.
2. Vérifier le SHA de `main`, toutes les branches et les tags avant et après. Actualiser les remotes locaux et les liens du site depuis `pipeline/build.py`, puis reconstruire ; ne pas modifier les fichiers générés à la main.
3. Vérifier les variables et noms de secrets GitHub Actions, les protections, ainsi que la branche de production `main`. Ce circuit Direct Upload ne demande aucune nouvelle connexion Git du projet Pages ni nouvelle installation Cloudflare GitHub App.
4. Avant la première publication, relever le déploiement de production actuel et son SHA, présenter l'impact et le retour arrière. Si nécessaire, revenir à ce déploiement dans Cloudflare Pages ; les données KV restent indépendantes des déploiements.
5. Après publication, vérifier l'URL du déploiement, le domaine et les liaisons. Ne pas envoyer de faux signalements en production pour tester.

## Vérifier en local

Avec Python 3.12 et Playwright/Chromium installés :

```
python3.12 pipeline/run.py
git diff --exit-code -- public README.md METHODOLOGIE.md
python3.12 tests/smoke.py
```

Pour développer les fonctions avec des données locales uniquement :

```
npx wrangler pages dev public --kv LIMITS --kv REPORTS --binding ADMIN_TOKEN=test
```

Lecture administrative en production, uniquement lorsqu'elle est nécessaire et avec le secret existant :

```
curl -H "Authorization: Bearer <ADMIN_TOKEN>" https://p2027.org/api/reports
```

## Rappel légal

La loi interdit la publication de sondages la veille et le jour de chaque tour : l'app les masque automatiquement les 17-18 avril et 1er-2 mai 2027 (heure de Paris).
