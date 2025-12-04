# 📚 Liste des commandes

Ce document recense toutes les commandes disponibles dans le CLI `projects`.

## 📖 Navigation

Chaque commande possède sa propre documentation détaillée avec des exemples d'utilisation.

---

## 🖥️ Interface

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **dashboard** | 🔥 **TUI Dashboard** - Interface complète en plein écran | - |

## 🔧 Gestion de base

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **add** | Ajouter un nouveau projet | [→ Voir la doc](docs/commands/add.md) |
| **list** | Lister tous les projets (avec statut git!) | [→ Voir la doc](docs/commands/list.md) |
| **info** | Afficher les détails d'un projet | [→ Voir la doc](docs/commands/info.md) |
| **edit** | Modifier les informations d'un projet | [→ Voir la doc](docs/commands/edit.md) |
| **rm** | Supprimer un projet | [→ Voir la doc](docs/commands/rm.md) |
| **status** | Changer le statut d'un projet | [→ Voir la doc](docs/commands/status.md) |

## 🏷️ Organisation

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **tag** | Gérer les tags d'un projet | [→ Voir la doc](docs/commands/tag.md) |
| **stats** | Afficher les statistiques | [→ Voir la doc](docs/commands/stats.md) |
| **stale** | Trouver les projets inactifs | [→ Voir la doc](docs/commands/stale.md) |

## 🔍 Import et découverte

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **scan** | Scanner un dossier pour importer des repos git | [→ Voir la doc](docs/commands/scan.md) |

## 📊 Visualisation

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **tree** | Afficher l'arborescence des fichiers | [→ Voir la doc](docs/commands/tree.md) |
| **commits** | Afficher l'historique Git (tableau) | [→ Voir la doc](docs/commands/commits.md) |
| **git-tree** | Afficher l'historique Git (graphe) | [→ Voir la doc](docs/commands/git-tree.md) |

## 📝 Activité et suivi

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **log** | Journaliser et voir l'activité | [→ Voir la doc](docs/commands/log.md) |

## 🌐 Intégrations

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **github** | Stats GitHub + comparaison local/remote | [→ Voir la doc](docs/commands/github.md) |
| **auth** | 🆕 Gérer les tokens GitHub/GitLab | [→ Voir la doc](docs/commands/auth.md) |
| **sync** | 🆕 Synchroniser avec GitHub (stars, forks, issues, CI/CD) | [→ Voir la doc](docs/commands/sync.md) |

## ⚙️ Configuration & Outils

| Commande | Description | Documentation |
|----------|-------------|---------------|
| **open** | Ouvrir un projet dans votre IDE | - |
| **config** | Gérer la configuration (IDE, etc.) | - |
| **refresh** | Actualiser le statut git de tous les projets | - |

---

## 🚀 Aide rapide

Pour obtenir de l'aide sur une commande spécifique :

```bash
projects <commande> --help
```

Exemple :
```bash
projects add --help
projects list --help
```

---

**[← Retour au README](README.md)** | **[Architecture →](ARCHITECTURE.md)** | **[Contribuer →](CONTRIBUTING.md)**
