"""Sync command - Manage GitHub/GitLab synchronization."""

import typer
from typing import Optional
from rich.table import Table
from rich.console import Console

from .. import database as db
from .. import display
from .. import credentials
from .. import remote_api
from .. import sync_queue

console = Console()
app = typer.Typer(help="Manage remote repository synchronization")


def register_command(main_app: typer.Typer):
    """Register sync command group."""
    main_app.add_typer(app, name="sync")


@app.command()
def enable(
    name: Optional[str] = typer.Argument(None, help="Project name (uses current directory if not specified)"),
    platform: Optional[str] = typer.Option(None, "--platform", help="Platform: 'github' or 'gitlab'"),
    owner: Optional[str] = typer.Option(None, "--owner", help="Repository owner/username"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository name"),
):
    """
    Enable sync for a project.

    Auto-detects remote repository from git config if not specified.

    Examples:
      # Auto-detect from current directory
      cd myproject && projects sync enable

      # Specify project name (auto-detect remote)
      projects sync enable myproject

      # Manual specification
      projects sync enable myproject --platform github --owner user --repo repo
    """
    # Get project
    if not name:
        # Try to use current directory
        from pathlib import Path
        cwd = Path.cwd()

        # Find project by path
        all_projects = db.get_all_projects()
        project = None
        for p in all_projects:
            if p.path and Path(p.path).resolve() == cwd.resolve():
                project = p
                break

        if not project:
            display.print_error("Not in a project directory")
            display.print_info("Either cd to a project directory or specify project name")
            raise typer.Exit(1)
    else:
        project = db.get_project(name)
        if not project:
            display.print_error(f"Project '{name}' not found")
            raise typer.Exit(1)

    # Check if already enabled
    existing_remote = db.get_remote_repo_info(project.id)
    if existing_remote and existing_remote['sync_enabled']:
        display.print_info(f"Sync already enabled for '{project.name}'")
        display.print_info(f"Platform: {existing_remote['platform']}")
        display.print_info(f"Repository: {existing_remote['owner']}/{existing_remote['repo_name']}")
        return

    # Auto-detect or use manual specification
    if not platform or not owner or not repo:
        if not project.path:
            display.print_error(f"Project '{project.name}' has no path set")
            display.print_info("Use --platform, --owner, and --repo to specify manually")
            raise typer.Exit(1)

        display.print_info("Detecting remote repository...")
        detected_platform, detected_owner, detected_repo = remote_api.detect_remote_info(project.path)

        if not detected_platform:
            display.print_error("Could not detect remote repository")
            display.print_info("Make sure the project has a git remote configured")
            display.print_info("Or use --platform, --owner, and --repo to specify manually")
            raise typer.Exit(1)

        platform = platform or detected_platform
        owner = owner or detected_owner
        repo = repo or detected_repo

        display.print_success(f"Detected {platform.title()} repository: {owner}/{repo}")

    # Enable sync
    remote_url = f"https://{platform}.com/{owner}/{repo}.git"
    success = db.enable_sync_for_project(
        project_id=project.id,
        platform=platform,
        owner=owner,
        repo_name=repo,
        remote_url=remote_url,
        default_branch="main"
    )

    if success:
        display.print_success(f"Sync enabled for '{project.name}'")
        display.print_info(f"Run 'projects sync run {project.name}' to fetch data")
    else:
        display.print_error("Failed to enable sync")
        raise typer.Exit(1)


@app.command()
def disable(
    name: str = typer.Argument(..., help="Project name"),
    delete_cache: bool = typer.Option(False, "--delete-cache", help="Delete cached metrics data"),
):
    """
    Disable sync for a project.

    Examples:
      # Just disable sync (keep cached data)
      projects sync disable myproject

      # Disable and delete all cached data
      projects sync disable myproject --delete-cache
    """
    project = db.get_project(name)
    if not project:
        display.print_error(f"Project '{name}' not found")
        raise typer.Exit(1)

    # Check if sync is enabled
    remote_info = db.get_remote_repo_info(project.id)
    if not remote_info:
        display.print_error(f"Sync not enabled for '{name}'")
        raise typer.Exit(1)

    # Disable
    success = db.disable_sync_for_project(project.id, delete_cache=delete_cache)

    if success:
        if delete_cache:
            display.print_success(f"Sync disabled and cache deleted for '{name}'")
        else:
            display.print_success(f"Sync disabled for '{name}' (cached data preserved)")
    else:
        display.print_error("Failed to disable sync")
        raise typer.Exit(1)


@app.command()
def status(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """
    Show sync status.

    Examples:
      # Show status for one project
      projects sync status myproject

      # Show all projects with sync
      projects sync status --all

      # Show detailed information
      projects sync status --all --verbose
    """
    if name:
        # Single project
        project = db.get_project(name)
        if not project:
            display.print_error(f"Project '{name}' not found")
            raise typer.Exit(1)

        remote_info = db.get_remote_repo_info(project.id)
        if not remote_info:
            display.print_error(f"Sync not enabled for '{name}'")
            display.print_info(f"Enable with: projects sync enable {name}")
            raise typer.Exit(1)

        _display_single_project_status(project, remote_info, verbose)

    elif all_projects:
        # All projects
        all_projs = db.get_all_projects()

        table = Table(title="Sync Status")
        table.add_column("Project", style="cyan")
        table.add_column("Platform", style="green")
        table.add_column("Repository", style="blue")
        table.add_column("Last Synced", style="yellow")
        table.add_column("Enabled", justify="center")

        for proj in all_projs:
            remote_info = db.get_remote_repo_info(proj.id)

            if remote_info:
                last_synced = remote_info['last_synced_at']
                if last_synced:
                    from datetime import datetime
                    synced_dt = datetime.fromisoformat(last_synced)
                    last_synced_str = _format_relative_time(synced_dt)
                else:
                    last_synced_str = "Never"

                enabled_str = "✓" if remote_info['sync_enabled'] else "✗"

                table.add_row(
                    proj.name,
                    remote_info['platform'].title(),
                    f"{remote_info['owner']}/{remote_info['repo_name']}",
                    last_synced_str,
                    enabled_str
                )
            else:
                table.add_row(proj.name, "-", "-", "-", "✗")

        console.print(table)

    else:
        display.print_error("Specify a project name or use --all")
        raise typer.Exit(1)


def _display_single_project_status(project, remote_info: dict, verbose: bool):
    """Display detailed status for a single project."""
    from datetime import datetime

    lines = []
    lines.append(f"[bold]Project:[/bold] {project.name}")
    lines.append(f"[bold]Platform:[/bold] {remote_info['platform'].title()}")
    lines.append(f"[bold]Repository:[/bold] {remote_info['owner']}/{remote_info['repo_name']}")
    lines.append(f"[bold]Sync Enabled:[/bold] {'Yes' if remote_info['sync_enabled'] else 'No'}")

    if remote_info['last_synced_at']:
        synced_dt = datetime.fromisoformat(remote_info['last_synced_at'])
        lines.append(f"[bold]Last Synced:[/bold] {_format_relative_time(synced_dt)}")
    else:
        lines.append(f"[bold]Last Synced:[/bold] Never")

    # Get cached metrics if verbose
    if verbose:
        metrics = db.get_metrics_for_project(project.id)
        if metrics:
            lines.append("")
            lines.append("[bold]Cached Metrics:[/bold]")
            lines.append(f"  ⭐ Stars: {metrics['stars']}")
            lines.append(f"  🍴 Forks: {metrics['forks']}")
            lines.append(f"  ⚠️  Issues: {metrics['open_issues']}")
            lines.append(f"  🔀 Pull Requests: {metrics['open_prs']}")
            if metrics.get('language'):
                lines.append(f"  💻 Language: {metrics['language']}")

    for line in lines:
        console.print(line)


def _format_relative_time(dt) -> str:
    """Format datetime as relative time (e.g., '2h ago')."""
    from datetime import datetime, timedelta

    now = datetime.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}d ago"
    elif diff < timedelta(days=30):
        weeks = diff.days // 7
        return f"{weeks}w ago"
    else:
        months = diff.days // 30
        return f"{months}mo ago"


@app.command()
def run(
    name: Optional[str] = typer.Argument(None, help="Project name (syncs all if not specified)"),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Sync all enabled projects"),
    update_metadata: bool = typer.Option(False, "--update-metadata", help="Update project metadata from remote"),
    force: bool = typer.Option(False, "--force", "-f", help="Force sync (ignore cache TTL)"),
    priority: int = typer.Option(5, "--priority", "-p", help="Queue priority (1=highest, 10=lowest)"),
):
    """
    Run sync for project(s).

    Examples:
      # Sync one project
      projects sync run myproject

      # Sync all enabled projects
      projects sync run --all

      # Force sync (ignore cache)
      projects sync run myproject --force

      # Update project metadata from GitHub
      projects sync run myproject --update-metadata
    """
    from .. import sync_orchestrator

    orchestrator = sync_orchestrator.SyncOrchestrator()

    if all_projects:
        # Sync all enabled projects
        results = orchestrator.sync_all_enabled(update_metadata=update_metadata)

        # Display summary
        console.print("\n[bold]Sync Summary[/bold]")
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        console.print(f"  Total: {len(results)}")
        console.print(f"  [green]Successful: {successful}[/green]")
        if failed > 0:
            console.print(f"  [red]Failed: {failed}[/red]")

        # Show failed projects
        if failed > 0:
            console.print("\n[bold red]Failed Projects:[/bold red]")
            for result in results:
                if not result.success:
                    console.print(f"  - {result.project_name}: {result.error}")

    elif name:
        # Sync single project
        project = db.get_project(name)
        if not project:
            display.print_error(f"Project '{name}' not found")
            raise typer.Exit(1)

        display.print_info(f"Syncing {project.name}...")

        result = orchestrator.sync_project(
            project_id=project.id,
            update_metadata=update_metadata,
            force=force
        )

        # Display result
        if result.success:
            display.print_success(f"Synced {result.project_name} in {result.duration_seconds:.1f}s")

            if result.error:
                # Cached data was used
                display.print_info(result.error)
            else:
                # Fresh data fetched
                console.print(f"  ⭐ Stars: {result.stars}")
                console.print(f"  🍴 Forks: {result.forks}")
                console.print(f"  ⚠️  Open Issues: {result.open_issues}")
                console.print(f"  🔀 Pull Requests: {result.open_prs}")

                if result.workflow_status:
                    status_icon = "✓" if result.workflow_status == "success" else "❌"
                    console.print(f"  CI/CD: {status_icon} {result.workflow_status}")
        else:
            display.print_error(f"Failed to sync {result.project_name}")
            display.print_error(result.error)
            raise typer.Exit(1)

    else:
        display.print_error("Specify a project name or use --all")
        display.print_info("Examples:")
        display.print_info("  projects sync run myproject")
        display.print_info("  projects sync run --all")
        raise typer.Exit(1)


@app.command("queue")
def queue_status(
    clear_completed: bool = typer.Option(False, "--clear-completed", help="Remove completed items"),
    retry_failed: bool = typer.Option(False, "--retry-failed", help="Retry failed items"),
):
    """
    Show and manage sync queue.

    Examples:
      # Show queue status
      projects sync queue

      # Clear old completed items
      projects sync queue --clear-completed
    """
    queue = sync_queue.SyncQueue()
    stats = queue.get_queue_stats()

    console.print(f"[bold]Sync Queue Status[/bold]")
    console.print(f"  Pending: {stats['pending']}")
    console.print(f"  Processing: {stats['processing']}")
    console.print(f"  Completed: {stats['completed']}")
    console.print(f"  Failed: {stats['failed']}")

    if clear_completed:
        deleted = queue.clear_completed(older_than_days=7)
        display.print_success(f"Cleared {deleted} completed items")


@app.command("rate-limit")
def show_rate_limit(
    platform: str = typer.Argument("github", help="Platform (github or gitlab)"),
):
    """
    Show API rate limit status.

    Examples:
      # Show GitHub rate limit
      projects sync rate-limit

      # Show GitLab rate limit
      projects sync rate-limit gitlab
    """
    token = credentials.get_token(platform)
    if not token:
        display.print_error(f"No {platform} token found")
        display.print_info(f"Store token: projects auth {platform} --token YOUR_TOKEN")
        raise typer.Exit(1)

    try:
        api = remote_api.RemoteAPI(platform, token)
        rate_info = api.get_rate_limit()

        console.print(f"[bold]{platform.title()} API Rate Limit[/bold]")
        console.print(f"  Remaining: {rate_info['remaining']}/{rate_info['limit']}")
        console.print(f"  Used: {rate_info['used']}")
        console.print(f"  Resets at: {rate_info['reset_at']}")

        # Calculate percentage
        percentage = (rate_info['remaining'] / rate_info['limit']) * 100
        if percentage > 50:
            console.print(f"  Status: [green]Good ({percentage:.0f}% remaining)[/green]")
        elif percentage > 20:
            console.print(f"  Status: [yellow]Moderate ({percentage:.0f}% remaining)[/yellow]")
        else:
            console.print(f"  Status: [red]Low ({percentage:.0f}% remaining)[/red]")

    except Exception as e:
        display.print_error(f"Failed to get rate limit: {e}")
        raise typer.Exit(1)
