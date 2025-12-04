"""Detail panel for project information."""

from textual.reactive import reactive
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
import json
import urllib.request
import urllib.error
from ...models import Project
from ... import display as display_utils
from ... import git_utils


class DetailPanel(Static):
    """Panel showing detailed project information."""

    project: reactive[Project | None] = reactive(None)

    def watch_project(self, project: Project | None):
        """React to project changes."""
        if project:
            self.update(self.render_project(project))
        else:
            self.update(Panel("No project selected", title="ℹ️  Info"))

    def _get_directory_size(self, path: Path) -> str:
        """Get human-readable directory size."""
        try:
            total_size = 0
            for f in path.rglob("*"):
                if f.is_file() and not any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__']
                                          for part in f.parts):
                    total_size += f.stat().st_size

            # Convert to human readable
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total_size < 1024.0:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024.0
            return f"{total_size:.1f} TB"
        except Exception:
            return "Unknown"

    def _count_lines_of_code(self, path: Path) -> int:
        """Count total lines of code in common source files."""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
                          '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.vue'}
        total_lines = 0

        try:
            files = [f for f in path.rglob("*")
                    if f.is_file() and f.suffix in code_extensions
                    and not any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__', 'dist', 'build']
                              for part in f.parts)]

            for f in files[:1000]:  # Limit to avoid hanging
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        total_lines += sum(1 for _ in file)
                except Exception:
                    continue

            return total_lines
        except Exception:
            return 0

    def _count_dependencies(self, path: Path) -> dict[str, int]:
        """Count dependencies from various package files."""
        deps = {}

        # Common subdirectories to check (for monorepos)
        search_paths = [
            path,
            path / "client",
            path / "frontend",
            path / "server",
            path / "backend",
        ]

        # package.json (Node.js)
        for search_path in search_paths:
            package_json = search_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        count = len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))
                        if count > 0:
                            deps['npm'] = deps.get('npm', 0) + count
                except Exception:
                    pass

        # requirements.txt (Python)
        for search_path in search_paths:
            requirements = search_path / "requirements.txt"
            if requirements.exists():
                try:
                    with open(requirements, 'r', encoding='utf-8') as f:
                        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                        if lines:
                            deps['pip'] = deps.get('pip', 0) + len(lines)
                except Exception:
                    pass

        # Cargo.toml (Rust)
        for search_path in search_paths:
            cargo = search_path / "Cargo.toml"
            if cargo.exists():
                try:
                    with open(cargo, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '[dependencies]' in content:
                            # Simple count of lines after [dependencies]
                            deps_section = content.split('[dependencies]')[1].split('[')[0]
                            count = len([l for l in deps_section.split('\n') if '=' in l])
                            if count > 0:
                                deps['cargo'] = deps.get('cargo', 0) + count
                except Exception:
                    pass

        # go.mod (Go)
        for search_path in search_paths:
            go_mod = search_path / "go.mod"
            if go_mod.exists():
                try:
                    with open(go_mod, 'r', encoding='utf-8') as f:
                        lines = [l for l in f if l.strip().startswith('require')]
                        if lines:
                            deps['go'] = deps.get('go', 0) + len(lines)
                except Exception:
                    pass

        return deps

    def _get_github_remote(self, path: Path) -> str | None:
        """Get GitHub repository URL from git remote."""
        if not git_utils.is_git_repo(path):
            return None

        success, output = git_utils.run_git_command(path, "remote", "get-url", "origin")
        if success and output:
            # Convert SSH to HTTPS URL
            if output.startswith("git@github.com:"):
                return "https://github.com/" + output.replace("git@github.com:", "").replace(".git", "")
            elif "github.com" in output:
                return output.replace(".git", "")
        return None

    def _get_github_stats(self, github_url: str) -> dict | None:
        """Fetch GitHub repository stats from API."""
        try:
            # Extract owner/repo from URL
            # https://github.com/owner/repo -> owner/repo
            parts = github_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return None

            owner, repo = parts[0], parts[1]
            api_url = f"https://api.github.com/repos/{owner}/{repo}"

            # Fetch with timeout
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')

            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())

                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'language': data.get('language', ''),
                    'updated_at': data.get('updated_at', ''),
                }
        except Exception:
            return None

    def render_project(self, project: Project):
        """Render enhanced project details."""
        text = Text()

        # Header: Status and priority with better formatting
        status_emoji = display_utils.get_status_emoji(project.status)
        priority_emoji = display_utils.get_priority_emoji(project.priority)

        text.append(f"{status_emoji} ", style="bold")
        text.append(f"{project.status.upper()}", style=display_utils.get_status_color(project.status))
        text.append(f" | {priority_emoji} ", style="bold")
        text.append(f"{project.priority.upper()}\n\n", style="bold yellow")

        # Description with section header
        if project.description:
            text.append("📝 Description\n", style="bold underline")
            text.append(f"{project.description}\n\n", style="")

        # Path with better formatting
        if project.path:
            text.append("📂 Location\n", style="bold underline dim")
            text.append(f"{project.path}\n\n", style="dim italic")

        # Language
        if project.language:
            text.append("💻 Language\n", style="bold underline cyan")
            text.append(f"{project.language}\n\n", style="cyan")

        # Tags as a bulleted list
        if project.tags:
            text.append("🏷️  Tags\n", style="bold underline blue")
            for tag in project.tags:
                text.append(f"  • {tag}\n", style="blue")
            text.append("\n")

        # GitHub remote URL and stats
        if project.path:
            path = Path(project.path)
            github_url = self._get_github_remote(path)
            if github_url:
                text.append("🔗 GitHub\n", style="bold underline blue")
                text.append(f"  {github_url}\n", style="blue italic")

                # Fetch GitHub stats
                gh_stats = self._get_github_stats(github_url)
                if gh_stats:
                    text.append(f"  ⭐ {gh_stats['stars']:,} stars", style="yellow")
                    text.append(f"  🔀 {gh_stats['forks']:,} forks", style="")
                    text.append(f"  👁️  {gh_stats['watchers']:,} watchers\n", style="")
                    if gh_stats['open_issues'] > 0:
                        text.append(f"  🔴 {gh_stats['open_issues']} open issues\n", style="red")
                text.append("\n")

        # Enhanced Git status with details
        if project.git_status and project.git_status.get("is_repo"):
            text.append("🔀 Git Status\n", style="bold underline yellow")

            branch = project.git_status.get("branch", "unknown")
            text.append(f"  Branch: ", style="dim")
            text.append(f"{branch}\n", style="yellow bold")

            ahead = project.git_status.get("ahead", 0)
            behind = project.git_status.get("behind", 0)

            if ahead > 0:
                text.append(f"  ↑ {ahead} ahead\n", style="green")
            if behind > 0:
                text.append(f"  ↓ {behind} behind\n", style="red")

            uncommitted = project.git_status.get("uncommitted", 0)
            if uncommitted > 0:
                text.append(f"  ● {uncommitted} uncommitted changes\n", style="yellow")
            else:
                text.append(f"  ✓ Working tree clean\n", style="green")
            text.append("\n")

        # Recent commits section (separate from git status)
        if project.path:
            path = Path(project.path)
            if git_utils.is_git_repo(path):
                commits = git_utils.get_recent_commits(path, limit=5)
                if commits:
                    text.append("📜 Recent Commits\n", style="bold underline green")
                    for commit in commits:
                        # Truncate long commit messages
                        msg = commit["message"]
                        if len(msg) > 35:
                            msg = msg[:32] + "..."

                        text.append(f"  {commit['hash']}", style="cyan bold")
                        text.append(f" {commit['date']}\n", style="dim")
                        text.append(f"    {msg}\n", style="")
                    text.append("\n")

        # Project statistics
        if project.path:
            path = Path(project.path)
            if path.exists():
                text.append("📊 Project Stats\n", style="bold underline magenta")

                # Project size
                size = self._get_directory_size(path)
                text.append(f"  Size: {size}\n", style="")

                # Lines of code
                loc = self._count_lines_of_code(path)
                if loc > 0:
                    text.append(f"  Lines of code: {loc:,}\n", style="")

                # File count
                try:
                    files = list(path.rglob("*"))
                    files = [
                        f for f in files
                        if f.is_file()
                        and not any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__', 'dist', 'build']
                                  for part in f.parts)
                    ]
                    file_count = len(files)
                    text.append(f"  Files: {file_count}\n", style="")

                    # Show top 3 file types
                    extensions = {}
                    for f in files:
                        ext = f.suffix or "(no ext)"
                        extensions[ext] = extensions.get(ext, 0) + 1

                    if extensions:
                        top_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:3]
                        text.append(f"  Types: ", style="dim")
                        type_str = ", ".join([f"{ext}({count})" for ext, count in top_exts])
                        text.append(f"{type_str}\n", style="")

                except Exception:
                    pass

                text.append("\n")

        # Dependencies
        if project.path:
            path = Path(project.path)
            deps = self._count_dependencies(path)
            if deps:
                text.append("📦 Dependencies\n", style="bold underline yellow")
                for manager, count in deps.items():
                    text.append(f"  {manager}: {count} packages\n", style="")
                text.append("\n")

        # Timeline section with better formatting
        text.append("📅 Timeline\n", style="bold underline cyan")

        if project.created_at:
            from datetime import datetime
            if isinstance(project.created_at, str):
                created = datetime.fromisoformat(project.created_at.replace('Z', '+00:00'))
            else:
                created = project.created_at
            text.append(f"  Created:  ", style="dim")
            text.append(f"{created.strftime('%Y-%m-%d %H:%M')}\n", style="")

        if project.updated_at:
            from datetime import datetime
            if isinstance(project.updated_at, str):
                updated = datetime.fromisoformat(project.updated_at.replace('Z', '+00:00'))
            else:
                updated = project.updated_at
            text.append(f"  Updated:  ", style="dim")
            text.append(f"{updated.strftime('%Y-%m-%d %H:%M')}\n", style="")

        if project.last_activity:
            rel_time = display_utils.format_relative_time(project.last_activity)
            text.append(f"  Activity: ", style="dim")
            text.append(f"{rel_time}\n", style="bold cyan")

        return Panel(
            text,
            title=f"ℹ️  {project.name}",
            border_style="magenta",
            padding=(1, 2)
        )
