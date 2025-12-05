"""Git hook installation and management."""

import os
import stat
from pathlib import Path
from typing import Optional, Tuple

from . import hook_templates
from . import database as db


# Marker to identify our hooks
HOOK_MARKER = "# DO NOT EDIT - Managed by project-cli"


def install_hooks(project_path: Path, project_id: int, db_path: Path) -> Tuple[bool, str]:
    """
    Install post-commit hook for time tracking.

    Args:
        project_path: Path to project directory
        project_id: Project ID from database
        db_path: Path to SQLite database

    Returns:
        (success, message)
    """
    # Check if it's a git repo
    git_dir = project_path / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return False, "Not a git repository"

    # Create hooks directory if it doesn't exist
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Path to post-commit hook
    hook_path = hooks_dir / "post-commit"

    # Check if hook already exists and is not ours
    if hook_path.exists():
        try:
            existing_content = hook_path.read_text()
            if HOOK_MARKER not in existing_content:
                return False, f"A post-commit hook already exists at {hook_path}. Please remove or backup before installing."
        except Exception as e:
            return False, f"Error reading existing hook: {e}"

    # Generate hook content
    try:
        hook_content = hook_templates.get_post_commit_hook(
            project_id=project_id,
            db_path=str(db_path),
            project_path=str(project_path)
        )

        # Write hook file
        hook_path.write_text(hook_content)

        # Make executable
        current_permissions = hook_path.stat().st_mode
        hook_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Update database
        db.mark_hooks_installed(project_id, True)

        return True, f"Installed time tracking hook at {hook_path}"

    except Exception as e:
        return False, f"Error installing hook: {e}"


def uninstall_hooks(project_path: Path, project_id: int) -> Tuple[bool, str]:
    """
    Uninstall post-commit hook for time tracking.

    Args:
        project_path: Path to project directory
        project_id: Project ID from database

    Returns:
        (success, message)
    """
    # Check if it's a git repo
    git_dir = project_path / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return False, "Not a git repository"

    # Path to post-commit hook
    hook_path = git_dir / "hooks" / "post-commit"

    if not hook_path.exists():
        # Update database anyway
        db.mark_hooks_installed(project_id, False)
        return True, "No hook to uninstall"

    # Check if it's our hook
    try:
        existing_content = hook_path.read_text()
        if HOOK_MARKER not in existing_content:
            return False, f"Hook at {hook_path} is not managed by project-cli. Please remove manually."

        # Remove the hook
        hook_path.unlink()

        # Update database
        db.mark_hooks_installed(project_id, False)

        return True, f"Uninstalled time tracking hook from {hook_path}"

    except Exception as e:
        return False, f"Error uninstalling hook: {e}"


def check_hooks_installed(project_path: Path) -> bool:
    """
    Check if hooks are installed for a project.

    Args:
        project_path: Path to project directory

    Returns:
        True if hooks are installed and valid
    """
    # Check if it's a git repo
    git_dir = project_path / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return False

    # Path to post-commit hook
    hook_path = git_dir / "hooks" / "post-commit"

    if not hook_path.exists():
        return False

    # Check if it's our hook and executable
    try:
        existing_content = hook_path.read_text()
        is_ours = HOOK_MARKER in existing_content

        # Check if executable
        is_executable = os.access(hook_path, os.X_OK)

        return is_ours and is_executable

    except Exception:
        return False


def get_hook_status(project_path: Path, project_id: int) -> dict:
    """
    Get detailed hook status for a project.

    Args:
        project_path: Path to project directory
        project_id: Project ID from database

    Returns:
        Dictionary with status information
    """
    git_dir = project_path / ".git"
    is_git_repo = git_dir.exists() and git_dir.is_dir()

    if not is_git_repo:
        return {
            "is_git_repo": False,
            "hooks_installed": False,
            "hook_exists": False,
            "hook_valid": False,
            "hook_executable": False,
            "db_status": False,
        }

    hook_path = git_dir / "hooks" / "post-commit"
    hook_exists = hook_path.exists()

    hook_valid = False
    hook_executable = False

    if hook_exists:
        try:
            existing_content = hook_path.read_text()
            hook_valid = HOOK_MARKER in existing_content
            hook_executable = os.access(hook_path, os.X_OK)
        except Exception:
            pass

    # Check database status
    db_status = db.is_hooks_installed(project_id)

    hooks_installed = hook_valid and hook_executable

    return {
        "is_git_repo": is_git_repo,
        "hooks_installed": hooks_installed,
        "hook_exists": hook_exists,
        "hook_valid": hook_valid,
        "hook_executable": hook_executable,
        "db_status": db_status,
        "in_sync": (hooks_installed == db_status),
    }
