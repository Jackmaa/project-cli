"""Scan directory modal for bulk importing git repositories."""

import subprocess
from pathlib import Path
from datetime import datetime
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Checkbox
from textual.binding import Binding

from .base_modal import BaseModal
from ... import database as db


class ScanModal(BaseModal):
    """Modal for scanning directories for git repositories."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "scan", "Scan"),
    ]

    def __init__(self):
        super().__init__(title="Scan Directory for Git Repos", width=80, height=35)
        self.found_repos = []
        self.scanning = False

    def compose_body(self):
        """Compose the modal body with input fields."""
        yield Static("Directory to scan:", classes="field-label")
        yield Input(
            placeholder="e.g., ~/projects or ~/Development",
            id="directory-input"
        )

        yield Static("\nMax depth (optional, leave empty for unlimited):", classes="field-label")
        yield Input(placeholder="e.g., 2", id="depth-input")

        with Horizontal(id="scan-controls"):
            yield Button("Scan", variant="primary", id="scan-btn")
            yield Button("Import Selected", variant="success", id="import-btn", disabled=True)

        yield Static("\n", id="status-message")

        with ScrollableContainer(id="repos-container"):
            yield Static("Scan a directory to find git repositories", classes="dim")

    def compose_buttons(self):
        """Compose modal buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button("Close", variant="default", id="cancel-btn")

    async def on_mount(self):
        """Focus the directory input when modal opens."""
        directory_input = self.query_one("#directory-input", Input)
        directory_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "scan-btn":
            self._scan_directory()
        elif event.button.id == "import-btn":
            self._import_selected()
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def _scan_directory_recursive(self, base_path: Path, max_depth: int | None = None) -> list[Path]:
        """Find all git repositories in a directory."""
        repos = []

        def walk(path: Path, depth: int):
            if max_depth and depth > max_depth:
                return

            if not path.is_dir():
                return

            # If it's a git repo, add it and don't descend deeper
            if self._is_git_repo(path):
                repos.append(path)
                return

            # Otherwise continue searching
            try:
                for child in path.iterdir():
                    if child.is_dir() and not child.name.startswith('.'):
                        walk(child, depth + 1)
            except PermissionError:
                pass  # Ignore inaccessible directories

        walk(base_path, 0)
        return repos

    def _is_git_repo(self, path: Path) -> bool:
        """Check if a directory is a git repository."""
        return (path / ".git").exists()

    def _detect_language(self, path: Path) -> str | None:
        """Detect the primary language in a project directory."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript",
            ".tsx": "TypeScript",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".dart": "Dart",
            ".vue": "Vue",
            ".html": "HTML",
            ".css": "CSS",
            ".sh": "Shell",
        }

        extension_counts = {}

        try:
            for file in path.rglob("*"):
                if file.is_file():
                    ext = file.suffix.lower()
                    if ext in language_map:
                        extension_counts[ext] = extension_counts.get(ext, 0) + 1
        except PermissionError:
            pass

        if extension_counts:
            most_common_ext = max(extension_counts, key=extension_counts.get)
            return language_map[most_common_ext]

        return None

    def _get_last_git_activity(self, path: Path) -> datetime | None:
        """Get the date of the last commit in a git repository."""
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "log", "-1", "--format=%ct"],
                capture_output=True,
                text=True,
                check=True,
            )
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp)
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
            return None

    def _scan_directory(self):
        """Scan the directory for git repositories."""
        directory_str = self.query_one("#directory-input", Input).value.strip()
        depth_str = self.query_one("#depth-input", Input).value.strip()

        # Validate directory
        if not directory_str:
            self.notify("Please enter a directory to scan", severity="error")
            return

        base_path = Path(directory_str).expanduser().resolve()
        if not base_path.exists():
            self.notify(f"Directory does not exist: {directory_str}", severity="error")
            return

        if not base_path.is_dir():
            self.notify(f"Not a directory: {directory_str}", severity="error")
            return

        # Parse depth
        max_depth = None
        if depth_str:
            try:
                max_depth = int(depth_str)
            except ValueError:
                self.notify("Depth must be a number", severity="error")
                return

        # Update status
        status_msg = self.query_one("#status-message", Static)
        status_msg.update(f"Scanning {base_path}...")
        self.notify("Scanning for git repositories...", severity="information")

        # Scan
        repos = self._scan_directory_recursive(base_path, max_depth)

        if not repos:
            status_msg.update("No git repositories found.")
            self._clear_repos_list()
            return

        # Store found repos
        self.found_repos = []
        for repo_path in repos:
            name = repo_path.name
            language = self._detect_language(repo_path)
            last_activity = self._get_last_git_activity(repo_path)

            # Check if already exists
            existing = db.get_project(name)

            self.found_repos.append({
                "path": repo_path,
                "name": name,
                "language": language,
                "last_activity": last_activity,
                "exists": existing is not None,
            })

        # Update UI
        status_msg.update(f"Found {len(repos)} git repositories")
        self._display_repos()

        # Enable import button
        import_btn = self.query_one("#import-btn", Button)
        import_btn.disabled = False

    def _clear_repos_list(self):
        """Clear the repos container."""
        container = self.query_one("#repos-container")
        container.remove_children()
        container.mount(Static("Scan a directory to find git repositories", classes="dim"))

    def _display_repos(self):
        """Display found repositories with checkboxes."""
        container = self.query_one("#repos-container")
        container.remove_children()

        for i, repo in enumerate(self.found_repos):
            # Create checkbox for each repo
            lang_str = f"[{repo['language']}]" if repo['language'] else "[unknown]"
            status_str = " (already exists)" if repo['exists'] else ""

            checkbox = Checkbox(
                f"{repo['name']} {lang_str}{status_str}",
                value=not repo['exists'],  # Auto-select new repos
                id=f"repo-{i}"
            )
            container.mount(checkbox)

    def _import_selected(self):
        """Import the selected repositories."""
        # Get selected repos
        selected_repos = []
        for i, repo in enumerate(self.found_repos):
            try:
                checkbox = self.query_one(f"#repo-{i}", Checkbox)
                if checkbox.value and not repo['exists']:
                    selected_repos.append(repo)
            except Exception:
                continue

        if not selected_repos:
            self.notify("No new repositories selected", severity="warning")
            return

        # Import repos
        imported = 0
        for repo in selected_repos:
            success = db.add_project(
                name=repo['name'],
                path=str(repo['path']),
                language=repo['language'],
                last_activity=repo['last_activity'],
            )
            if success:
                imported += 1

        self.notify(f"Imported {imported} project(s)", severity="information")
        self.dismiss(True)

    def action_scan(self):
        """Handle Ctrl+S keybinding."""
        self._scan_directory()
