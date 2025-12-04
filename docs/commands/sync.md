# Commande `sync`

## Description

Synchroniser les projets avec GitHub/GitLab pour récupérer les métriques (stars, forks, issues, PRs) et le statut CI/CD.

## Sous-commandes

- `sync enable` - Activer la synchronisation pour un projet
- `sync disable` - Désactiver la synchronisation
- `sync status` - Voir le statut de synchronisation
- `sync run` - Exécuter la synchronisation
- `sync queue` - Gérer la file d'attente
- `sync rate-limit` - Afficher les limites API

---

## `sync enable`

Activer la synchronisation pour un projet (détection automatique du repo).

### Usage

```bash
projects sync enable [PROJECT] [OPTIONS]
```

### Options

- `--platform TEXT` - Plateforme (github/gitlab)
- `--owner TEXT` - Propriétaire du repo
- `--repo TEXT` - Nom du repo

### Exemples

```bash
# Auto-détection depuis le dossier courant
cd ~/Work/monprojet && projects sync enable

# Spécifier le nom du projet (auto-détection du remote)
projects sync enable monprojet

# Spécification manuelle
projects sync enable monprojet --platform github --owner user --repo repo
```

---

## `sync disable`

Désactiver la synchronisation pour un projet.

### Usage

```bash
projects sync disable PROJECT [OPTIONS]
```

### Options

- `--delete-cache` - Supprimer aussi les données en cache

### Exemples

```bash
# Désactiver mais garder le cache
projects sync disable monprojet

# Désactiver et supprimer toutes les données
projects sync disable monprojet --delete-cache
```

---

## `sync status`

Afficher le statut de synchronisation.

### Usage

```bash
projects sync status [PROJECT] [OPTIONS]
```

### Options

- `--all, -a` - Afficher tous les projets
- `--verbose, -v` - Afficher les détails

### Exemples

```bash
# Statut d'un projet
projects sync status monprojet

# Statut détaillé avec métriques
projects sync status monprojet --verbose

# Tous les projets
projects sync status --all
```

### Exemple de sortie

```
╭─────────────────── Sync Status ────────────────────╮
│ Project      Platform  Repository        Last S… │
│ monprojet    Github    user/monprojet    2h ago  │
│ autreprojet  Github    user/autre        Never   │
╰────────────────────────────────────────────────────╯
```

---

## `sync run`

Exécuter la synchronisation pour récupérer les données de GitHub.

### Usage

```bash
projects sync run [PROJECT] [OPTIONS]
```

### Options

- `--all, -a` - Synchroniser tous les projets activés
- `--force, -f` - Forcer la synchro (ignorer le cache 24h)
- `--update-metadata` - Mettre à jour description/language/tags
- `--priority, -p INTEGER` - Priorité dans la file (1=max, 10=min)

### Exemples

```bash
# Synchroniser un projet
projects sync run monprojet

# Forcer le rafraîchissement (ignorer le cache)
projects sync run monprojet --force

# Mettre à jour les métadonnées du projet
projects sync run monprojet --update-metadata

# Synchroniser tous les projets activés
projects sync run --all
```

### Exemple de sortie

```bash
ℹ Syncing monprojet...
ℹ Fetching repository metadata for user/monprojet...
ℹ Fetching pull request count...
ℹ Saving metrics to cache...
ℹ Fetching CI/CD workflow status...
✔ Synced monprojet in 2.3s
  ⭐ Stars: 42
  🍴 Forks: 7
  ⚠️  Open Issues: 3
  🔀 Pull Requests: 2
  🔧 CI/CD: ✓ success
```

---

## `sync queue`

Gérer la file d'attente de synchronisation.

### Usage

```bash
projects sync queue [OPTIONS]
```

### Options

- `--clear-completed` - Supprimer les éléments terminés
- `--retry-failed` - Relancer les échecs

### Exemples

```bash
# Voir le statut de la file
projects sync queue

# Nettoyer les anciens éléments
projects sync queue --clear-completed
```

### Exemple de sortie

```
Sync Queue Status
  Pending: 3
  Processing: 1
  Completed: 15
  Failed: 0
```

---

## `sync rate-limit`

Afficher les limites de l'API GitHub/GitLab.

