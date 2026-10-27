# Déployer sur Cloudflare Pages

Le site est statique (`public/`), avec trois petites fonctions (`functions/api/`). Aucun build côté Cloudflare : le site est déjà construit et versionné.

## 1. Créer le projet (une fois)

1. Cloudflare → **Workers & Pages** → **Créer** → onglet **Pages** → **Connecter à Git**.
2. Choisir le dépôt `promesses-2027`.
3. Réglages de build :
   - Framework : **Aucun**
   - Commande de build : *(vide)*
   - Répertoire de sortie : `public`
4. **Enregistrer et déployer.** Le site est en ligne sur `promesses-2027.pages.dev`. Chaque push sur `main` redéploie ; chaque branche a son aperçu.

## 2. Activer les signalements et les quotas (recommandé)

1. **Workers & Pages → KV** → créer deux espaces : `promesses-limits` et `promesses-reports`.
2. Projet Pages → **Paramètres → Liaisons** → ajouter :
   - KV `LIMITS` → `promesses-limits`
   - KV `REPORTS` → `promesses-reports`
3. **Paramètres → Variables et secrets** → ajouter :
   - `ADMIN_TOKEN` (secret) : une longue chaîne aléatoire, pour lire les signalements.
   - `SALT` (secret) : une autre chaîne aléatoire (hachage des IP pour les quotas, jamais stockées en clair).
4. Redéployer (onglet Déploiements → Réessayer).

Lire les signalements :
```
curl -H "Authorization: Bearer <ADMIN_TOKEN>" https://promesses-2027.pages.dev/api/reports
```
Sans la liaison `REPORTS`, l'app copie le signalement dans le presse-papiers à la place.

## 3. Activer l'assistant (facultatif, payant à l'usage)

1. Créer une clé sur console.anthropic.com, avec une **limite de dépense mensuelle** sur le compte.
2. Ajouter le secret `ANTHROPIC_API_KEY`.
3. Réglages facultatifs (variables) :
   - `ASK_MODEL` : modèle utilisé (défaut `claude-haiku-5-5`).
   - `ASK_PER_DAY` : questions par visiteur et par jour (défaut 15).
   - `ASK_GLOBAL_PER_DAY` : plafond global par jour (défaut 1500).
4. Redéployer. Sans clé, l'onglet « Demander » affiche simplement que l'assistant n'est pas disponible.

Le contexte (toutes les mesures) est mis en cache côté API : chaque question coûte surtout les tokens de la réponse.

## 4. Nom de domaine (facultatif)

Projet Pages → **Domaines personnalisés** → ajouter le domaine. Les liens de partage s'adaptent tout seuls au domaine.

## Tester en local

```
python3 pipeline/run.py
npx wrangler pages dev public --kv LIMITS --kv REPORTS --binding ADMIN_TOKEN=test
```
Pour l'assistant en local, mettre `ANTHROPIC_API_KEY=...` dans un fichier `.dev.vars` (ignoré par git).

## Rappel légal

La loi interdit la publication de sondages la veille et le jour de chaque tour : l'app les masque automatiquement les 17-18 avril et 1er-2 mai 2027 (heure de Paris).
