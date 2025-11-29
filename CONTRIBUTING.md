# Guide : Ajouter une nouvelle commande

Ce guide t'explique **étape par étape** comment ajouter une nouvelle commande à ce CLI.

## Exemple : Créer une commande `open`

On va créer une commande qui ouvre un projet dans VSCode.

### Étape 1 : Créer le fichier de commande

Crée un nouveau fichier dans `projects/commands/` :

```bash
touch projects/commands/open.py
```

### Étape 2 : Écrire la structure de base

Ouvre `projects/commands/open.py` et écris :

```python
"""Open command - Open a project in VSCode."""

import typer
import subprocess

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'open' command with the Typer app."""

    @app.command()
    def open(
        name: str = typer.Argument(..., help="Project name"),
    ):
        """Open a project in VSCode."""
        # TODO: Implémenter la logique ici
        pass
```

### Explication ligne par ligne (pour débutants)

```python
"""Open command - Open a project in VSCode."""
```
👉 La docstring en haut du fichier. Explique ce que fait la commande.

```python
import typer
import subprocess
```
👉 Import des librairies nécessaires :
- `typer` : Pour créer la commande CLI
- `subprocess` : Pour exécuter des commandes système (comme `code`)

```python
from .. import database as db
from .. import display
```
👉 Import des modules du projet :
- `..` = remonter d'un niveau (depuis `commands/` vers `projects/`)
- `database as db` = importer le module `database` et le renommer `db`
- `display` = module pour afficher les messages

```python
def register_command(app: typer.Typer):
```
👉 Cette fonction **doit toujours s'appeler `register_command`**.
Elle reçoit l'app Typer en paramètre.

```python
    @app.command()
```
👉 Décorateur qui transforme la fonction en commande CLI.
Le nom de la fonction devient le nom de la commande.

```python
    def open(
        name: str = typer.Argument(..., help="Project name"),
    ):
```
👉 Définition de la commande `open` :
- `name` : Argument obligatoire (grâce aux `...`)
- `str` : Le type de l'argument (texte)
- `typer.Argument(...)` : C'est un argument positionnel (pas une option)
- `help="..."` : Texte d'aide affiché avec `--help`

### Étape 3 : Implémenter la logique

```python
def register_command(app: typer.Typer):
    """Register the 'open' command with the Typer app."""

    @app.command()
    def open(
        name: str = typer.Argument(..., help="Project name"),
    ):
        """Open a project in VSCode."""
        # Récupérer le projet depuis la base de données
        project = db.get_project(name)

        # Vérifier s'il existe
        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        # Vérifier s'il a un path
        if not project.path:
            display.print_error(f"Project '{name}' has no path set.")
            raise typer.Exit(1)

        # Ouvrir dans VSCode
        try:
            subprocess.run(["code", project.path], check=True)
            display.print_success(f"Opened '{name}' in VSCode.")
        except FileNotFoundError:
            display.print_error("VSCode (code) is not installed or not in PATH.")
            raise typer.Exit(1)
        except subprocess.CalledProcessError:
            display.print_error("Failed to open project.")
            raise typer.Exit(1)
```

### Explication de la logique

1. **Récupération du projet** :
```python
project = db.get_project(name)
```
Appelle la fonction `get_project()` du module `database` pour récupérer le projet.

2. **Vérifications** :
```python
if not project:
    display.print_error(f"Project '{name}' not found.")
    raise typer.Exit(1)
```
Si le projet n'existe pas, afficher une erreur et quitter avec le code 1 (erreur).

3. **Exécution de la commande** :
```python
subprocess.run(["code", project.path], check=True)
```
Exécute la commande `code /path/to/project` pour ouvrir VSCode.

4. **Gestion des erreurs** :
```python
except FileNotFoundError:
    display.print_error("VSCode (code) is not installed or not in PATH.")
```
Si `code` n'est pas trouvé, afficher un message d'erreur.

### Étape 4 : Tester

C'est tout ! La commande est automatiquement chargée au démarrage.

```bash
# Voir l'aide
python3 -m projects.cli open --help

# Utiliser la commande
python3 -m projects.cli open project-cli
```

## Types de paramètres

### Argument positionnel (obligatoire)

```python
name: str = typer.Argument(..., help="Project name")
```

Utilisation : `projects cmd my-project`

### Argument optionnel

```python
name: str = typer.Argument(None, help="Project name (optional)")
```

Utilisation :
- `projects cmd` (sans argument)
- `projects cmd my-project` (avec argument)

### Option avec flag court

```python
limit: int = typer.Option(10, "--limit", "-n", help="Number of items")
```

Utilisation :
- `projects cmd --limit 20`
- `projects cmd -n 20`

