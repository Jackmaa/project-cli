"""Database layer for projects management."""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import Project


# Emplacement de la base de donn�es
DB_DIR = Path.home() / ".config" / "project-cli"
DB_PATH = DB_DIR / "projects.db"


def init_db() -> sqlite3.Connection:
    """Initialize database and create tables if they don't exist."""
    # Cr�er le dossier de config si besoin
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table projects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            path TEXT,
            description TEXT,
            status TEXT DEFAULT 'active',
            priority TEXT DEFAULT 'medium',
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP
        )
    """)

    # Table tags
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            tag TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Table activity_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Table git_status_cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS git_status_cache (
            project_id INTEGER PRIMARY KEY,
            is_repo BOOLEAN NOT NULL DEFAULT 0,
            branch TEXT,
            uncommitted_changes INTEGER DEFAULT 0,
            ahead INTEGER DEFAULT 0,
            behind INTEGER DEFAULT 0,
            has_remote BOOLEAN DEFAULT 0,
            remote_branch TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Run migrations
    _run_migrations(conn)

    return conn


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Run database migrations if needed."""
    import importlib.util
    from pathlib import Path as MigrationPath

    # Get migrations directory
    migrations_dir = MigrationPath(__file__).parent.parent / "migrations"

    if not migrations_dir.exists():
        return

    # Get all migration files
    migration_files = sorted(migrations_dir.glob("*.py"))

    for migration_file in migration_files:
        if migration_file.name.startswith("__"):
            continue

        # Load migration module
        spec = importlib.util.spec_from_file_location(
            f"migrations.{migration_file.stem}",
            migration_file
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if migration is needed
            if hasattr(module, 'check_migration_needed'):
                if module.check_migration_needed(conn):
                    # Run migration silently
                    if hasattr(module, 'migrate'):
                        module.migrate(conn)


def add_project(
    name: str,
    description: Optional[str] = None,
    path: Optional[str] = None,
    priority: str = "medium",
    language: Optional[str] = None,
    tags: Optional[List[str]] = None,
    last_activity: Optional[datetime] = None,
) -> bool:
    """Add a new project to the database."""
    conn = init_db()
    cursor = conn.cursor()

    try:
        # Ins�rer le projet
        cursor.execute(
            """
            INSERT INTO projects (name, description, path, priority, language, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, path, priority, language, last_activity),
        )
        project_id = cursor.lastrowid

        # Ajouter les tags
        if tags:
            for tag in tags:
                cursor.execute(
                    "INSERT INTO tags (project_id, tag) VALUES (?, ?)",
                    (project_id, tag),
                )

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Le projet existe d�j�
        return False
    finally:
        conn.close()


def get_all_projects(
    status: Optional[str] = None, tag: Optional[str] = None
) -> List[Project]:
    """Get all projects, optionally filtered by status or tag."""
    conn = init_db()
    cursor = conn.cursor()

    # Query de base
    query = """
        SELECT DISTINCT p.id, p.name, p.path, p.description, p.status, p.priority,
               p.language, p.created_at, p.updated_at, p.last_activity
        FROM projects p
    """

    params = []

    # Filtrer par tag si demand�
    if tag:
        query += " JOIN tags t ON p.id = t.project_id WHERE t.tag = ?"
        params.append(tag)

    # Filtrer par statut
    if status:
        if tag:
            query += " AND p.status = ?"
        else:
            query += " WHERE p.status = ?"
        params.append(status)

    query += " ORDER BY p.updated_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    projects = []
    for row in rows:
        # R�cup�rer les tags pour ce projet
        cursor.execute("SELECT tag FROM tags WHERE project_id = ?", (row[0],))
        tags = [t[0] for t in cursor.fetchall()]

        # Récupérer le git status depuis le cache
        git_status = get_git_status_cache(row[0])

        projects.append(
            Project(
                id=row[0],
                name=row[1],
                path=row[2],
                description=row[3],
                status=row[4],
                priority=row[5],
                language=row[6],
                created_at=row[7],
                updated_at=row[8],
                last_activity=row[9],
                tags=tags,
                git_status=git_status,
            )
        )

    conn.close()
    return projects


def get_project(name: str) -> Optional[Project]:
    """Get a single project by name."""
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, path, description, status, priority, language,
               created_at, updated_at, last_activity
        FROM projects WHERE name = ?
        """,
        (name,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    # R�cup�rer les tags
    cursor.execute("SELECT tag FROM tags WHERE project_id = ?", (row[0],))
    tags = [t[0] for t in cursor.fetchall()]

    # Récupérer le git status depuis le cache
    git_status = get_git_status_cache(row[0])

    project = Project(
        id=row[0],
        name=row[1],
        path=row[2],
        description=row[3],
        status=row[4],
        priority=row[5],
        language=row[6],
        created_at=row[7],
        updated_at=row[8],
        last_activity=row[9],
        tags=tags,
        git_status=git_status,
    )

    conn.close()
    return project


def get_project_by_id(project_id: int) -> Optional[Project]:
    """Get a single project by ID."""
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, path, description, status, priority, language,
               created_at, updated_at, last_activity
        FROM projects WHERE id = ?
        """,
        (project_id,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    # Récupérer les tags
    cursor.execute("SELECT tag FROM tags WHERE project_id = ?", (row[0],))
    tags = [t[0] for t in cursor.fetchall()]

    # Récupérer le git status depuis le cache
    git_status = get_git_status_cache(row[0])

    project = Project(
        id=row[0],
        name=row[1],
        path=row[2],
        description=row[3],
        status=row[4],
        priority=row[5],
        language=row[6],
        created_at=row[7],
        updated_at=row[8],
        last_activity=row[9],
        tags=tags,
        git_status=git_status,
    )

    conn.close()
    return project


def update_project_status(name: str, status: str) -> bool:
    """Update the status of a project."""
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE projects
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            """,
            (status, name),
        )
        conn.commit()
        success = cursor.rowcount > 0
    finally:
        conn.close()

    return success


def delete_project(name: str) -> bool:
    """Delete a project by name."""
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM projects WHERE name = ?", (name,))
        conn.commit()
        success = cursor.rowcount > 0
    finally:
        conn.close()

    return success


def get_stats() -> dict:
    """Get statistics about all projects."""
    conn = init_db()
    cursor = conn.cursor()

    # Total projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    total = cursor.fetchone()[0]

    # By status
    cursor.execute(
        """
        SELECT status, COUNT(*) FROM projects GROUP BY status
        """
    )
    by_status = dict(cursor.fetchall())

    # By priority
    cursor.execute(
        """
        SELECT priority, COUNT(*) FROM projects GROUP BY priority
        """
    )
    by_priority = dict(cursor.fetchall())

    # Oldest stale project (sans activit�)
    cursor.execute(
        """
        SELECT name, last_activity FROM projects
        WHERE last_activity IS NOT NULL AND status = 'active'
        ORDER BY last_activity ASC LIMIT 1
        """
    )
    stale = cursor.fetchone()

    conn.close()

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "oldest_stale": stale,
    }


def add_tags(name: str, tags: List[str]) -> bool:
    """Add tags to a project."""
    conn = init_db()
    cursor = conn.cursor()

    # Récupérer l'ID du projet
    cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False

    project_id = result[0]

    # Ajouter chaque tag s'il n'existe pas déjà
    for tag in tags:
        cursor.execute(
            """
            INSERT OR IGNORE INTO tags (project_id, tag)
            SELECT ?, ? WHERE NOT EXISTS (
                SELECT 1 FROM tags WHERE project_id = ? AND tag = ?
            )
            """,
            (project_id, tag, project_id, tag),
        )

    conn.commit()
    conn.close()
    return True


def remove_tags(name: str, tags: List[str]) -> bool:
    """Remove tags from a project."""
    conn = init_db()
    cursor = conn.cursor()

    # Récupérer l'ID du projet
    cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False

    project_id = result[0]

    # Supprimer les tags
    for tag in tags:
        cursor.execute(
            "DELETE FROM tags WHERE project_id = ? AND tag = ?",
            (project_id, tag),
        )

    conn.commit()
    conn.close()
    return True


def update_project_field(name: str, field: str, value) -> bool:
    """Update a specific field of a project."""
    conn = init_db()
    cursor = conn.cursor()

    # Liste des champs autorisés
    allowed_fields = ["name", "description", "priority", "status", "language", "path"]

    if field not in allowed_fields:
        conn.close()
        return False

    try:
        query = f"UPDATE projects SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?"
        cursor.execute(query, (value, name))
        conn.commit()
        success = cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Erreur si le nouveau nom existe déjà
        success = False
    finally:
        conn.close()

    return success


def add_log_entry(name: str, message: str) -> bool:
    """Add an activity log entry for a project."""
    conn = init_db()
    cursor = conn.cursor()

    # Récupérer l'ID du projet
    cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False

    project_id = result[0]

    # Ajouter l'entrée de log
    cursor.execute(
        "INSERT INTO activity_logs (project_id, message) VALUES (?, ?)",
        (project_id, message),
    )

    # Mettre à jour le timestamp du projet
    cursor.execute(
        "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (project_id,),
    )

    conn.commit()
    conn.close()
    return True


def get_project_logs(name: str, limit: int = 20) -> list:
    """Get activity logs for a specific project."""
    conn = init_db()
    cursor = conn.cursor()

    # Récupérer l'ID du projet
    cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return []

    project_id = result[0]

    # Récupérer les logs
    cursor.execute(
        """
        SELECT message, timestamp
        FROM activity_logs
        WHERE project_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (project_id, limit),
    )

    logs = [
        {"project_name": name, "message": row[0], "timestamp": row[1]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return logs


def get_all_logs(limit: int = 20) -> list:
    """Get activity logs for all projects."""
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.name, l.message, l.timestamp
        FROM activity_logs l
        JOIN projects p ON l.project_id = p.id
        ORDER BY l.timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )

    logs = [
        {"project_name": row[0], "message": row[1], "timestamp": row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return logs


def save_git_status_cache(project_id: int, git_status: dict) -> None:
    """Save git status to cache."""
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO git_status_cache
        (project_id, is_repo, branch, uncommitted_changes, ahead, behind, has_remote, remote_branch, cached_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            project_id,
            git_status.get("is_repo", False),
            git_status.get("branch"),
            git_status.get("uncommitted_changes", 0),
            git_status.get("ahead", 0),
            git_status.get("behind", 0),
            git_status.get("has_remote", False),
            git_status.get("remote_branch"),
        ),
    )

    conn.commit()
    conn.close()


def get_git_status_cache(project_id: int, ttl_minutes: int = 5) -> Optional[dict]:
    """
    Get git status from cache if still valid.

    Args:
        project_id: Project ID
        ttl_minutes: Cache TTL in minutes (default: 5)

    Returns:
        Git status dict if cache is valid, None otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT is_repo, branch, uncommitted_changes, ahead, behind, has_remote, remote_branch, cached_at
        FROM git_status_cache
        WHERE project_id = ?
        AND datetime(cached_at, '+' || ? || ' minutes') > datetime('now')
        """,
        (project_id, ttl_minutes),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "is_repo": bool(row[0]),
        "branch": row[1],
        "uncommitted_changes": row[2],
        "ahead": row[3],
        "behind": row[4],
        "has_remote": bool(row[5]),
        "remote_branch": row[6],
        "cached_at": row[7],
    }


def clear_git_status_cache(project_id: Optional[int] = None) -> None:
    """
    Clear git status cache.

    Args:
        project_id: If specified, clear cache for this project only.
                   If None, clear all cache.
    """
    conn = init_db()
    cursor = conn.cursor()

    if project_id:
        cursor.execute("DELETE FROM git_status_cache WHERE project_id = ?", (project_id,))
    else:
        cursor.execute("DELETE FROM git_status_cache")

    conn.commit()
    conn.close()


def update_git_status_for_project(project: Project, fetch: bool = False) -> None:
    """
    Update git status cache for a project by checking the actual git repo.

    Args:
        project: Project to update git status for
        fetch: Whether to fetch from remote (default: False)
    """
    from pathlib import Path
    from . import git_utils

    if not project.path:
        return

    path = Path(project.path)
    git_status = git_utils.get_git_status(path, fetch=fetch)

    # Convert GitStatus dataclass to dict
    status_dict = {
        "is_repo": git_status.is_repo,
        "branch": git_status.branch,
        "uncommitted_changes": git_status.uncommitted_changes,
        "ahead": git_status.ahead,
        "behind": git_status.behind,
        "has_remote": git_status.has_remote,
        "remote_branch": git_status.remote_branch,
    }

    save_git_status_cache(project.id, status_dict)


# =============================================================================
# Remote Repository Sync Functions
# =============================================================================

def enable_sync_for_project(
    project_id: int,
    platform: str,
    owner: str,
    repo_name: str,
    remote_url: str,
    default_branch: str = "main"
) -> bool:
    """
    Enable sync by storing remote info in remote_repos table.

    Args:
        project_id: Project ID
        platform: Platform name ('github' or 'gitlab')
        owner: Repository owner/username
        repo_name: Repository name
        remote_url: Full remote URL
        default_branch: Default branch name

    Returns:
        True if successful, False otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO remote_repos
            (project_id, platform, owner, repo_name, remote_url, default_branch, sync_enabled)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (project_id, platform, owner, repo_name, remote_url, default_branch))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error enabling sync: {e}")
        return False
    finally:
        conn.close()


def disable_sync_for_project(project_id: int, delete_cache: bool = False) -> bool:
    """
    Disable sync (set sync_enabled=0), optionally delete cached data.

    Args:
        project_id: Project ID
        delete_cache: Whether to delete cached metrics data

    Returns:
        True if successful, False otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        if delete_cache:
            # Delete cached data
            cursor.execute("""
                DELETE FROM remote_metrics_cache
                WHERE remote_repo_id IN (
                    SELECT id FROM remote_repos WHERE project_id = ?
                )
            """, (project_id,))

            cursor.execute("""
                DELETE FROM pipeline_status
                WHERE remote_repo_id IN (
                    SELECT id FROM remote_repos WHERE project_id = ?
                )
            """, (project_id,))

            # Delete remote_repos entry
            cursor.execute("DELETE FROM remote_repos WHERE project_id = ?", (project_id,))
        else:
            # Just disable sync
            cursor.execute("""
                UPDATE remote_repos
                SET sync_enabled = 0
                WHERE project_id = ?
            """, (project_id,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error disabling sync: {e}")
        return False
    finally:
        conn.close()


def get_remote_repo_info(project_id: int) -> Optional[dict]:
    """
    Get remote_repos row for a project.

    Args:
        project_id: Project ID

    Returns:
        Dictionary with remote repo info or None
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, project_id, platform, owner, repo_name, remote_url,
               default_branch, last_synced_at, sync_enabled
        FROM remote_repos
        WHERE project_id = ?
    """, (project_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'id': row[0],
        'project_id': row[1],
        'platform': row[2],
        'owner': row[3],
        'repo_name': row[4],
        'remote_url': row[5],
        'default_branch': row[6],
        'last_synced_at': row[7],
        'sync_enabled': bool(row[8]),
    }


def get_all_sync_enabled_projects() -> List[dict]:
    """
    Get all projects where sync_enabled=1.

    Returns:
        List of dictionaries with project and remote repo info
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.path, r.id as remote_id, r.platform, r.owner, r.repo_name
        FROM projects p
        INNER JOIN remote_repos r ON p.id = r.project_id
        WHERE r.sync_enabled = 1
    """)

    projects = []
    for row in cursor.fetchall():
        projects.append({
            'project_id': row[0],
            'name': row[1],
            'path': row[2],
            'remote_id': row[3],
            'platform': row[4],
            'owner': row[5],
            'repo_name': row[6],
        })

    conn.close()
    return projects


# =============================================================================
# Remote Metrics Cache Functions
# =============================================================================

def save_remote_metrics(remote_repo_id: int, metrics: dict) -> bool:
    """
    Save metrics to remote_metrics_cache table.

    Args:
        remote_repo_id: Remote repository ID
        metrics: Dictionary with metrics data

    Returns:
        True if successful, False otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        import json

        # Delete existing cache for this remote repo
        cursor.execute("DELETE FROM remote_metrics_cache WHERE remote_repo_id = ?", (remote_repo_id,))

        cursor.execute("""
            INSERT INTO remote_metrics_cache
            (remote_repo_id, stars, forks, watchers, open_issues, open_prs,
             language, size_kb, license, description, topics, created_at,
             updated_at, pushed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            remote_repo_id,
            metrics.get('stars', 0),
            metrics.get('forks', 0),
            metrics.get('watchers', 0),
            metrics.get('open_issues', 0),
            metrics.get('open_prs', 0),
            metrics.get('language'),
            metrics.get('size_kb', 0),
            metrics.get('license'),
            metrics.get('description'),
            json.dumps(metrics.get('topics', [])),
            metrics.get('created_at'),
            metrics.get('updated_at'),
            metrics.get('pushed_at'),
        ))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving remote metrics: {e}")
        return False
    finally:
        conn.close()


def get_remote_metrics(remote_repo_id: int, ttl_hours: int = 24) -> Optional[dict]:
    """
    Get cached metrics if still valid (within TTL).

    Args:
        remote_repo_id: Remote repository ID
        ttl_hours: Cache TTL in hours

    Returns:
        Dictionary with metrics or None if not found/expired
    """
    from datetime import datetime, timedelta
    import json

    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stars, forks, watchers, open_issues, open_prs,
               language, size_kb, license, description, topics,
               created_at, updated_at, pushed_at, cached_at
        FROM remote_metrics_cache
        WHERE remote_repo_id = ?
    """, (remote_repo_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # Check TTL
    cached_at = datetime.fromisoformat(row[13]) if row[13] else None
    if cached_at:
        age = datetime.now() - cached_at
        if age > timedelta(hours=ttl_hours):
            return None

    return {
        'stars': row[0],
        'forks': row[1],
        'watchers': row[2],
        'open_issues': row[3],
        'open_prs': row[4],
        'language': row[5],
        'size_kb': row[6],
        'license': row[7],
        'description': row[8],
        'topics': json.loads(row[9]) if row[9] else [],
        'created_at': row[10],
        'updated_at': row[11],
        'pushed_at': row[12],
        'cached_at': row[13],
    }


def get_metrics_for_project(project_id: int) -> Optional[dict]:
    """
    Join remote_repos + remote_metrics_cache for a project.

    Args:
        project_id: Project ID

    Returns:
        Dictionary with metrics or None
    """
    remote_info = get_remote_repo_info(project_id)
    if not remote_info:
        return None

    return get_remote_metrics(remote_info['id'], ttl_hours=999999)  # Don't check TTL here


# =============================================================================
# Pipeline Status Functions
# =============================================================================

def save_pipeline_status(remote_repo_id: int, pipeline_data: dict) -> bool:
    """
    Save GitHub Actions/GitLab CI status to pipeline_status table.

    Args:
        remote_repo_id: Remote repository ID
        pipeline_data: Dictionary with pipeline data

    Returns:
        True if successful, False otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pipeline_status
            (remote_repo_id, pipeline_name, status, branch, commit_sha,
             started_at, completed_at, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            remote_repo_id,
            pipeline_data.get('name', 'Workflow'),
            pipeline_data.get('status'),
            pipeline_data.get('branch'),
            pipeline_data.get('commit_sha'),
            pipeline_data.get('started_at'),
            pipeline_data.get('completed_at'),
            pipeline_data.get('url'),
        ))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving pipeline status: {e}")
        return False
    finally:
        conn.close()


def get_latest_pipeline_status(remote_repo_id: int) -> Optional[dict]:
    """
    Get most recent pipeline status.

    Args:
        remote_repo_id: Remote repository ID

    Returns:
        Dictionary with pipeline status or None
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pipeline_name, status, branch, commit_sha, started_at, completed_at, url
        FROM pipeline_status
        WHERE remote_repo_id = ?
        ORDER BY cached_at DESC
        LIMIT 1
    """, (remote_repo_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'name': row[0],
        'status': row[1],
        'conclusion': row[1],  # For GitHub Actions compatibility
        'branch': row[2],
        'commit_sha': row[3],
        'started_at': row[4],
        'completed_at': row[5],
        'url': row[6],
    }


# =============================================================================
# Sync Metadata Functions
# =============================================================================

def update_last_synced(remote_repo_id: int) -> None:
    """
    Update last_synced_at timestamp.

    Args:
        remote_repo_id: Remote repository ID
    """
    from datetime import datetime

    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE remote_repos
        SET last_synced_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), remote_repo_id))

    conn.commit()
    conn.close()


def update_project_from_remote_metadata(
    project_id: int,
    description: str,
    language: str,
    topics: List[str]
) -> bool:
    """
    Update project description/language/tags from remote data.

    Args:
        project_id: Project ID
        description: Repository description
        language: Primary language
        topics: List of topics/tags

    Returns:
        True if successful, False otherwise
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        # Update project description and language
        cursor.execute("""
            UPDATE projects
            SET description = ?, language = ?
            WHERE id = ?
        """, (description, language, project_id))

        # Delete existing tags and add new ones
        cursor.execute("DELETE FROM tags WHERE project_id = ?", (project_id,))

        for topic in topics:
            cursor.execute("""
                INSERT INTO tags (project_id, tag)
                VALUES (?, ?)
            """, (project_id, topic))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating project metadata: {e}")
        return False
    finally:
        conn.close()


# =============================================================================
# Sync Statistics Functions
# =============================================================================

def get_sync_statistics() -> dict:
    """
    Get sync stats: total enabled, synced in 24h, by platform, etc.

    Returns:
        Dictionary with statistics
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    # Total enabled
    cursor.execute("SELECT COUNT(*) FROM remote_repos WHERE sync_enabled = 1")
    total_enabled = cursor.fetchone()[0]

    # Total sync-capable (all remote repos)
    cursor.execute("SELECT COUNT(*) FROM remote_repos")
    total_repos = cursor.fetchone()[0]

    # Synced in last 24 hours
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    cursor.execute("""
        SELECT COUNT(*) FROM remote_repos
        WHERE last_synced_at > ? AND sync_enabled = 1
    """, (cutoff,))
    synced_24h = cursor.fetchone()[0]

    # By platform
    cursor.execute("""
        SELECT platform, COUNT(*)
        FROM remote_repos
        WHERE sync_enabled = 1
        GROUP BY platform
    """)
    by_platform = {row[0]: row[1] for row in cursor.fetchall()}

    # Never synced
    cursor.execute("""
        SELECT COUNT(*) FROM remote_repos
        WHERE last_synced_at IS NULL AND sync_enabled = 1
    """)
    never_synced = cursor.fetchone()[0]

    conn.close()

    return {
        'total_enabled': total_enabled,
        'total_repos': total_repos,
        'synced_24h': synced_24h,
        'by_platform': by_platform,
        'never_synced': never_synced,
    }


# ============================================================================
# PROJECT SETTINGS (AUTO-REFRESH, HOOKS)
# ============================================================================

def enable_auto_refresh(project_id: int, enabled: bool = True) -> bool:
    """
    Enable or disable auto-refresh for a project.

    Args:
        project_id: Project ID
        enabled: True to enable, False to disable

    Returns:
        True if successful
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE projects
            SET auto_refresh_enabled = ?
            WHERE id = ?
        """, (1 if enabled else 0, project_id))
        conn.commit()
        success = cursor.rowcount > 0
    finally:
        conn.close()

    return success


def is_auto_refresh_enabled(project_id: int) -> bool:
    """
    Check if auto-refresh is enabled for a project.

    Args:
        project_id: Project ID

    Returns:
        True if auto-refresh is enabled
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT auto_refresh_enabled FROM projects WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()

    conn.close()
    return bool(row[0]) if row else False


def mark_hooks_installed(project_id: int, installed: bool = True) -> bool:
    """
    Mark hooks as installed or uninstalled for a project.

    Args:
        project_id: Project ID
        installed: True if hooks are installed, False otherwise

    Returns:
        True if successful
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE projects
            SET hooks_installed = ?
            WHERE id = ?
        """, (1 if installed else 0, project_id))
        conn.commit()
        success = cursor.rowcount > 0
    finally:
        conn.close()

    return success


def is_hooks_installed(project_id: int) -> bool:
    """
    Check if hooks are installed for a project.

    Args:
        project_id: Project ID

    Returns:
        True if hooks are installed
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hooks_installed FROM projects WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()

    conn.close()
    return bool(row[0]) if row else False


def get_auto_refresh_projects() -> List[int]:
    """
    Get list of project IDs that have auto-refresh enabled.

    Returns:
        List of project IDs
    """
    conn = init_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM projects WHERE auto_refresh_enabled = 1
    """)
    project_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return project_ids


# ============================================================================
# TIME TRACKING
# ============================================================================

def log_commit_time(
    project_id: int,
    commit_hash: str,
    time_minutes: int,
    commit_message: str,
    author: str,
    branch: str,
    commit_date: str,
    tags: Optional[str] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Log time spent on a commit.

    Args:
        project_id: Project ID
        commit_hash: Git commit hash
        time_minutes: Time spent in minutes
        commit_message: Commit message
        author: Commit author
        branch: Git branch
        commit_date: Commit timestamp
        tags: Optional JSON string of tags
        notes: Optional notes

    Returns:
        True if successful
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO commit_time_logs
            (project_id, commit_hash, commit_message, commit_date,
             time_spent_minutes, author, branch, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, commit_hash, commit_message, commit_date,
              time_minutes, author, branch, tags, notes))
        conn.commit()
        success = cursor.rowcount > 0
    finally:
        conn.close()

    return success


def get_commit_time_logs(project_id: Optional[int] = None, days: int = 30) -> List[dict]:
    """
    Get commit time logs for a project or all projects.

    Args:
        project_id: Optional project ID (None for all projects)
        days: Number of days to look back

    Returns:
        List of dictionaries with commit time data
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    if project_id:
        cursor.execute("""
            SELECT ctl.id, ctl.project_id, p.name, ctl.commit_hash,
                   ctl.commit_message, ctl.commit_date, ctl.time_spent_minutes,
                   ctl.author, ctl.branch, ctl.tags, ctl.notes, ctl.logged_at
            FROM commit_time_logs ctl
            JOIN projects p ON ctl.project_id = p.id
            WHERE ctl.project_id = ? AND ctl.commit_date > ?
            ORDER BY ctl.commit_date DESC
        """, (project_id, cutoff))
    else:
        cursor.execute("""
            SELECT ctl.id, ctl.project_id, p.name, ctl.commit_hash,
                   ctl.commit_message, ctl.commit_date, ctl.time_spent_minutes,
                   ctl.author, ctl.branch, ctl.tags, ctl.notes, ctl.logged_at
            FROM commit_time_logs ctl
            JOIN projects p ON ctl.project_id = p.id
            WHERE ctl.commit_date > ?
            ORDER BY ctl.commit_date DESC
        """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    logs = []
    for row in rows:
        logs.append({
            'id': row[0],
            'project_id': row[1],
            'project_name': row[2],
            'commit_hash': row[3],
            'commit_message': row[4],
            'commit_date': row[5],
            'time_spent_minutes': row[6],
            'author': row[7],
            'branch': row[8],
            'tags': row[9],
            'notes': row[10],
            'logged_at': row[11],
        })

    return logs


def get_time_summary_by_day(project_id: Optional[int] = None, days: int = 30) -> List[dict]:
    """
    Get time summary aggregated by day.

    Args:
        project_id: Optional project ID (None for all projects)
        days: Number of days to look back

    Returns:
        List of dictionaries with daily summaries
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    if project_id:
        cursor.execute("""
            SELECT DATE(SUBSTR(commit_date, 1, 10)) as day,
                   COUNT(*) as commit_count,
                   SUM(time_spent_minutes) as total_minutes
            FROM commit_time_logs
            WHERE project_id = ? AND commit_date > ?
            GROUP BY DATE(SUBSTR(commit_date, 1, 10))
            ORDER BY day DESC
        """, (project_id, cutoff))
    else:
        cursor.execute("""
            SELECT DATE(SUBSTR(commit_date, 1, 10)) as day,
                   COUNT(*) as commit_count,
                   SUM(time_spent_minutes) as total_minutes
            FROM commit_time_logs
            WHERE commit_date > ?
            GROUP BY DATE(SUBSTR(commit_date, 1, 10))
            ORDER BY day DESC
        """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    summaries = []
    for row in rows:
        summaries.append({
            'day': row[0],
            'commit_count': row[1],
            'total_minutes': row[2],
        })

    return summaries


def get_time_summary_by_project(days: int = 30) -> List[dict]:
    """
    Get time summary aggregated by project.

    Args:
        days: Number of days to look back

    Returns:
        List of dictionaries with project summaries
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT p.id, p.name,
               COUNT(*) as commit_count,
               SUM(time_spent_minutes) as total_minutes
        FROM commit_time_logs ctl
        JOIN projects p ON ctl.project_id = p.id
        WHERE ctl.commit_date > ?
        GROUP BY p.id, p.name
        ORDER BY total_minutes DESC
    """, (cutoff,))

    rows = cursor.fetchall()
    conn.close()

    summaries = []
    for row in rows:
        summaries.append({
            'project_id': row[0],
            'project_name': row[1],
            'commit_count': row[2],
            'total_minutes': row[3],
        })

    return summaries


# ============================================================================
# BRANCH AND STASH CACHE
# ============================================================================

def save_branches_cache(project_id: int, branches: List[dict]) -> None:
    """
    Save branches to cache.

    Args:
        project_id: Project ID
        branches: List of branch dictionaries with keys:
                  name, is_current, is_remote, last_commit_hash, last_commit_date
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        # Clear old cache
        cursor.execute("""
            DELETE FROM git_branches_cache WHERE project_id = ?
        """, (project_id,))

        # Insert new cache
        for branch in branches:
            cursor.execute("""
                INSERT INTO git_branches_cache
                (project_id, branch_name, is_current, is_remote,
                 last_commit_hash, last_commit_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                branch['name'],
                1 if branch.get('is_current', False) else 0,
                1 if branch.get('is_remote', False) else 0,
                branch.get('last_commit_hash'),
                branch.get('last_commit_date'),
            ))

        conn.commit()
    finally:
        conn.close()


