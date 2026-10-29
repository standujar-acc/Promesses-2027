# Déployer sur Cloudflare Pages

Le site est statique (`public/`), avec deux petites fonctions (`functions/api/`). Aucun build côté Cloudflare : le site est déjà construit et versionné.

## Option A : tout en ligne de commande (Claude Code peut le faire seul)

```
npx wrangler login                                   # une fois, ouvre le navigateur
npx wrangler pages project create promesses-2027 --production-branch main
npx wrangler kv namespace create promesses-limits    # noter l'id
npx wrangler kv namespace create promesses-reports   # noter l'id
npx wrangler pages deploy public --project-name promesses-2027 --branch main
```
Puis, dans le tableau de bord du projet (Paramètres → Liaisons), lier `LIMITS` et `REPORTS` aux deux espaces KV, et ajouter les secrets :
```
npx wrangler pages secret put ADMIN_TOKEN --project-name promesses-2027
npx wrangler pages secret put SALT --project-name promesses-2027
```
Déploiement automatique à chaque push : créer un jeton API Cloudflare (modèle « Cloudflare Pages : modifier »), puis
```
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
gh variable set CF_PAGES_PROJECT --body promesses-2027
```
Le workflow `.github/workflows/deploy.yml` prend alors le relais.

## Option B : depuis le tableau de bord

### 1. Créer le projet (une fois)

1. Cloudflare → **Workers & Pages** → **Créer** → onglet **Pages** → **Connecter à Git**.
2. Choisir le dépôt `promesses-2027`.
3. Réglages de build :
   - Framework : **Aucun**
   - Commande de build : *(vide)*
   - Répertoire de sortie : `public`
4. **Enregistrer et déployer.** Le site est en ligne sur `p2027.org` (domaine personnalisé ; `promesses-2027.pages.dev` reste l'adresse technique du projet Cloudflare). Chaque push sur `main` redéploie ; chaque branche a son aperçu.

### 2. Activer les signalements et les quotas (recommandé)

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
curl -H "Authorization: Bearer <ADMIN_TOKEN>" https://p2027.org/api/reports
```
Sans la liaison `REPORTS`, l'app copie le signalement dans le presse-papiers à la place.

### 3. Nom de domaine (facultatif)

Projet Pages → **Domaines personnalisés** → ajouter le domaine. Les liens de partage s'adaptent tout seuls au domaine.

## Tester en local

```
python3 pipeline/run.py
npx wrangler pages dev public --kv LIMITS --kv REPORTS --binding ADMIN_TOKEN=test
```
## Rappel légal

La loi interdit la publication de sondages la veille et le jour de chaque tour : l'app les masque automatiquement les 17-18 avril et 1er-2 mai 2027 (heure de Paris).
