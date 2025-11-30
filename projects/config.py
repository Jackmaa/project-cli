"""Configuration management for project-cli."""

import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict


def get_config_path() -> Path:
    """Get path to config file: ~/.config/project-cli/config.json"""
    config_dir = Path.home() / ".config" / "project-cli"
    return config_dir / "config.json"


def load_config() -> dict:
    """Load config from JSON file, return empty dict if not exists."""
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupted config file - backup and return empty
        backup_path = config_path.with_suffix(".json.bak")
        if config_path.exists():
            shutil.copy(config_path, backup_path)
        return {}
    except Exception:
        return {}


def save_config(config: dict) -> None:
    """Save config to JSON file, creates parent dirs if needed."""
    config_path = get_config_path()

    # Create parent directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        # Fail silently or log - don't crash the app
        print(f"Warning: Could not save config: {e}")


def get_ide() -> Optional[str]:
    """Get configured IDE command, returns None if not set."""
    config = load_config()
    return config.get("ide")


def set_ide(ide_name: Optional[str]) -> None:
    """Set IDE preference and save. None to clear."""
    config = load_config()

    if ide_name is None:
        config.pop("ide", None)
    else:
        config["ide"] = ide_name

    # Ensure version is set
    if "version" not in config:
        config["version"] = "1.0"

    save_config(config)


def detect_available_ides() -> List[Dict[str, str]]:
    """
    Detect installed IDEs using shutil.which().
    Returns: [{"name": "Neovim", "command": "nvim"}, ...]
    """
    ides = [
        {"name": "Neovim", "command": "nvim"},
        {"name": "Vim", "command": "vim"},
        {"name": "VS Code", "command": "code"},
        {"name": "Cursor AI", "command": "cursor"},
        {"name": "Emacs", "command": "emacs"},
        {"name": "Sublime Text", "command": "subl"},
        {"name": "Nano", "command": "nano"},
        {"name": "PyCharm", "command": "pycharm"},
        {"name": "IntelliJ IDEA", "command": "idea"},
    ]

    # Filter to only installed IDEs
    available = []
    for ide in ides:
        if shutil.which(ide["command"]):
            available.append(ide)

    return available


def interactive_ide_setup() -> str:
    """
    Show interactive IDE picker using inquirer.
    Returns: chosen IDE command (e.g., "nvim")
    """
    import inquirer

    available_ides = detect_available_ides()

    if not available_ides:
        # No IDEs detected - ask for manual entry
        questions = [
            inquirer.Text(
                'ide',
                message="No common IDEs detected. Enter command to open IDE (e.g., 'gedit', 'kate')",
            )
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers['ide']:
            # User cancelled or empty input - use nano as fallback
            ide_command = "nano"
        else:
            ide_command = answers['ide'].strip()

            # Validate that the command exists
            if not shutil.which(ide_command):
                print(f"Warning: '{ide_command}' not found in PATH. Using anyway.")
    else:
        # Show detected IDEs
        choices = [f"{ide['name']} ({ide['command']})" for ide in available_ides]
        choices.append("Other (manual entry)")

        questions = [
            inquirer.List(
                'ide',
                message="Select your preferred IDE",
                choices=choices,
                carousel=True,
            )
        ]

        answers = inquirer.prompt(questions)

        if not answers:
            # User cancelled - use first available IDE
            ide_command = available_ides[0]['command']
        elif answers['ide'] == "Other (manual entry)":
            # Manual entry
            questions = [
                inquirer.Text(
                    'custom_ide',
                    message="Enter command to open IDE",
                )
            ]
            custom_answers = inquirer.prompt(questions)

            if not custom_answers or not custom_answers['custom_ide']:
                ide_command = available_ides[0]['command']
            else:
                ide_command = custom_answers['custom_ide'].strip()
        else:
            # Extract command from selection "Name (command)"
            selected = answers['ide']
            ide_command = selected.split('(')[-1].rstrip(')')

    # Save the selection
    set_ide(ide_command)

    return ide_command
