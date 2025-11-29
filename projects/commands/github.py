"""GitHub command - Fetch and display GitHub stats for a project."""

import typer
import json
import subprocess
from typing import Optional
from pathlib import Path
from rich.table import Table
from rich.panel import Panel
from rich import box

from .. import database as db
from .. import display


def get_github_repo_info(repo_path: Path) -> Optional[dict]:
    """
    Extract GitHub owner/repo from git remote.

    Returns: {"owner": "username", "repo": "reponame"} or None
    """
    try:
        # Récupérer l'URL remote origin
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )

        url = result.stdout.strip()

        # Parser l'URL pour extraire owner/repo
        # Formats possibles:
        # - https://github.com/owner/repo.git
        # - git@github.com:owner/repo.git
        if "github.com" not in url:
            return None

        # Nettoyer l'URL
        if url.startswith("https://"):
            # https://github.com/owner/repo.git
            parts = url.replace("https://github.com/", "").replace(".git", "").split("/")
        elif url.startswith("git@"):
            # git@github.com:owner/repo.git
            parts = url.replace("git@github.com:", "").replace(".git", "").split("/")
        else:
            return None

        if len(parts) != 2:
            return None

        return {"owner": parts[0], "repo": parts[1]}

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def fetch_github_stats(owner: str, repo: str) -> Optional[dict]:
    """
    Fetch repository stats from GitHub API.

    Returns dict with stats or None if failed.
    """
    try:
        # Utiliser curl pour faire une requête à l'API GitHub
        # Pas besoin d'authentification pour les repos publics
        url = f"https://api.github.com/repos/{owner}/{repo}"

        result = subprocess.run(
            ["curl", "-s", "-H", "Accept: application/vnd.github.v3+json", url],
            capture_output=True,
            text=True,
            check=True,
        )

        data = json.loads(result.stdout)

        # Vérifier si c'est une erreur
        if "message" in data and data["message"] == "Not Found":
            return None

        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("watchers_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "language": data.get("language"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "size": data.get("size", 0),  # en KB
            "default_branch": data.get("default_branch"),
            "license": data.get("license", {}).get("name") if data.get("license") else None,
            "url": data.get("html_url"),
        }

    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


def register_command(app: typer.Typer):
    """Register the 'github' command with the Typer app."""

    @app.command()
    def github(
        name: str = typer.Argument(..., help="Project name"),
    ):
        """Fetch and display GitHub stats for a project."""
        # Récupérer le projet
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        if not project.path:
            display.print_error(f"Project '{name}' has no path set.")
            raise typer.Exit(1)

        path = Path(project.path)
        if not path.exists():
            display.print_error(f"Path does not exist: {project.path}")
            raise typer.Exit(1)

        # Vérifier si c'est un repo git
        if not (path / ".git").exists():
            display.print_error(f"'{name}' is not a git repository.")
            raise typer.Exit(1)

        # Extraire les infos GitHub
        display.print_info("Fetching GitHub repository info...")
        repo_info = get_github_repo_info(path)

        if not repo_info:
            display.print_error("Could not extract GitHub repository info from git remote.")
            display.print_info("Make sure the remote 'origin' points to a GitHub repository.")
            raise typer.Exit(1)

        owner = repo_info["owner"]
        repo = repo_info["repo"]

        # Récupérer les stats depuis l'API
        display.print_info(f"Fetching stats for {owner}/{repo}...")
        stats = fetch_github_stats(owner, repo)

        if not stats:
            display.print_error(f"Failed to fetch stats for {owner}/{repo}.")
            display.print_info("The repository might be private or doesn't exist.")
            raise typer.Exit(1)

        # Afficher les stats dans un panel
        lines = []
        lines.append(f"[bold]Repository:[/bold] {stats['full_name']}")

        if stats["description"]:
            lines.append(f"[bold]Description:[/bold] {stats['description']}")

        lines.append("")
        lines.append(f"[bold cyan]⭐ Stars:[/bold cyan] {stats['stars']}")
        lines.append(f"[bold cyan]🍴 Forks:[/bold cyan] {stats['forks']}")
        lines.append(f"[bold cyan]👀 Watchers:[/bold cyan] {stats['watchers']}")
        lines.append(f"[bold yellow]⚠️  Open Issues:[/bold yellow] {stats['open_issues']}")

        lines.append("")
        if stats["language"]:
            lines.append(f"[bold]Language:[/bold] {stats['language']}")

        lines.append(f"[bold]Size:[/bold] {stats['size']} KB")
        lines.append(f"[bold]Default Branch:[/bold] {stats['default_branch']}")

        if stats["license"]:
            lines.append(f"[bold]License:[/bold] {stats['license']}")

        lines.append("")
        lines.append(f"[bold]Created:[/bold] {stats['created_at'][:10]}")
        lines.append(f"[bold]Last Updated:[/bold] {stats['updated_at'][:10]}")
        lines.append(f"[bold]Last Pushed:[/bold] {stats['pushed_at'][:10]}")

        lines.append("")
        lines.append(f"[bold]URL:[/bold] {stats['url']}")

        content = "\n".join(lines)
        panel = Panel(content, title=f"📊 GitHub Stats for '{name}'", border_style="cyan")

        display.console.print(panel)
