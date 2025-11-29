# github - Statistiques GitHub

Récupère et affiche les statistiques d'un projet depuis l'API GitHub.

## Synopsis

```bash
projects github <nom>
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Exemples

### Usage basique

```bash
projects github mon-projet
```

Résultat :
```
ℹ Fetching GitHub repository info...
ℹ Fetching stats for username/mon-projet...

╭─────────────────────────────────────────────────╮
│ 📊 GitHub Stats for 'mon-projet'                │
├─────────────────────────────────────────────────┤
│ Repository: username/mon-projet                 │
│ Description: Mon super projet open source      │
│                                                 │
│ ⭐ Stars: 1,234                                 │
│ 🍴 Forks: 56                                    │
│ 👀 Watchers: 78                                 │
│ ⚠️ Open Issues: 12                              │
│                                                 │
│ Language: Python                                │
│ Size: 2,456 KB                                  │
│ Default Branch: main                            │
│ License: MIT License                            │
│                                                 │
│ Created: 2024-01-15                             │
│ Last Updated: 2025-11-29                        │
│ Last Pushed: 2025-11-29                         │
│                                                 │
│ URL: https://github.com/username/mon-projet     │
╰─────────────────────────────────────────────────╯
```

## Informations affichées

### Métriques principales
- **⭐ Stars** : Nombre d'étoiles
- **🍴 Forks** : Nombre de forks
- **👀 Watchers** : Nombre de watchers
- **⚠️ Open Issues** : Nombre d'issues ouvertes

### Informations techniques
- **Language** : Langage principal détecté par GitHub
- **Size** : Taille du repository en KB
- **Default Branch** : Branche par défaut (main, master, etc.)
- **License** : Type de licence (MIT, GPL, Apache, etc.)

### Dates
- **Created** : Date de création du repo
- **Last Updated** : Dernière mise à jour des métadonnées
- **Last Pushed** : Dernier push de code

### Lien
- **URL** : Lien direct vers le repository

## Fonctionnement

1. **Détection automatique** : Le CLI extrait automatiquement le nom du repo depuis la remote Git `origin`
2. **Appel API** : Fait une requête à l'API GitHub (pas besoin d'authentification pour les repos publics)
3. **Affichage** : Formate et affiche les statistiques

## Prérequis

### Le projet doit :
- ✅ Avoir un **path** configuré
- ✅ Être un **repo git** (contenir `.git`)
- ✅ Avoir une remote `origin` qui pointe vers **GitHub**
- ✅ Être un repo **public** (ou avoir configuré l'authentification)

### Le système doit :
- ✅ Avoir `curl` installé
- ✅ Avoir une connexion internet

## Formats d'URL supportés

La commande détecte automatiquement les URLs GitHub :

### HTTPS
```
https://github.com/username/repo.git
https://github.com/username/repo
```

### SSH
```
git@github.com:username/repo.git
git@github.com:username/repo
```

## Erreurs courantes

### Could not extract GitHub repository info

```
✖ Could not extract GitHub repository info from git remote.
ℹ Make sure the remote 'origin' points to a GitHub repository.
```

**Causes possibles :**
- La remote `origin` ne pointe pas vers GitHub (GitLab, Bitbucket, etc.)
- Pas de remote `origin` configurée
- Le repo n'est pas un repo git

**Solutions :**
```bash
# Vérifier la remote
cd /path/to/project
git remote -v

# Ajouter une remote GitHub
git remote add origin https://github.com/username/repo.git
```

### Failed to fetch stats

```
✖ Failed to fetch stats for username/repo.
ℹ The repository might be private or doesn't exist.
```

**Causes possibles :**
- Le repository est **privé** (nécessite authentification)
- Le repository n'existe pas sur GitHub
- Problème de connexion internet
- Rate limit API atteint

**Solutions :**
- Vérifie que le repo existe sur GitHub
- Pour les repos privés, configure un token GitHub
- Vérifie ta connexion internet

### curl not found

```
✖ Git is not installed or not in PATH.
```

**Solution :**
```bash
# Arch Linux
sudo pacman -S curl

# Ubuntu/Debian
sudo apt install curl
```

## Cas d'usage

### Vérifier la popularité

```bash
projects github awesome-lib
```

Voir combien de stars/forks ton projet a reçu.

### Comparer des projets

```bash
projects github lib-a
projects github lib-b
```

Comparer les métriques de deux projets.

### Surveiller l'activité

```bash
projects github mon-projet
```

Voir la dernière date de push et le nombre d'issues ouvertes.

### Vérifier avant contribution

Avant de contribuer à un projet open source :
```bash
projects github projet-oss
```

Voir si le projet est actif (dernière mise à jour), combien d'issues sont ouvertes, etc.

## Limitations

- ⚠️ **Repos privés** : Nécessite authentification (non implémenté actuellement)
- ⚠️ **Rate limiting** : L'API GitHub limite à 60 requêtes/heure sans authentification
- ⚠️ **GitHub uniquement** : Ne fonctionne pas avec GitLab, Bitbucket, etc.

## Voir aussi

- [info](info.md) - Informations locales du projet
- [commits](commits.md) - Historique Git local
- [stats](stats.md) - Statistiques de tous les projets

---

**[← Retour aux commandes](../../COMMANDES.md)**
