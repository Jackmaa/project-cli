# Architecture du projet

## Vue d'ensemble

Ce CLI utilise une **architecture modulaire** où chaque commande est définie dans son propre fichier. Les commandes sont chargées **dynamiquement** au démarrage.

## Structure du projet

```
project-cli/
├── projects/
│   ├── __init__.py
│   ├── cli.py              # Point d'entrée principal (simplifié)
│   ├── database.py         # Couche base de données
│   ├── models.py           # Modèles de données
│   ├── display.py          # Affichage avec Rich
│   └── commands/           # Dossier des commandes (architecture modulaire)
│       ├── __init__.py     # Système de chargement dynamique
│       ├── add.py
│       ├── list.py
│       ├── info.py
│       ├── rm.py
│       ├── status.py
│       ├── stats.py
│       ├── tag.py
│       ├── edit.py
│       ├── scan.py
│       ├── stale.py
│       ├── commits.py
│       ├── log.py
│       ├── tree.py
│       ├── github.py
│       ├── auth.py         # Authentification GitHub/GitLab
│       ├── sync.py         # Synchronisation remote
│       └── track.py        # 🆕 Suivi du temps !
├── pyproject.toml
└── README.md
```

## Comment ça fonctionne ?

### 1. Chargement dynamique des commandes

Le fichier `projects/commands/__init__.py` contient la fonction `load_commands()` qui :

1. **Scanne** le dossier `commands/`
2. **Importe** chaque module Python (fichier `.py`)
3. **Appelle** la fonction `register_command(app)` de chaque module

```python
def load_commands(app: typer.Typer):
    """Charge dynamiquement toutes les commandes depuis ce package."""
    commands_dir = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(commands_dir)]):
        module_name = module_info.name

        if module_name.startswith('_'):
            continue

        full_module_name = f"projects.commands.{module_name}"
        module = importlib.import_module(full_module_name)

        if hasattr(module, 'register_command'):
            module.register_command(app)
```

### 2. Structure d'une commande

Chaque fichier de commande doit suivre ce pattern :

```python
"""Description de la commande."""

import typer
from .. import database as db
from .. import display

def register_command(app: typer.Typer):
    """Register the 'nom_commande' command with the Typer app."""

    @app.command()
    def nom_commande(
        arg1: str = typer.Argument(..., help="Description"),
        option1: str = typer.Option(None, "--opt", help="Description"),
    ):
        """Description de ce que fait la commande."""
        # Implémentation ici
        pass
```

### 3. Le point d'entrée (`cli.py`)

Le fichier `cli.py` est maintenant **très simple** :

```python
import typer

# Créer l'app Typer
app = typer.Typer(
    name="projects",
    help="Manage your mountain of unfinished projects",
)

# Charger dynamiquement toutes les commandes
from .commands import load_commands
load_commands(app)

if __name__ == "__main__":
    app()
```

## Avantages de cette architecture

### Modularité
Chaque commande est isolée dans son propre fichier. Facile à maintenir et à comprendre.

### Extensibilité
Pour ajouter une nouvelle commande, il suffit de :
1. Créer un nouveau fichier dans `commands/`
2. Implémenter la fonction `register_command(app)`
3. C'est tout ! La commande sera automatiquement chargée

### Organisation
Le code est bien organisé. Plus besoin d'un fichier `cli.py` de 400 lignes !

### Réutilisabilité
Les fonctions utilitaires (comme `detect_language`, `get_last_git_activity`) peuvent être partagées entre commandes.

## Nouvelles commandes

### commits - Historique git

Affiche l'historique des commits d'un projet.

```bash
projects commits project-cli -n 5
projects commits project-cli --author "Valentin"
```

### log - Journalisation d'activité

Track l'activité sur tes projets.

```bash
# Ajouter une entrée
projects log project-cli --add "Fixed authentication bug"

# Voir les logs d'un projet
projects log project-cli

# Voir tous les logs
projects log
```

### tree - Arborescence

Visualise la structure d'un projet dans le terminal.

```bash
# Afficher tout
projects tree project-cli

# Limiter la profondeur
projects tree project-cli --depth 2

# Afficher les fichiers cachés
projects tree project-cli --all
```

### github - Stats GitHub

Récupère les statistiques d'un repo GitHub via l'API.

```bash
projects github project-cli
```

Affiche :
- Nombre de stars, forks, watchers
- Issues ouvertes
- Langage principal
- Taille du repo
- Dates de création/mise à jour
- Licence

## Base de données

La base de données SQLite contient maintenant 3 tables :

### projects
Informations sur les projets (nom, path, status, priority, etc.)

### tags
Tags associés aux projets

### activity_logs (NOUVEAU)
Journalisation de l'activité sur chaque projet

```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

## Concepts Python utilisés

Pour les débutants, voici les concepts Python utilisés dans cette architecture :

### 1. Import dynamique (`importlib`)

Au lieu de faire :
```python
from .commands.add import register_command as add_cmd
from .commands.list import register_command as list_cmd
# etc...
```

On fait :
```python
module = importlib.import_module(f"projects.commands.{module_name}")
```

Cela permet de charger des modules dont on ne connaît pas le nom à l'avance.

### 2. Introspection (`hasattr`)

`hasattr(module, 'register_command')` vérifie si le module a un attribut (fonction, variable, etc.) nommé `register_command`.

### 3. Package et `__path__`

En Python, un dossier avec un fichier `__init__.py` est un **package**.
La variable `__path__` contient le chemin du package.

### 4. Modules et imports relatifs

Les imports avec `..` permettent d'importer depuis le package parent :
```python
from .. import database as db  # Import depuis projects/
from . import display          # Import depuis projects/
```

### 5. Décorateurs

`@app.command()` est un décorateur qui transforme une fonction en commande CLI.

### 6. Type hints et Enum

```python
status: Status = typer.Option(...)
```

`Status` est un Enum qui limite les valeurs possibles.

## Comment ajouter une nouvelle commande ?

Exemple : Ajouter une commande `backup` qui sauvegarde la base de données.

1. **Créer** `projects/commands/backup.py` :

```python
"""Backup command - Backup the project database."""

import typer
import shutil
from datetime import datetime
from pathlib import Path

from .. import database as db
from .. import display

def register_command(app: typer.Typer):
    """Register the 'backup' command with the Typer app."""

    @app.command()
    def backup(
        output: str = typer.Option(".", "--output", "-o", help="Output directory"),
    ):
        """Backup the project database."""
        # Créer le nom du fichier de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"projects_backup_{timestamp}.db"
        backup_path = Path(output) / backup_name

        # Copier la base de données
        try:
            shutil.copy2(db.DB_PATH, backup_path)
            display.print_success(f"Database backed up to: {backup_path}")
        except Exception as e:
            display.print_error(f"Backup failed: {e}")
            raise typer.Exit(1)
```

2. **Tester** :

```bash
python3 -m projects.cli backup
```

3. C'est tout ! La commande est automatiquement chargée.

## Prochaines améliorations possibles

- Commande `export` pour exporter les projets en JSON/Markdown
- Commande `search` pour rechercher dans les descriptions/tags
- Commande `archive` pour archiver les vieux projets
- Commande `open` pour ouvrir un projet dans VSCode
- Intégration avec d'autres APIs (GitLab, Bitbucket, etc.)
