"""Queue-based sync system for rate limit management."""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from . import database as db


@dataclass
class SyncQueueItem:
    """Represents an item in the sync queue."""
    id: int
    project_id: int
    priority: int
    requested_at: datetime
    status: str  # 'pending', 'processing', 'completed', 'failed'


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, platform: str):
        """
        Initialize rate limiter.

        Args:
            platform: Platform name ('github' or 'gitlab')
        """
        self.platform = platform
        self.limits = {
            'github': {'calls': 5000, 'window': 3600},  # 5000/hour
            'gitlab': {'calls': 300, 'window': 60},  # 300/minute (future)
        }
        self.calls: List[datetime] = []

    def can_make_request(self, buffer: int = 100) -> bool:
        """
        Check if we can make a request without exceeding limits.

        Args:
            buffer: Number of requests to keep in reserve

        Returns:
            True if request can be made, False otherwise
        """
        if self.platform not in self.limits:
            return True

        limit = self.limits[self.platform]
        now = datetime.now()
        window_start = now - timedelta(seconds=limit['window'])

        # Remove old calls outside window
        self.calls = [c for c in self.calls if c > window_start]

        # Check if we're under limit (with buffer)
        return len(self.calls) < (limit['calls'] - buffer)

    def record_request(self) -> None:
        """Record that a request was made."""
        self.calls.append(datetime.now())

    def get_reset_time(self) -> Optional[datetime]:
        """
        Get time when rate limit will reset.

        Returns:
            Datetime when limit resets, or None if not limited
        """
        if not self.calls:
            return None

        limit = self.limits[self.platform]
        oldest_call = min(self.calls)
        return oldest_call + timedelta(seconds=limit['window'])

    def get_remaining(self) -> int:
        """
        Get number of remaining API calls.

        Returns:
            Number of calls remaining in current window
        """
        if self.platform not in self.limits:
            return 999999

        limit = self.limits[self.platform]
        now = datetime.now()
        window_start = now - timedelta(seconds=limit['window'])

        # Remove old calls
        self.calls = [c for c in self.calls if c > window_start]

        return limit['calls'] - len(self.calls)


class SyncQueue:
    """Queue manager for synchronization requests."""

    def __init__(self):
        """Initialize sync queue."""
        self.rate_limiters: Dict[str, RateLimiter] = {}

    def _get_rate_limiter(self, platform: str) -> RateLimiter:
        """Get or create rate limiter for platform."""
        if platform not in self.rate_limiters:
            self.rate_limiters[platform] = RateLimiter(platform)
        return self.rate_limiters[platform]

    def add_to_queue(self, project_id: int, priority: int = 5) -> int:
        """
        Add project to sync queue.

        Args:
            project_id: Project ID to sync
            priority: Priority (1=highest, 10=lowest)

        Returns:
            Queue item ID
        """
        conn = db.init_db()
        cursor = conn.cursor()

        # Check if already in queue
        cursor.execute("""
            SELECT id FROM sync_queue
            WHERE project_id = ? AND status = 'pending'
        """, (project_id,))

        existing = cursor.fetchone()
        if existing:
            conn.close()
            return existing[0]

        # Add to queue
        cursor.execute("""
            INSERT INTO sync_queue (project_id, priority, status)
            VALUES (?, ?, 'pending')
        """, (project_id, priority))

        queue_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return queue_id

    def get_next_batch(self, platform: str, batch_size: int = 10) -> List[SyncQueueItem]:
        """
        Get next batch of items to sync, respecting rate limits.

        Args:
            platform: Platform to sync ('github' or 'gitlab')
            batch_size: Maximum number of items to return

        Returns:
            List of sync queue items
        """
        rate_limiter = self._get_rate_limiter(platform)

        # Check if we can make requests
        if not rate_limiter.can_make_request():
            return []

        # Calculate how many we can fetch
        remaining = rate_limiter.get_remaining()
        fetch_count = min(batch_size, remaining - 100)  # Keep buffer

        if fetch_count <= 0:
            return []

        conn = db.init_db()
        cursor = conn.cursor()

        # Get pending items, ordered by priority and request time
        cursor.execute("""
            SELECT q.id, q.project_id, q.priority, q.requested_at, q.status
            FROM sync_queue q
            INNER JOIN projects p ON q.project_id = p.id
            INNER JOIN remote_repos r ON p.id = r.project_id
            WHERE q.status = 'pending'
            AND r.platform = ?
            AND r.sync_enabled = 1
            ORDER BY q.priority ASC, q.requested_at ASC
            LIMIT ?
        """, (platform, fetch_count))

        items = []
        for row in cursor.fetchall():
            items.append(SyncQueueItem(
                id=row[0],
                project_id=row[1],
                priority=row[2],
                requested_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
                status=row[4]
            ))

        conn.close()
        return items

    def mark_processing(self, queue_id: int) -> None:
        """Mark queue item as processing."""
        conn = db.init_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sync_queue
            SET status = 'processing'
            WHERE id = ?
        """, (queue_id,))

        conn.commit()
        conn.close()

    def mark_completed(self, queue_id: int) -> None:
        """Mark queue item as completed."""
        conn = db.init_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sync_queue
            SET status = 'completed'
            WHERE id = ?
        """, (queue_id,))

        conn.commit()
        conn.close()

    def mark_failed(self, queue_id: int) -> None:
        """Mark queue item as failed."""
        conn = db.init_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sync_queue
            SET status = 'failed'
            WHERE id = ?
        """, (queue_id,))

        conn.commit()
        conn.close()

    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get statistics about the sync queue.

        Returns:
            Dictionary with queue statistics
        """
        conn = db.init_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status, COUNT(*)
            FROM sync_queue
            GROUP BY status
        """)

        stats = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]

        conn.close()
        return stats

    def clear_completed(self, older_than_days: int = 7) -> int:
        """
        Clear completed queue items older than specified days.

        Args:
            older_than_days: Remove items older than this many days

        Returns:
            Number of items removed
        """
        conn = db.init_db()
        cursor = conn.cursor()

        cutoff = datetime.now() - timedelta(days=older_than_days)

        cursor.execute("""
            DELETE FROM sync_queue
            WHERE status = 'completed'
            AND requested_at < ?
        """, (cutoff.isoformat(),))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted
