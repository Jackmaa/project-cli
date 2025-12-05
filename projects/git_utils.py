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


# ============================================================================
# BRANCH OPERATIONS
# ============================================================================

def get_all_branches(path: Path, include_remote: bool = True) -> list[dict]:
    """
    Get all branches (local and optionally remote).

    Args:
        path: Path to git repository
        include_remote: Include remote branches

    Returns:
        List of dicts with keys: name, is_current, is_remote, last_commit_hash, last_commit_date
    """
    if not is_git_repo(path):
        return []

    # Get all branches with verbose info
    args = ["branch", "-v", "--format=%(refname:short)|%(HEAD)|%(objectname:short)|%(committerdate:iso)"]
    if include_remote:
        args.insert(1, "-a")

    success, output = run_git_command(path, *args)
    if not success or not output:
        return []

    branches = []
    for line in output.split("\n"):
        if not line.strip():
            continue

        parts = line.split("|")
        if len(parts) >= 4:
            branch_name = parts[0].strip()
            is_current = parts[1].strip() == "*"
            is_remote = branch_name.startswith("remotes/")

            # Clean up remote branch names
            if is_remote:
                branch_name = branch_name.replace("remotes/", "")

            branches.append({
                "name": branch_name,
                "is_current": is_current,
                "is_remote": is_remote,
                "last_commit_hash": parts[2].strip(),
                "last_commit_date": parts[3].strip() if len(parts) > 3 else None,
            })

    return branches


def checkout_branch(path: Path, branch_name: str, create: bool = False) -> tuple[bool, str]:
    """
    Checkout a branch, optionally creating it.

    Args:
        path: Path to git repository
        branch_name: Name of branch to checkout
        create: Create branch if it doesn't exist

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    if create:
        success, output = run_git_command(path, "checkout", "-b", branch_name)
    else:
        success, output = run_git_command(path, "checkout", branch_name)

    if success:
        return True, f"Switched to branch '{branch_name}'"
    else:
        return False, output


def delete_branch(path: Path, branch_name: str, force: bool = False) -> tuple[bool, str]:
    """
    Delete a branch.

    Args:
        path: Path to git repository
        branch_name: Name of branch to delete
        force: Force delete unmerged branch

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    flag = "-D" if force else "-d"
    success, output = run_git_command(path, "branch", flag, branch_name)

    if success:
        return True, f"Deleted branch '{branch_name}'"
    else:
        return False, output


def pull_current_branch(path: Path) -> tuple[bool, str]:
    """
    Pull current branch from remote.

    Args:
        path: Path to git repository

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    success, output = run_git_command(path, "pull")

    if success:
        # Check if already up to date
        if "Already up to date" in output or "Already up-to-date" in output:
            return True, "Already up to date"
        else:
            return True, output
    else:
        return False, output


def push_current_branch(path: Path, set_upstream: bool = False) -> tuple[bool, str]:
    """
    Push current branch to remote.

    Args:
        path: Path to git repository
        set_upstream: Set upstream tracking branch

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    if set_upstream:
        # Get current branch
        branch = get_current_branch(path)
        if not branch:
            return False, "Could not determine current branch"

        success, output = run_git_command(path, "push", "-u", "origin", branch)
    else:
        success, output = run_git_command(path, "push")

    if success:
        return True, output
    else:
        return False, output


# ============================================================================
# STASH OPERATIONS
# ============================================================================

