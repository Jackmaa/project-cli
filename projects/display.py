"""Display utilities using Rich for beautiful terminal output."""

from typing import List
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .models import Project


console = Console()


def get_status_emoji(status: str) -> str:
    emoji_map = {
        "active": "⚡",
        "paused": "⏸️",
        "completed": "✔️",
        "abandoned": "🗑️",
    }
    return emoji_map.get(status, "•")


def get_priority_emoji(priority: str) -> str:
    emoji_map = {
        "high": "🔥",
        "medium": "●",
        "low": "○",
    }
    return emoji_map.get(priority, "●")



def get_status_color(status: str) -> str:
    """Get color for a project status."""
    color_map = {
        "active": "green",
        "paused": "yellow",
        "completed": "blue",
        "abandoned": "red",
    }
    return color_map.get(status, "white")


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 days ago')."""
    now = datetime.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days}d ago"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f"{months}mo ago"
    else:
        years = diff.days // 365
        return f"{years}y ago"


def display_projects_table(projects: List[Project]):
    """Display projects in a formatted table."""
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return

    table = Table(title="Your Projects", box=box.ROUNDED)

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Language", style="magenta")
    table.add_column("Last Activity", style="dim")
    table.add_column("Tags", style="blue")

    for project in projects:
        # Formater la derni�re activit�
        if project.last_activity:
            activity = format_relative_time(project.last_activity)
        else:
            activity = "never"

        # Formater les tags
        tags_str = ", ".join(project.tags) if project.tags else "-"

        # Status avec emoji et couleur
        status_str = f"{get_status_emoji(project.status)} {project.status}"

        # Priority avec emoji
        priority_str = f"{get_priority_emoji(project.priority)} {project.priority}"

        table.add_row(
            project.name,
            status_str,
            priority_str,
            project.language or "-",
            activity,
            tags_str,
            style=get_status_color(project.status),
        )

    console.print(table)


def display_project_details(project: Project):
    """Display detailed information about a single project."""
    # Titre avec emoji
    title = f"{get_status_emoji(project.status)} {project.name}"

    # Construire le contenu
    lines = []
    lines.append(f"[bold]Status:[/bold] {project.status}")
    lines.append(f"[bold]Priority:[/bold] {get_priority_emoji(project.priority)} {project.priority}")

    if project.description:
        lines.append(f"[bold]Description:[/bold] {project.description}")

    if project.path:
        lines.append(f"[bold]Path:[/bold] {project.path}")

    if project.language:
        lines.append(f"[bold]Language:[/bold] {project.language}")

    if project.tags:
        lines.append(f"[bold]Tags:[/bold] {', '.join(project.tags)}")

    # Dates
    lines.append(f"[bold]Created:[/bold] {project.created_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"[bold]Updated:[/bold] {project.updated_at.strftime('%Y-%m-%d %H:%M')}")

    if project.last_activity:
        rel_time = format_relative_time(project.last_activity)
        lines.append(f"[bold]Last Activity:[/bold] {project.last_activity.strftime('%Y-%m-%d %H:%M')} ({rel_time})")
    else:
        lines.append("[bold]Last Activity:[/bold] Never")

    content = "\n".join(lines)

    panel = Panel(content, title=title, border_style=get_status_color(project.status))
    console.print(panel)


def display_stats(stats: dict):
    """Display project statistics."""
    table = Table(title="Project Statistics", box=box.ROUNDED)

    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="bold")

    # Total
    table.add_row("Total Projects", str(stats["total"]))

    # Separator
    table.add_row("", "")

    # By status
    for status, count in stats["by_status"].items():
        emoji = get_status_emoji(status)
        table.add_row(f"{emoji} {status.capitalize()}", str(count))

    # Separator
    table.add_row("", "")

    # By priority
    for priority, count in stats["by_priority"].items():
        emoji = get_priority_emoji(priority)
        table.add_row(f"{emoji} {priority.capitalize()}", str(count))

    # Oldest stale
    if stats["oldest_stale"]:
        name, last_activity = stats["oldest_stale"]
        dt = datetime.fromisoformat(last_activity)
        rel_time = format_relative_time(dt)
        table.add_row("", "")
        table.add_row("Oldest Stale Project", f"{name} ({rel_time})")

    console.print(table)


def print_success(message: str):
    console.print(f"[green]✔[/green] {message}")

def print_error(message: str):
    console.print(f"[red]✖[/red] {message}")

def print_info(message: str):
    console.print(f"[blue]ℹ[/blue] {message}")

