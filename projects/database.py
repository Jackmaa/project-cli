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
    return conn


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