def get_branches_cache(project_id: int, ttl_minutes: int = 10) -> Optional[List[dict]]:
    """
    Get branches from cache if not stale.

    Args:
        project_id: Project ID
        ttl_minutes: Cache TTL in minutes

    Returns:
        List of branch dictionaries or None if cache is stale
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(minutes=ttl_minutes)).isoformat()

    cursor.execute("""
        SELECT branch_name, is_current, is_remote,
               last_commit_hash, last_commit_date, cached_at
        FROM git_branches_cache
        WHERE project_id = ? AND cached_at > ?
        ORDER BY is_current DESC, branch_name ASC
    """, (project_id, cutoff))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    branches = []
    for row in rows:
        branches.append({
            'name': row[0],
            'is_current': bool(row[1]),
            'is_remote': bool(row[2]),
            'last_commit_hash': row[3],
            'last_commit_date': row[4],
        })

    return branches


def save_stashes_cache(project_id: int, stashes: List[dict]) -> None:
    """
    Save stashes to cache.

    Args:
        project_id: Project ID
        stashes: List of stash dictionaries with keys:
                 index, name, branch, created_date
    """
    conn = init_db()
    cursor = conn.cursor()

    try:
        # Clear old cache
        cursor.execute("""
            DELETE FROM git_stashes_cache WHERE project_id = ?
        """, (project_id,))

        # Insert new cache
        for stash in stashes:
            cursor.execute("""
                INSERT INTO git_stashes_cache
                (project_id, stash_index, stash_name, branch, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_id,
                stash['index'],
                stash['name'],
                stash.get('branch'),
                stash.get('created_date'),
            ))

        conn.commit()
    finally:
        conn.close()


def get_stashes_cache(project_id: int, ttl_minutes: int = 10) -> Optional[List[dict]]:
    """
    Get stashes from cache if not stale.

    Args:
        project_id: Project ID
        ttl_minutes: Cache TTL in minutes

    Returns:
        List of stash dictionaries or None if cache is stale
    """
    from datetime import datetime, timedelta

    conn = init_db()
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(minutes=ttl_minutes)).isoformat()

    cursor.execute("""
        SELECT stash_index, stash_name, branch, created_date, cached_at
        FROM git_stashes_cache
        WHERE project_id = ? AND cached_at > ?
        ORDER BY stash_index ASC
    """, (project_id, cutoff))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    stashes = []
    for row in rows:
        stashes.append({
            'index': row[0],
            'name': row[1],
            'branch': row[2],
            'created_date': row[3],
        })

    return stashes
