"""Commands package - each command is in its own module."""

import importlib
import pkgutil
from pathlib import Path
from typing import List
import typer


def load_commands(app: typer.Typer):
    """
    Charge dynamiquement toutes les commandes depuis ce package.

    Cette fonction :
    1. Scanne le dossier commands/
    2. Pour chaque fichier .py (sauf __init__.py)
    3. Importe le module
    4. Si le module a une fonction 'register_command', l'appelle avec l'app

    Exemple de fichier de commande :
    ```python
    import typer
    from .. import database as db

    def register_command(app: typer.Typer):
        @app.command()
        def ma_commande():
            '''Description de ma commande'''
            print("Hello!")
    ```
    """
    # __path__ est une variable spéciale qui contient le chemin du package
    commands_dir = Path(__file__).parent

    # pkgutil.iter_modules liste tous les modules dans un package
    for module_info in pkgutil.iter_modules([str(commands_dir)]):
        module_name = module_info.name

        # Ignorer __init__ et les fichiers privés
        if module_name.startswith('_'):
            continue

        # Importer le module dynamiquement
        # f"projects.commands.{module_name}" est le nom complet du module
        full_module_name = f"projects.commands.{module_name}"
        module = importlib.import_module(full_module_name)

        # Si le module a une fonction 'register_command', l'appeler
        if hasattr(module, 'register_command'):
            module.register_command(app)
