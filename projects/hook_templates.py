"""Git hook templates for time tracking."""

# Post-commit hook template
# This will be installed in .git/hooks/post-commit in each project
POST_COMMIT_HOOK = """#!/usr/bin/env python3
# Post-commit hook for project-cli time tracking
# DO NOT EDIT - Managed by project-cli

import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration (injected during installation)
PROJECT_ID = {project_id}
DB_PATH = "{db_path}"
PROJECT_PATH = "{project_path}"

def get_commit_info():
    \"\"\"Get info about the commit that just happened.\"\"\"
    try:
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_PATH
        )
        commit_hash = result.stdout.strip()

        # Get commit details
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s|%an|%ai|%D"],
            capture_output=True, text=True, cwd=PROJECT_PATH
        )
        parts = result.stdout.strip().split('|')

        message = parts[0] if len(parts) > 0 else "No message"
        author = parts[1] if len(parts) > 1 else "Unknown"
        date = parts[2] if len(parts) > 2 else datetime.now().isoformat()
        refs = parts[3] if len(parts) > 3 else ""

        # Extract branch name from refs
        branch = "main"
        if refs:
            # Parse refs like "HEAD -> main, origin/main"
            ref_parts = refs.split(',')
            for ref in ref_parts:
                if '->' in ref:
                    branch = ref.split('->')[1].strip()
                    break
                elif ref.strip() and not ref.startswith('tag:'):
                    branch = ref.strip()
                    break

        return commit_hash, message, author, date, branch
    except Exception as e:
        print(f"Error getting commit info: {{e}}", file=sys.stderr)
        return None, None, None, None, None

def prompt_for_time():
    \"\"\"Prompt user for time spent on this commit.\"\"\"
    print("\\n" + "="*60)
    print("Time Tracking - How long did this commit take?")
    print("="*60)
    print("Enter time in minutes (or press Enter to skip): ", end='', flush=True)

    try:
        # Try to read from /dev/tty for truly interactive input
        # This works even when git hooks redirect stdin/stdout
        try:
            with open('/dev/tty', 'r') as tty:
                time_input = tty.readline().strip()
        except (OSError, IOError):
            # Fall back to regular input if /dev/tty not available
            time_input = input().strip()

        if not time_input:
            return None
        return int(time_input)
    except (ValueError, KeyboardInterrupt, EOFError):
        print()
        return None

def log_time(commit_hash, commit_message, author, commit_date, branch, time_minutes):
    \"\"\"Log time to database.\"\"\"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(\"\"\"
            INSERT OR IGNORE INTO commit_time_logs
            (project_id, commit_hash, commit_message, commit_date,
             time_spent_minutes, author, branch)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        \"\"\", (PROJECT_ID, commit_hash, commit_message, commit_date,
              time_minutes, author, branch))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error logging time: {{e}}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # Get commit info
    commit_hash, message, author, date, branch = get_commit_info()

    if not commit_hash:
        # Failed to get commit info, exit silently
        sys.exit(0)

    # Prompt for time
    time_minutes = prompt_for_time()

    if time_minutes is not None and time_minutes > 0:
        if log_time(commit_hash, message, author, date, branch, time_minutes):
            print(f"✓ Logged {{time_minutes}} minutes for this commit")
        else:
            print("✗ Failed to log time", file=sys.stderr)
    else:
        print("Skipped time tracking")

    print("="*60 + "\\n")
"""


def get_post_commit_hook(project_id: int, db_path: str, project_path: str) -> str:
    """
    Get the post-commit hook with injected configuration.

    Args:
        project_id: Project ID from database
        db_path: Path to SQLite database
        project_path: Path to project directory

    Returns:
        Complete hook script ready to install
    """
    return POST_COMMIT_HOOK.format(
        project_id=project_id,
        db_path=db_path,
        project_path=project_path
    )
