# Project CLI

Un CLI Python pour gérer ta montagne de projets inachevés.

## Motivation

Tu as des dizaines de projets en cours, abandonnés, ou pausés ? Tu ne sais plus où tu en es ? Ce CLI est fait pour toi !

## Features

- Ajouter et gérer des projets avec statut (active, paused, completed, abandoned)
- Tags et priorités
- Détection automatique du langage
- Scan automatique de dossiers pour importer tous tes repos git
- Intégration Git pour tracker la dernière activité
- Affichage coloré et joli avec Rich
- Statistiques sur tes projets
- Commande `stale` pour trouver les projets abandonnés

## Installation

### Dépendances

Sur Arch Linux :
```bash
sudo pacman -S python-pip python-typer python-rich
```

Ou avec pip :
```bash
pip install typer[all] rich --user
```

### Utilisation

```bash
cd project-cli
python3 -m projects.cli --help
```

## Commandes

### Add - Ajouter un projet

```bash
# Simple
python3 -m projects.cli add "my-awesome-project"

# Avec toutes les options
python3 -m projects.cli add "my-cli" \
  --desc "A cool CLI tool" \
  --path ~/Work/my-cli \
  --priority high \
  --tags "cli,python"
```

### List - Lister les projets

```bash
# Tous les projets
python3 -m projects.cli list

# Filtrer par statut
python3 -m projects.cli list --status active
python3 -m projects.cli list --status abandoned

# Filtrer par tag
python3 -m projects.cli list --tag web
```

### Info - Détails d'un projet

```bash
python3 -m projects.cli info "my-project"
```

### Status - Changer le statut

```bash
python3 -m projects.cli status "my-project" completed
python3 -m projects.cli status "old-project" abandoned
python3 -m projects.cli status "on-hold" paused
```

### Tag - Gérer les tags

```bash
# Voir les tags actuels
python3 -m projects.cli tag "my-project"

# Ajouter des tags
python3 -m projects.cli tag "my-project" --add "web,frontend"

# Supprimer des tags
python3 -m projects.cli tag "my-project" --remove "old-tag"
```

### Stats - Statistiques

```bash
python3 -m projects.cli stats
```

Affiche :
- Nombre total de projets
- Répartition par statut
- Répartition par priorité
- Projet le plus vieux sans activité

### Scan - Import automatique

```bash
# Scanner ton dossier de travail
python3 -m projects.cli scan ~/Work

# Dry-run pour voir ce qui serait importé
python3 -m projects.cli scan ~/Work --dry-run

# Limiter la profondeur
python3 -m projects.cli scan ~/Work --depth 2
```

### Stale - Projets abandonnés

```bash
# Projets sans activité depuis 30 jours (défaut)
python3 -m projects.cli stale

# Personnaliser le nombre de jours
python3 -m projects.cli stale --days 60
```

### Rm - Supprimer un projet

```bash
python3 -m projects.cli rm "old-project"
```

## Structure du projet

```
project-cli/
├── projects/
│   ├── __init__.py
│   ├── cli.py          # Commandes CLI
│   ├── database.py     # Couche base de données
│   ├── models.py       # Modèles de données
│   └── display.py      # Affichage avec Rich
├── pyproject.toml      # Configuration
└── README.md
```

## Base de données

Les données sont stockées dans `~/.config/project-cli/projects.db` (SQLite).

Tables :
- `projects` : Informations sur les projets
- `tags` : Tags associés aux projets

## Exemples d'utilisation

### Workflow typique

```bash
# 1. Scanner tous tes projets
python3 -m projects.cli scan ~/Work

# 2. Voir ce que tu as
python3 -m projects.cli list

# 3. Trouver les projets abandonnés
python3 -m projects.cli stale --days 90

# 4. Marquer certains comme abandonnés
python3 -m projects.cli status "really-old-project" abandoned

# 5. Voir les stats
python3 -m projects.cli stats

# 6. Se concentrer sur les projets actifs high priority
python3 -m projects.cli list --status active
```

### Organiser avec des tags

```bash
# Ajouter des tags pour organiser
python3 -m projects.cli tag "web-app" --add "web,typescript,react"
python3 -m projects.cli tag "ml-experiment" --add "python,ml,research"
python3 -m projects.cli tag "game-project" --add "rust,gamedev"

# Filtrer par tag
python3 -m projects.cli list --tag web
python3 -m projects.cli list --tag rust
```

## Personnalisation

### Statuts disponibles
- `active` : En cours de développement
- `paused` : Mis en pause temporairement
- `completed` : Terminé
- `abandoned` : Abandonné

### Priorités disponibles
- `high` : ⚡ Haute priorité
- `medium` : ● Priorité moyenne
- `low` : ○ Basse priorité

## Détection automatique

### Langage
Le CLI détecte automatiquement le langage principal en comptant les extensions de fichiers :
- Python, JavaScript, TypeScript, Rust, Go, Java, C, C++, etc.

### Dernière activité Git
Pour les repos git, la date du dernier commit est automatiquement récupérée.

## TODO / Améliorations futures

- [ ] Commande `edit` pour modifier un projet
- [ ] Export en JSON/Markdown
- [ ] TUI interactive avec `textual`
- [ ] Sync avec GitHub
- [ ] Templates de projets
- [ ] Notifications pour projets stale

## Licence

MIT

## Auteur

Valentin "Vraith" GILLOT
