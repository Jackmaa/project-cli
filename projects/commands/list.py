"""List command - List all projects."""

import typer
from typing import Optional
from enum import Enum
from pathlib import Path
import subprocess

from .. import database as db
from .. import display
from .. import config
from ..models import Project


class Status(str, Enum):
    """Project status options."""
    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"


def select_project_interactive(projects: list[Project]) -> Optional[Project]:
    """
    Show interactive project selector using inquirer.List.
    Format: "name (status, priority)"
    Returns: selected Project or None if cancelled
    """
    import inquirer

    # Format choices as "name (status, priority)"
    choices = [
        f"{p.name} ({p.status}, {p.priority})"
        for p in projects
    ]

    questions = [
        inquirer.List(
            'project',
            message="Select a project",
            choices=choices,
            carousel=True,
        )
    ]

    answers = inquirer.prompt(questions)

    if not answers:
        return None

    # Extract project name from selection
    selected_name = answers['project'].split(' (')[0]
    return next(p for p in projects if p.name == selected_name)


def select_action_interactive() -> Optional[str]:
    """
    Show action menu using inquirer.List.
    Actions: ["Open in IDE", "View Details", "Cancel"]
    Returns: action name or None
    """
    import inquirer

    actions = [
        "Open in IDE",
        "View Details",
        # Future actions (commented for now):
        # "Show Tree",
        # "Show Commits",
        # "GitHub Stats",
    ]

    questions = [
        inquirer.List(
            'action',
            message="What would you like to do?",
            choices=actions + ["Cancel"],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(questions)

    if not answers or answers['action'] == "Cancel":
        return None

    return answers['action']


def execute_action(action: str, project: Project):
    """
    Execute selected action.
    Currently: "Open in IDE" -> open_project_in_ide()
              "View Details" -> display.display_project_details()
    """
    if action == "Open in IDE":
        open_project_in_ide(project)
    elif action == "View Details":
        display.display_project_details(project)
    # Future actions will be added here


def open_project_in_ide(project: Project):
    """
    1. Validate project has path and path exists
    2. Get IDE from config (or prompt setup if not configured)
    3. Run subprocess: [ide_command, project_path]
    4. Handle errors (IDE not found, path missing, etc.)
    """
    # Check if path exists
    if not project.path:
        display.print_error(f"Project '{project.name}' has no path configured")
        display.print_info("Update path with 'projects edit {project.name}'")
        return

    path = Path(project.path)
    if not path.exists():
        display.print_error(f"Path does not exist: {project.path}")
        display.print_info(f"Update path with 'projects edit {project.name}'")
        return

    # Get or setup IDE
    ide = config.get_ide()
    if not ide:
        display.print_info("No IDE configured. Let's set one up!")
        ide = config.interactive_ide_setup()
        display.print_success(f"IDE configured: {ide}")

    # Open IDE
    try:
        display.print_info(f"Opening {project.name} in {ide}...")
        subprocess.run([ide, str(path)])
        display.print_success(f"Opened {project.name} in {ide}")
    except FileNotFoundError:
        display.print_error(f"IDE '{ide}' not found. Please reconfigure.")
        # Reset config
        config.set_ide(None)
        display.print_info("Run the command again to reconfigure your IDE")
    except Exception as e:
        display.print_error(f"Failed to open IDE: {e}")


def register_command(app: typer.Typer):
    """Register the 'list' command with the Typer app."""

    @app.command()
    def list(
        status: Optional[Status] = typer.Option(None, "--status", "-s", help="Filter by status"),
        tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    ):
        """List all projects."""
        status_value = status.value if status else None
        projects = db.get_all_projects(status=status_value, tag=tag)

        if not interactive:
            # Existing behavior - just display table
            display.display_projects_table(projects)
            return

        # Interactive mode
        if not projects:
            display.print_error("No projects found")
            display.print_info("Add projects with 'projects add'")
            return

        selected_project = select_project_interactive(projects)
        if not selected_project:
            return  # User cancelled

        action = select_action_interactive()
        if not action:
            return  # User cancelled

        execute_action(action, selected_project)
