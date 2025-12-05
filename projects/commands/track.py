"""Time tracking commands."""

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional

from .. import database as db
from .. import hook_installer
from .. import display

console = Console()


def register_command(app: typer.Typer):
    """Register the track command group."""

    track_app = typer.Typer(help="Track time spent on projects")

    @track_app.command("install-hooks")
    def install_hooks_cmd(
        project: Optional[str] = typer.Argument(None, help="Project name (or use --all)"),
        all_projects: bool = typer.Option(False, "--all", help="Install hooks for all projects"),
    ):
        """Install post-commit hooks for time tracking."""
        if not project and not all_projects:
            console.print("[red]Error:[/red] Please specify a project name or use --all")
            raise typer.Exit(1)

        db_path = db.DB_PATH

        if all_projects:
            # Install for all projects
            projects = db.get_all_projects()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Installing hooks...", total=len(projects))

                success_count = 0
                skip_count = 0
                fail_count = 0

                for proj in projects:
                    if not proj.path:
                        skip_count += 1
                        progress.update(task, advance=1)
                        continue

                    project_path = Path(proj.path)
                    success, message = hook_installer.install_hooks(
                        project_path, proj.id, db_path
                    )

                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        if "Not a git repository" not in message:
                            console.print(f"[yellow]{proj.name}:[/yellow] {message}")

                    progress.update(task, advance=1)

            console.print(f"\n[green]✓ Installed hooks for {success_count} projects[/green]")
            if skip_count > 0:
                console.print(f"[yellow]⊘ Skipped {skip_count} projects (no path)[/yellow]")
            if fail_count > 0:
                console.print(f"[red]✗ Failed for {fail_count} projects[/red]")

        else:
            # Install for single project
            proj = db.get_project(project)
            if not proj:
                console.print(f"[red]Error:[/red] Project '{project}' not found")
                raise typer.Exit(1)

            if not proj.path:
                console.print(f"[red]Error:[/red] Project '{project}' has no path")
                raise typer.Exit(1)

            project_path = Path(proj.path)
            success, message = hook_installer.install_hooks(project_path, proj.id, db_path)

            if success:
                console.print(f"[green]✓ {message}[/green]")
            else:
                console.print(f"[red]✗ {message}[/red]")
                raise typer.Exit(1)

    @track_app.command("uninstall-hooks")
    def uninstall_hooks_cmd(
        project: Optional[str] = typer.Argument(None, help="Project name (or use --all)"),
        all_projects: bool = typer.Option(False, "--all", help="Uninstall hooks for all projects"),
    ):
        """Uninstall post-commit hooks."""
        if not project and not all_projects:
            console.print("[red]Error:[/red] Please specify a project name or use --all")
            raise typer.Exit(1)

        if all_projects:
            # Uninstall for all projects
            projects = db.get_all_projects()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Uninstalling hooks...", total=len(projects))

                success_count = 0
                skip_count = 0

                for proj in projects:
                    if not proj.path:
                        skip_count += 1
                        progress.update(task, advance=1)
                        continue

                    project_path = Path(proj.path)
                    success, message = hook_installer.uninstall_hooks(project_path, proj.id)

                    if success:
                        success_count += 1

                    progress.update(task, advance=1)

            console.print(f"\n[green]✓ Uninstalled hooks for {success_count} projects[/green]")
            if skip_count > 0:
                console.print(f"[yellow]⊘ Skipped {skip_count} projects (no path)[/yellow]")

        else:
            # Uninstall for single project
            proj = db.get_project(project)
            if not proj:
                console.print(f"[red]Error:[/red] Project '{project}' not found")
                raise typer.Exit(1)

            if not proj.path:
                console.print(f"[red]Error:[/red] Project '{project}' has no path")
                raise typer.Exit(1)

            project_path = Path(proj.path)
            success, message = hook_installer.uninstall_hooks(project_path, proj.id)

            if success:
                console.print(f"[green]✓ {message}[/green]")
            else:
                console.print(f"[red]✗ {message}[/red]")
                raise typer.Exit(1)

    @track_app.command("log")
    def show_log(
        project: Optional[str] = typer.Argument(None, help="Project name (omit for all projects)"),
        days: int = typer.Option(30, "--days", "-d", help="Number of days to look back"),
    ):
        """Show commit time logs."""
        if project:
            proj = db.get_project(project)
            if not proj:
                console.print(f"[red]Error:[/red] Project '{project}' not found")
                raise typer.Exit(1)
            project_id = proj.id
        else:
            project_id = None

        logs = db.get_commit_time_logs(project_id, days)

        if not logs:
            console.print("[yellow]No time logs found[/yellow]")
            return

        # Create table
        table = Table(title=f"Commit Time Logs (Last {days} days)")
        table.add_column("Date", style="cyan")
        table.add_column("Project", style="green")
        table.add_column("Commit", style="blue")
        table.add_column("Message", style="white")
        table.add_column("Time", style="magenta", justify="right")
        table.add_column("Branch", style="yellow")

        total_minutes = 0

        for log in logs:
            # Format date
            commit_date = log['commit_date'][:10] if log['commit_date'] else "Unknown"

            # Format commit hash
            commit_hash = log['commit_hash'][:7] if log['commit_hash'] else "Unknown"

            # Format message (truncate if too long)
            message = log['commit_message'] or ""
            if len(message) > 50:
                message = message[:47] + "..."

            # Format time
            minutes = log['time_spent_minutes']
            total_minutes += minutes
            hours = minutes // 60
            mins = minutes % 60
            if hours > 0:
                time_str = f"{hours}h {mins}m"
            else:
                time_str = f"{mins}m"

            table.add_row(
                commit_date,
                log['project_name'],
                commit_hash,
                message,
                time_str,
                log['branch'] or "-",
            )

        console.print(table)

        # Print summary
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        console.print(f"\n[bold]Total:[/bold] {len(logs)} commits, {total_hours}h {total_mins}m")

    @track_app.command("summary")
    def show_summary(
        days: int = typer.Option(30, "--days", "-d", help="Number of days to look back"),
        by_project: bool = typer.Option(False, "--by-project", help="Group by project instead of day"),
        chart: bool = typer.Option(False, "--chart", help="Show chart (requires plotext)"),
    ):
        """Show time tracking summary."""
        if by_project:
            summaries = db.get_time_summary_by_project(days)

            if not summaries:
                console.print("[yellow]No time tracking data found[/yellow]")
                return

            # Create table
            table = Table(title=f"Time Summary by Project (Last {days} days)")
            table.add_column("Project", style="green")
            table.add_column("Commits", justify="right", style="cyan")
            table.add_column("Total Time", justify="right", style="magenta")

            total_commits = 0
            total_minutes = 0

            for summary in summaries:
                minutes = summary['total_minutes']
                total_minutes += minutes
                total_commits += summary['commit_count']

                hours = minutes // 60
                mins = minutes % 60
                if hours > 0:
                    time_str = f"{hours}h {mins}m"
                else:
                    time_str = f"{mins}m"

                table.add_row(
                    summary['project_name'],
                    str(summary['commit_count']),
                    time_str,
                )

            console.print(table)

            # Print total
            total_hours = total_minutes // 60
            total_mins = total_minutes % 60
            console.print(f"\n[bold]Total:[/bold] {total_commits} commits, {total_hours}h {total_mins}m")

        else:
            summaries = db.get_time_summary_by_day(None, days)

            if not summaries:
                console.print("[yellow]No time tracking data found[/yellow]")
                return

            # Create table
            table = Table(title=f"Time Summary by Day (Last {days} days)")
            table.add_column("Day", style="cyan")
            table.add_column("Commits", justify="right", style="blue")
            table.add_column("Total Time", justify="right", style="magenta")

            total_commits = 0
            total_minutes = 0

            for summary in summaries:
                minutes = summary['total_minutes']
                total_minutes += minutes
                total_commits += summary['commit_count']

                hours = minutes // 60
                mins = minutes % 60
                if hours > 0:
                    time_str = f"{hours}h {mins}m"
                else:
                    time_str = f"{mins}m"

                table.add_row(
                    summary['day'],
                    str(summary['commit_count']),
                    time_str,
                )

            console.print(table)

            # Print total
            total_hours = total_minutes // 60
            total_mins = total_minutes % 60
            console.print(f"\n[bold]Total:[/bold] {total_commits} commits, {total_hours}h {total_mins}m")

            # Show chart if requested
            if chart:
                try:
                    import plotext as plt

                    # Prepare data (reverse to show oldest first)
                    days_list = [s['day'] for s in reversed(summaries)]
                    minutes_list = [s['total_minutes'] for s in reversed(summaries)]

                    # Limit to last 14 days for readability
                    if len(days_list) > 14:
                        days_list = days_list[-14:]
                        minutes_list = minutes_list[-14:]

                    # Format x-axis labels (show only day and month)
                    x_labels = [d.split('-')[1] + '/' + d.split('-')[2] for d in days_list]

                    plt.clear_figure()
                    plt.bar(x_labels, minutes_list)
                    plt.title("Time Spent (minutes per day)")
                    plt.xlabel("Date")
                    plt.ylabel("Minutes")
                    plt.plotsize(80, 20)
                    plt.show()

                except ImportError:
                    console.print("[yellow]plotext not installed. Install with: pip install plotext[/yellow]")

    @track_app.command("status")
    def show_status():
        """Show which projects have time tracking hooks installed."""
        projects = db.get_all_projects()

        # Create table
        table = Table(title="Time Tracking Status")
        table.add_column("Project", style="green")
        table.add_column("Git Repo", justify="center")
        table.add_column("Hooks Installed", justify="center")
        table.add_column("Status", style="cyan")

        for proj in projects:
            if not proj.path:
                table.add_row(proj.name, "-", "-", "[dim]No path[/dim]")
                continue

            project_path = Path(proj.path)
            status = hook_installer.get_hook_status(project_path, proj.id)

            # Git repo status
            git_status = "✓" if status['is_git_repo'] else "✗"

            # Hooks installed
            hooks_status = "✓" if status['hooks_installed'] else "✗"

            # Overall status
            if status['hooks_installed']:
                overall = "[green]Active[/green]"
            elif status['is_git_repo']:
                overall = "[yellow]Not installed[/yellow]"
            else:
                overall = "[dim]Not a git repo[/dim]"

            table.add_row(proj.name, git_status, hooks_status, overall)

        console.print(table)

    app.add_typer(track_app, name="track")