def get_stashes(path: Path) -> list[dict]:
    """
    Get all stashes.

    Args:
        path: Path to git repository

    Returns:
        List of dicts with keys: index, name, branch, created_date
    """
    if not is_git_repo(path):
        return []

    success, output = run_git_command(path, "stash", "list", "--format=%gd|%s|%cr")
    if not success or not output:
        return []

    stashes = []
    for idx, line in enumerate(output.split("\n")):
        if not line.strip():
            continue

        parts = line.split("|", 2)
        if len(parts) >= 2:
            stash_ref = parts[0].strip()  # e.g., "stash@{0}"
            stash_name = parts[1].strip()
            created_date = parts[2].strip() if len(parts) > 2 else "Unknown"

            # Extract branch from stash message if present
            # Format is usually "WIP on <branch>: <hash> <message>" or "On <branch>: <message>"
            branch = None
            if "WIP on " in stash_name:
                branch = stash_name.split("WIP on ")[1].split(":")[0].strip()
            elif "On " in stash_name:
                branch = stash_name.split("On ")[1].split(":")[0].strip()

            stashes.append({
                "index": idx,
                "name": stash_name,
                "branch": branch,
                "created_date": created_date,
            })

    return stashes


def stash_changes(path: Path, message: Optional[str] = None, include_untracked: bool = False) -> tuple[bool, str]:
    """
    Stash current changes.

    Args:
        path: Path to git repository
        message: Optional stash message
        include_untracked: Include untracked files

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    args = ["stash", "push"]

    if include_untracked:
        args.append("-u")

    if message:
        args.extend(["-m", message])

    success, output = run_git_command(path, *args)

    if success:
        if "No local changes to save" in output:
            return True, "No changes to stash"
        else:
            return True, f"Stashed changes"
    else:
        return False, output


def apply_stash(path: Path, stash_index: int = 0) -> tuple[bool, str]:
    """
    Apply a stash without removing it.

    Args:
        path: Path to git repository
        stash_index: Stash index (0 is most recent)

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    stash_ref = f"stash@{{{stash_index}}}"
    success, output = run_git_command(path, "stash", "apply", stash_ref)

    if success:
        return True, f"Applied stash {stash_index}"
    else:
        return False, output


def pop_stash(path: Path, stash_index: int = 0) -> tuple[bool, str]:
    """
    Apply a stash and remove it from the stash list.

    Args:
        path: Path to git repository
        stash_index: Stash index (0 is most recent)

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    stash_ref = f"stash@{{{stash_index}}}"
    success, output = run_git_command(path, "stash", "pop", stash_ref)

    if success:
        return True, f"Popped stash {stash_index}"
    else:
        return False, output


def drop_stash(path: Path, stash_index: int = 0) -> tuple[bool, str]:
    """
    Drop a stash from the stash list.

    Args:
        path: Path to git repository
        stash_index: Stash index (0 is most recent)

    Returns:
        (success, message)
    """
    if not is_git_repo(path):
        return False, "Not a git repository"

    stash_ref = f"stash@{{{stash_index}}}"
    success, output = run_git_command(path, "stash", "drop", stash_ref)

    if success:
        return True, f"Dropped stash {stash_index}"
    else:
        return False, output


# ============================================================================
# TIME TRACKING HELPERS
# ============================================================================

def get_commit_info(path: Path, commit_hash: str) -> Optional[dict]:
    """
    Get information about a specific commit.

    Args:
        path: Path to git repository
        commit_hash: Commit hash

    Returns:
        Dict with keys: hash, message, author, date, branch
    """
    if not is_git_repo(path):
        return None

    # Get commit info
    success, output = run_git_command(
        path, "show", "--format=%H|%s|%an|%ai", "--no-patch", commit_hash
    )
    if not success or not output:
        return None

    parts = output.split("|")
    if len(parts) >= 4:
        # Get branch (if possible)
        branch = get_current_branch(path)

        return {
            "hash": parts[0].strip(),
            "message": parts[1].strip(),
            "author": parts[2].strip(),
            "date": parts[3].strip(),
            "branch": branch,
        }

    return None


def get_last_commit_hash(path: Path) -> Optional[str]:
    """
    Get the hash of the last commit (HEAD).

    Args:
        path: Path to git repository

    Returns:
        Commit hash or None
    """
    if not is_git_repo(path):
        return None

    success, output = run_git_command(path, "rev-parse", "HEAD")
    if success and output:
        return output
    return None