### Usage

```bash
projects sync rate-limit [PLATFORM]
```

### Arguments

- `PLATFORM` - Plateforme (github/gitlab, défaut: github)

### Exemples

```bash
# Limites GitHub
projects sync rate-limit github

# Limites GitLab
projects sync rate-limit gitlab
```

### Exemple de sortie

```
Github API Rate Limit
  Remaining: 4850/5000
  Used: 150
  Resets at: 2025-12-04 12:30:45
  Status: Good (97% remaining)
```

---

## Données récupérées

### Métriques de base
- ⭐ **Stars** - Nombre d'étoiles
- 🍴 **Forks** - Nombre de forks
- 👀 **Watchers** - Nombre de watchers
- ⚠️ **Issues** - Issues ouvertes
- 🔀 **Pull Requests** - PRs ouvertes

### Métadonnées
- 💻 **Language** - Langage principal
- 📜 **License** - Type de licence
- 🏷️ **Topics** - Tags GitHub
- 📝 **Description** - Description du repo

### CI/CD
- 🔧 **Workflow Status** - Statut du dernier workflow
- ✓ Success / ❌ Failure / ⏳ Pending

---

## Système de cache

- **TTL par défaut**: 24 heures
- **Forcer rafraîchissement**: `--force`
- **Localisation**: SQLite `~/.config/project-cli/projects.db`

### Tables utilisées
- `remote_repos` - Configuration de sync
- `remote_metrics_cache` - Métriques en cache
- `pipeline_status` - Statuts CI/CD
- `sync_queue` - File d'attente

---

## Rate limiting

Le système respecte les limites API:

### GitHub
- **Limite**: 5000 requêtes/heure
- **Stratégie**: File d'attente avec batch processing
- **Cache**: 24h pour éviter les appels inutiles

### GitLab
- **Limite**: 300 requêtes/minute (à venir)

---

## Workflow complet

```bash
# 1. Configurer le token
projects auth github --token ghp_xxxxxxxxxxxxx

# 2. Activer sync pour un projet
projects sync enable monprojet

# 3. Première synchro
projects sync run monprojet

# 4. Voir les résultats
projects sync status monprojet --verbose
projects info monprojet  # Affiche aussi les métriques GitHub

# 5. Sync régulière (automatique avec cache)
projects sync run monprojet  # Utilise le cache si < 24h

# 6. Forcer rafraîchissement
projects sync run monprojet --force
```

---

## Intégration avec `info`

La commande `info` affiche automatiquement les métriques GitHub si disponibles:

```bash
projects info monprojet
```

Sortie:
```
╭──────────────── ⚡ monprojet ───────────────╮
│ Status: active                              │
│ ...                                         │
╰─────────────────────────────────────────────╯

╭───────────── 📊 Remote Repository ──────────────╮
│ Platform: Github                                │
│ Repository: user/monprojet                      │
│                                                 │
│ ⭐ Stars: 42  🍴 Forks: 7                       │
│ 👀 Watchers: 15  ⚠️  Issues: 3                  │
│ 🔀 Pull Requests: 2                             │
│ 💻 Language: Python                             │
│ 🔧 CI/CD: ✓ success                            │
│                                                 │
│ Last synced: 2h ago                             │
╰─────────────────────────────────────────────────╯
```

---

## Dépannage

### Repo non trouvé
```
✖ Repository not found or inaccessible
```
**Solutions**:
- Vérifie que le token a les permissions `repo`
- Vérifie owner/repo dans `projects sync status monprojet`
- Pour repo privé, assure-toi que le token a accès

### Rate limit dépassé
```
✖ Rate limit exceeded
```
**Solutions**:
- Attendre la réinitialisation: `projects sync rate-limit github`
- Utiliser le cache: retirer `--force`

### Token invalide
```
✖ No github token found
```
**Solutions**:
- Stocker le token: `projects auth github --token XXX`
- Tester: `projects auth github --test`

---

## Commandes liées

- `projects auth` - Gérer les tokens
- `projects info` - Voir détails + métriques GitHub
- `projects list` - Peut afficher sync status (futur)

---

**[← Retour aux commandes](../../COMMANDES.md)**