### Option booléenne (flag)

```python
all: bool = typer.Option(False, "--all", "-a", help="Show all")
```

Utilisation :
- `projects cmd` (False par défaut)
- `projects cmd --all` (True)
- `projects cmd -a` (True)

### Enum (choix multiples)

```python
from enum import Enum

class Status(str, Enum):
    active = "active"
    paused = "paused"

status: Status = typer.Option(None, "--status", "-s", help="Filter by status")
```

Utilisation :
- `projects cmd --status active`
- `projects cmd -s paused`

Typer va automatiquement valider que la valeur est dans l'Enum.

## Fonctions utiles

### Affichage

```python
from .. import display

display.print_success("Operation successful!")
display.print_error("Something went wrong!")
display.print_info("Some information")
```

### Base de données

```python
from .. import database as db

# Récupérer un projet
project = db.get_project("my-project")

# Récupérer tous les projets
projects = db.get_all_projects()

# Récupérer avec filtre
projects = db.get_all_projects(status="active", tag="python")

# Ajouter un projet
db.add_project(name="test", path="/path/to/test")

# Supprimer un projet
db.delete_project("test")
```

### Demander confirmation

```python
confirm = typer.confirm("Are you sure?")
if not confirm:
    display.print_info("Cancelled.")
    raise typer.Abort()
```

### Exécuter une commande système

```python
import subprocess

try:
    result = subprocess.run(
        ["git", "status"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
except subprocess.CalledProcessError as e:
    display.print_error(f"Command failed: {e.stderr}")
```

## Bonnes pratiques

1. **Toujours vérifier** que le projet existe avant de faire des opérations :
```python
project = db.get_project(name)
if not project:
    display.print_error(f"Project '{name}' not found.")
    raise typer.Exit(1)
```

2. **Gérer les erreurs** proprement avec try/except

3. **Donner du feedback** à l'utilisateur avec `display.print_*`

4. **Documenter** ta commande avec une docstring

5. **Utiliser les type hints** : `name: str`, `limit: int`, etc.

## Architecture complète d'un fichier de commande

```python
"""Description courte de la commande."""

# Imports standards
import subprocess
from typing import Optional
from pathlib import Path

# Imports de librairies tierces
import typer

# Imports du projet
from .. import database as db
from .. import display


# Fonctions helper (si besoin)
def helper_function():
    """Une fonction utilitaire."""
    pass


# Fonction d'enregistrement (OBLIGATOIRE)
def register_command(app: typer.Typer):
    """Register the 'nom' command with the Typer app."""

    @app.command()
    def nom(
        arg1: str = typer.Argument(..., help="Description"),
        option1: int = typer.Option(10, "--opt", "-o", help="Description"),
    ):
        """Description de ce que fait la commande."""
        # Implémentation ici
        pass
```

## Questions fréquentes

### Q: Pourquoi `register_command` ?

C'est le pattern utilisé par le système de chargement dynamique.
Le fichier `commands/__init__.py` cherche automatiquement cette fonction dans chaque module.

### Q: Que signifie `..` dans les imports ?

En Python, `.` = dossier actuel, `..` = dossier parent.

Depuis `projects/commands/open.py` :
- `from . import autre_commande` → importe depuis `projects/commands/`
- `from .. import database` → importe depuis `projects/`

### Q: Comment déboguer ma commande ?

Ajoute des `print()` :

```python
print(f"DEBUG: project = {project}")
print(f"DEBUG: path = {project.path}")
```

Ou utilise `display.print_info()` :

```python
display.print_info(f"Opening {project.path}")
```

### Q: Dois-je modifier d'autres fichiers ?

**Non !** Juste créer ton fichier dans `commands/` et c'est tout.
Le système de chargement dynamique s'occupe du reste.

## Exemples de commandes simples

### Commande sans argument

```python
def register_command(app: typer.Typer):
    @app.command()
    def hello():
        """Say hello."""
        display.print_success("Hello, world!")
```

### Commande avec un argument

```python
def register_command(app: typer.Typer):
    @app.command()
    def greet(name: str = typer.Argument(..., help="Name to greet")):
        """Greet someone."""
        display.print_success(f"Hello, {name}!")
```

### Commande avec options

```python
def register_command(app: typer.Typer):
    @app.command()
    def count(
        limit: int = typer.Option(10, "--limit", "-n", help="Max count"),
        start: int = typer.Option(1, "--start", "-s", help="Start from"),
    ):
        """Count from start to limit."""
        for i in range(start, start + limit):
            print(i)
```

## Ressources

- [Documentation Typer](https://typer.tiangolo.com/)
- [Documentation Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture du projet

Bon développement !
