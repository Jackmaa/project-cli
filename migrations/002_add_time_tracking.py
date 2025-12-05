"""
Migration 002: Add time tracking and git cache tables.

This migration adds support for:
- Per-commit time tracking with git hooks
- Project-level settings (auto-refresh, hooks installed)
- Branch and stash caching for TUI performance
"""

import sqlite3
from pathlib import Path


def migrate(conn: sqlite3.Connection) -> None:
    """Run migration to add time tracking and git cache tables."""
    cursor = conn.cursor()

    # Add columns to projects table for new settings
    try:
        cursor.execute("""
            ALTER TABLE projects ADD COLUMN auto_refresh_enabled BOOLEAN DEFAULT 0
        """)
    except sqlite3.OperationalError:
        # Column already exists
        pass

    try:
        cursor.execute("""
            ALTER TABLE projects ADD COLUMN hooks_installed BOOLEAN DEFAULT 0
        """)
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Commit time logs - per-commit time tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commit_time_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            commit_hash TEXT NOT NULL,
            commit_message TEXT,
            commit_date TIMESTAMP NOT NULL,
            time_spent_minutes INTEGER NOT NULL,
            author TEXT,
            branch TEXT,
            tags TEXT,
            notes TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            UNIQUE(project_id, commit_hash)
        )
    """)

    # Git branches cache - for branch switcher UI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS git_branches_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            is_current BOOLEAN DEFAULT 0,
            is_remote BOOLEAN DEFAULT 0,
            last_commit_hash TEXT,
            last_commit_date TIMESTAMP,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Git stashes cache - for stash manager UI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS git_stashes_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            stash_index INTEGER NOT NULL,
            stash_name TEXT NOT NULL,
            branch TEXT,
            created_date TIMESTAMP,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_commit_time_logs_project_id
        ON commit_time_logs(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_commit_time_logs_date
        ON commit_time_logs(commit_date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_git_branches_cache_project_id
        ON git_branches_cache(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_git_stashes_cache_project_id
        ON git_stashes_cache(project_id)
    """)

    conn.commit()
    print("✓ Migration 002 applied successfully")


def rollback(conn: sqlite3.Connection) -> None:
    """Rollback migration - drop all new tables and columns."""
    cursor = conn.cursor()

    # Drop tables
    tables = [
        'git_stashes_cache',
        'git_branches_cache',
        'commit_time_logs'
    ]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # Note: SQLite doesn't support dropping columns easily
    # So we'll leave the project columns in place
    # This is acceptable as they default to 0 and won't break anything

    conn.commit()
    print("✓ Migration 002 rolled back successfully")


def check_migration_needed(conn: sqlite3.Connection) -> bool:
    """Check if this migration needs to be run."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='commit_time_logs'
    """)
    return cursor.fetchone() is None


if __name__ == "__main__":
    # Test migration script
    import sys
    from pathlib import Path

    # Use test database
    test_db = Path.home() / ".config" / "project-cli" / "test.db"
    test_db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(test_db)

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback(conn)
    else:
        if check_migration_needed(conn):
            migrate(conn)
        else:
            print("Migration 002 already applied")

    conn.close()
