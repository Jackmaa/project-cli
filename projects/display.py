"""Display utilities using Rich for beautiful terminal output."""

from typing import List, Optional
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


def format_git_status(git_status: dict) -> str:
    """
    Format git status for display in table.

    Examples:
        "main ✓" - On main, up to date
        "dev ↑2" - On dev, 2 commits ahead
        "main ↓3" - On main, 3 commits behind
        "feat ↑1↓2" - On feat, 1 ahead, 2 behind
        "main *3" - On main, 3 uncommitted changes
        "dev ↑1*2" - On dev, 1 ahead, 2 uncommitted
        "-" - Not a git repo
    """
    if not git_status or not git_status.get("is_repo"):
        return "-"

    branch = git_status.get("branch", "?")
    uncommitted = git_status.get("uncommitted_changes", 0)
    ahead = git_status.get("ahead", 0)
    behind = git_status.get("behind", 0)
    has_remote = git_status.get("has_remote", False)

    parts = [branch]

    # Add ahead/behind indicators
    if has_remote:
        if ahead > 0:
            parts.append(f"↑{ahead}")
        if behind > 0:
            parts.append(f"↓{behind}")
        if ahead == 0 and behind == 0 and uncommitted == 0:
            parts.append("✓")

    # Add uncommitted changes indicator
    if uncommitted > 0:
        parts.append(f"*{uncommitted}")

    return " ".join(parts)


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
    table.add_column("Git", style="yellow", no_wrap=True)
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

        # Format git status
        git_str = format_git_status(project.git_status)

        table.add_row(
            project.name,
            status_str,
            priority_str,
            project.language or "-",
            git_str,
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


def display_remote_metrics(metrics: dict, pipeline_status: Optional[dict], remote_info: dict):
    """
    Display remote repository metrics in a Rich panel.

    Args:
        metrics: Dictionary with repository metrics (stars, forks, etc.)
        pipeline_status: Optional dictionary with CI/CD pipeline status
        remote_info: Dictionary with remote repository information
    """
    from rich.panel import Panel

    lines = []
    lines.append(f"[bold]Platform:[/bold] {remote_info['platform'].title()}")
    lines.append(f"[bold]Repository:[/bold] {remote_info['owner']}/{remote_info['repo_name']}")
    lines.append("")

    # Metrics
    lines.append(f"⭐ Stars: {metrics['stars']}  🍴 Forks: {metrics['forks']}")
    lines.append(f"👀 Watchers: {metrics['watchers']}  ⚠️  Issues: {metrics['open_issues']}")
    lines.append(f"🔀 Pull Requests: {metrics['open_prs']}")

    if metrics.get('language'):
        lines.append(f"💻 Language: {metrics['language']}")

    if metrics.get('license'):
        lines.append(f"📜 License: {metrics['license']}")

    # Topics/tags
    if metrics.get('topics'):
        topics_str = ', '.join(metrics['topics'][:5])  # Show first 5
        if len(metrics['topics']) > 5:
            topics_str += f' (+{len(metrics["topics"]) - 5} more)'
        lines.append(f"🏷️  Topics: {topics_str}")

    # CI/CD status
    if pipeline_status:
        status = pipeline_status.get('conclusion', pipeline_status.get('status', 'unknown'))
        if status == 'success':
            status_icon = "✓"
            status_color = "green"
        elif status == 'failure':
            status_icon = "❌"
            status_color = "red"
        elif status in ['pending', 'queued', 'in_progress']:
            status_icon = "⏳"
            status_color = "yellow"
        else:
            status_icon = "?"
            status_color = "dim"

        lines.append(f"🔧 CI/CD: [{status_color}]{status_icon} {status}[/{status_color}]")

    # Last synced
    lines.append("")
    if remote_info.get('last_synced_at'):
        from datetime import datetime
        synced_dt = datetime.fromisoformat(remote_info['last_synced_at'])
        rel_time = format_relative_time(synced_dt)
        lines.append(f"[dim]Last synced: {rel_time}[/dim]")
    else:
        lines.append(f"[dim]Not synced yet[/dim]")

    panel = Panel(
        "\n".join(lines),
        title="📊 Remote Repository",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def display_sync_status_table(projects: list):
    """
    Display sync status table for multiple projects.

    Args:
        projects: List of project dictionaries with sync information
    """
    from rich.table import Table

    table = Table(title="Sync Status")
    table.add_column("Project", style="cyan")
    table.add_column("Platform", style="green")
    table.add_column("Repository", style="blue")
    table.add_column("Last Synced", style="yellow")
    table.add_column("Enabled", justify="center")

    for proj in projects:
        table.add_row(
            proj.get('name', '-'),
            proj.get('platform', '-'),
            proj.get('repository', '-'),
            proj.get('last_synced', '-'),
            proj.get('enabled', '✗')
        )

    console.print(table)

