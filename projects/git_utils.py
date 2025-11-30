"""Git utilities for project management."""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GitStatus:
    """Git status information for a project."""
    is_repo: bool = False
    branch: Optional[str] = None
    uncommitted_changes: int = 0
    ahead: int = 0  # Commits ahead of remote
    behind: int = 0  # Commits behind remote
    has_remote: bool = False
    remote_branch: Optional[str] = None
    error: Optional[str] = None


def is_git_repo(path: Path) -> bool:
    """Check if a path is a git repository."""
    if not path.exists():
        return False

    git_dir = path / ".git"
    return git_dir.exists() and git_dir.is_dir()


def run_git_command(path: Path, *args) -> tuple[bool, str]:
    """
    Run a git command in the specified directory.
    Returns (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(path)] + list(args),
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except FileNotFoundError:
        return False, "Git not installed"
    except Exception as e:
        return False, str(e)


def get_current_branch(path: Path) -> Optional[str]:
    """Get the current branch name."""
    success, output = run_git_command(path, "rev-parse", "--abbrev-ref", "HEAD")
    if success and output:
        return output
    return None


def get_uncommitted_changes(path: Path) -> int:
    """Get count of uncommitted changes (staged + unstaged)."""
    # Get unstaged changes
    success, output = run_git_command(path, "status", "--porcelain")
    if not success:
        return 0

    # Count lines (each line is a changed file)
    return len([line for line in output.split("\n") if line.strip()])


def get_remote_tracking_branch(path: Path, branch: str) -> Optional[str]:
    """Get the remote tracking branch for the current branch."""
    success, output = run_git_command(
        path, "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"
    )
    if success and output:
        return output
    return None


def fetch_remote(path: Path) -> bool:
    """Fetch from remote to update remote tracking branches."""
    success, _ = run_git_command(path, "fetch", "--quiet")
    return success


def get_ahead_behind_counts(path: Path, branch: str, remote_branch: str) -> tuple[int, int]:
    """
    Get commits ahead and behind remote.
    Returns (ahead, behind)
    """
    # Get ahead count
    success, ahead_output = run_git_command(
        path, "rev-list", "--count", f"{remote_branch}..{branch}"
    )
    ahead = int(ahead_output) if success and ahead_output.isdigit() else 0

    # Get behind count
    success, behind_output = run_git_command(
        path, "rev-list", "--count", f"{branch}..{remote_branch}"
    )
    behind = int(behind_output) if success and behind_output.isdigit() else 0

    return ahead, behind


def get_git_status(path: Path, fetch: bool = False) -> GitStatus:
    """
    Get comprehensive git status for a project.

    Args:
        path: Path to the project
        fetch: Whether to fetch from remote first (default: False)

    Returns:
        GitStatus object with all git information
    """
    status = GitStatus()

    if not path or not path.exists():
        status.error = "Path does not exist"
        return status

    if not is_git_repo(path):
        return status

    status.is_repo = True

    # Get current branch
    branch = get_current_branch(path)
    if not branch:
        status.error = "Could not determine branch"
        return status

    status.branch = branch

    # Get uncommitted changes
    status.uncommitted_changes = get_uncommitted_changes(path)

    # Get remote tracking branch
    remote_branch = get_remote_tracking_branch(path, branch)

    if remote_branch:
        status.has_remote = True
        status.remote_branch = remote_branch

        # Fetch from remote if requested
        if fetch:
            fetch_remote(path)

        # Get ahead/behind counts
        ahead, behind = get_ahead_behind_counts(path, branch, remote_branch)
        status.ahead = ahead
        status.behind = behind

    return status


def get_recent_commits(path: Path, limit: int = 5) -> list[dict[str, str]]:
    """Get recent commits for a repository.

    Returns list of dicts with keys: hash, date, author, message
    """
    if not is_git_repo(path):
        return []

    git_format = "--pretty=format:%h|%ar|%an|%s"
    success, output = run_git_command(path, "log", git_format, f"-{limit}")

    if not success or not output.strip():
        return []

    commits = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", maxsplit=3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "author": parts[2],
                "message": parts[3]
            })

    return commits


def get_git_status_summary(status: GitStatus) -> str:
    """
    Get a human-readable summary of git status.

    Examples:
        "main ✓" - On main, up to date
        "dev ↑2" - On dev, 2 commits ahead
        "main ↓3" - On main, 3 commits behind
        "feature ↑1↓2" - On feature, 1 ahead, 2 behind
        "main *3" - On main, 3 uncommitted changes
        "dev ↑1*2" - On dev, 1 ahead, 2 uncommitted
    """
    if not status.is_repo:
        return "-"

    if status.error:
        return "⚠️"

    parts = [status.branch or "?"]

    # Add ahead/behind indicators
    if status.has_remote:
        if status.ahead > 0:
            parts.append(f"↑{status.ahead}")
        if status.behind > 0:
            parts.append(f"↓{status.behind}")
        if status.ahead == 0 and status.behind == 0:
            parts.append("✓")

    # Add uncommitted changes indicator
    if status.uncommitted_changes > 0:
        parts.append(f"*{status.uncommitted_changes}")

    return " ".join(parts)
