"""
Migration 001: Add sync and analytics tables.

This migration adds support for:
- Remote repository synchronization (GitHub/GitLab)
- Analytics and health scoring
- Time tracking and work sessions
- Sync queue for rate limiting
"""

import sqlite3
from pathlib import Path


def migrate(conn: sqlite3.Connection) -> None:
    """Run migration to add sync and analytics tables."""
    cursor = conn.cursor()

    # Remote repository sync metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remote_repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER UNIQUE,
            platform TEXT NOT NULL,
            owner TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            remote_url TEXT,
            default_branch TEXT,
            last_synced_at TIMESTAMP,
            sync_enabled BOOLEAN DEFAULT 1,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Cached remote repository metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remote_metrics_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remote_repo_id INTEGER,
            stars INTEGER DEFAULT 0,
            forks INTEGER DEFAULT 0,
            watchers INTEGER DEFAULT 0,
            open_issues INTEGER DEFAULT 0,
            open_prs INTEGER DEFAULT 0,
            language TEXT,
            size_kb INTEGER DEFAULT 0,
            license TEXT,
            description TEXT,
            topics TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            pushed_at TIMESTAMP,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (remote_repo_id) REFERENCES remote_repos(id) ON DELETE CASCADE
        )
    """)

    # CI/CD pipeline status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remote_repo_id INTEGER,
            pipeline_name TEXT,
            status TEXT,
            branch TEXT,
            commit_sha TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            url TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (remote_repo_id) REFERENCES remote_repos(id) ON DELETE CASCADE
        )
    """)

    # Work sessions for time tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds INTEGER,
            session_type TEXT DEFAULT 'manual',
            notes TEXT,
            tags TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Commit analytics (aggregated from git history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commit_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            date DATE,
            commit_count INTEGER DEFAULT 0,
            lines_added INTEGER DEFAULT 0,
            lines_removed INTEGER DEFAULT 0,
            files_changed INTEGER DEFAULT 0,
            authors TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Project health scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            score REAL,
            metrics TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Time allocation goals vs actuals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            week_start_date DATE,
            planned_hours REAL DEFAULT 0,
            actual_hours REAL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Sync queue for rate limiting
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            priority INTEGER DEFAULT 5,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_remote_repos_project_id
        ON remote_repos(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_work_sessions_project_id
        ON work_sessions(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_commit_analytics_project_date
        ON commit_analytics(project_id, date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_health_scores_project_id
        ON health_scores(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sync_queue_status
        ON sync_queue(status, priority)
    """)

    conn.commit()
    print("✓ Migration 001 applied successfully")


def rollback(conn: sqlite3.Connection) -> None:
    """Rollback migration - drop all new tables."""
    cursor = conn.cursor()

    tables = [
        'sync_queue',
        'time_allocations',
        'health_scores',
        'commit_analytics',
        'work_sessions',
        'pipeline_status',
        'remote_metrics_cache',
        'remote_repos'
    ]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    conn.commit()
    print("✓ Migration 001 rolled back successfully")


def check_migration_needed(conn: sqlite3.Connection) -> bool:
    """Check if this migration needs to be run."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='remote_repos'
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
            print("Migration 001 already applied")

    conn.close()
