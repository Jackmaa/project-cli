"""Sync orchestration logic."""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from . import database as db
from . import credentials
from . import remote_api
from . import sync_queue
from . import display


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    project_id: int
    project_name: str
    stars: Optional[int] = None
    forks: Optional[int] = None
    open_issues: Optional[int] = None
    open_prs: Optional[int] = None
    workflow_status: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class SyncOrchestrator:
    """Coordinates sync operations."""

    def __init__(self):
        self.queue = sync_queue.SyncQueue()

    def sync_project(
        self,
        project_id: int,
        update_metadata: bool = False,
        force: bool = False
    ) -> SyncResult:
        """
        Sync a single project.

        Steps:
        1. Get remote repo info from database
        2. Get token for platform
        3. Initialize RemoteAPI
        4. Fetch repo metadata
        5. Fetch PR count
        6. Fetch workflow status
        7. Save to cache tables
        8. Optionally update project metadata
        9. Update last_synced timestamp

        Args:
            project_id: Project ID to sync
            update_metadata: Whether to update project description/language/tags
            force: Force sync even if cache is valid

        Returns:
            SyncResult with operation details
        """
        start_time = time.time()

        # Get project
        project = db.get_project_by_id(project_id)
        if not project:
            return SyncResult(
                success=False,
                project_id=project_id,
                project_name="Unknown",
                error="Project not found",
                duration_seconds=time.time() - start_time
            )

        try:
            # Get remote repo info
            remote_info = db.get_remote_repo_info(project_id)
            if not remote_info:
                return SyncResult(
                    success=False,
                    project_id=project_id,
                    project_name=project.name,
                    error="Sync not enabled for this project",
                    duration_seconds=time.time() - start_time
                )

            if not remote_info['sync_enabled']:
                return SyncResult(
                    success=False,
                    project_id=project_id,
                    project_name=project.name,
                    error="Sync is disabled for this project",
                    duration_seconds=time.time() - start_time
                )

            # Check if cache is still valid (unless force)
            if not force:
                cached_metrics = db.get_remote_metrics(remote_info['id'], ttl_hours=24)
                if cached_metrics:
                    return SyncResult(
                        success=True,
                        project_id=project_id,
                        project_name=project.name,
                        stars=cached_metrics.get('stars'),
                        forks=cached_metrics.get('forks'),
                        open_issues=cached_metrics.get('open_issues'),
                        open_prs=cached_metrics.get('open_prs'),
                        error="Using cached data (use --force to refresh)",
                        duration_seconds=time.time() - start_time
                    )

            platform = remote_info['platform']
            owner = remote_info['owner']
            repo_name = remote_info['repo_name']

            # Get token
            token = credentials.get_token(platform)
            if not token:
                return SyncResult(
                    success=False,
                    project_id=project_id,
                    project_name=project.name,
                    error=f"No {platform} token found. Run: projects auth {platform} --token YOUR_TOKEN",
                    duration_seconds=time.time() - start_time
                )

            # Initialize API
            api = remote_api.RemoteAPI(platform, token)

            # Fetch repository metadata
            display.print_info(f"Fetching repository metadata for {owner}/{repo_name}...")
            repo_info = api.get_repo_info(owner, repo_name)

            if not repo_info:
                return SyncResult(
                    success=False,
                    project_id=project_id,
                    project_name=project.name,
                    error=f"Repository not found or inaccessible: {owner}/{repo_name}",
                    duration_seconds=time.time() - start_time
                )

            # Fetch PR count
            display.print_info("Fetching pull request count...")
            pr_count = api.get_open_prs_count(owner, repo_name)
            repo_info['open_prs'] = pr_count

            # Save metrics to cache
            display.print_info("Saving metrics to cache...")
            success = db.save_remote_metrics(remote_info['id'], repo_info)

            if not success:
                return SyncResult(
                    success=False,
                    project_id=project_id,
                    project_name=project.name,
                    error="Failed to save metrics to cache",
                    duration_seconds=time.time() - start_time
                )

            # Fetch workflow status (if available)
            workflow_status = None
            try:
                display.print_info("Fetching CI/CD workflow status...")
                workflow_data = api.get_latest_workflow_status(owner, repo_name)
                if workflow_data:
                    db.save_pipeline_status(remote_info['id'], workflow_data)
                    workflow_status = workflow_data.get('conclusion', workflow_data.get('status'))
            except Exception as e:
                # Workflow fetch is optional, don't fail sync if it errors
                display.print_info(f"Could not fetch workflow status: {e}")

            # Update project metadata if requested
            if update_metadata:
                display.print_info("Updating project metadata...")
                db.update_project_from_remote_metadata(
                    project_id=project_id,
                    description=repo_info.get('description', ''),
                    language=repo_info.get('language', ''),
                    topics=repo_info.get('topics', [])
                )

            # Update last synced timestamp
            db.update_last_synced(remote_info['id'])

            duration = time.time() - start_time

            return SyncResult(
                success=True,
                project_id=project_id,
                project_name=project.name,
                stars=repo_info.get('stars'),
                forks=repo_info.get('forks'),
                open_issues=repo_info.get('open_issues'),
                open_prs=repo_info.get('open_prs'),
                workflow_status=workflow_status,
                duration_seconds=duration
            )

        except remote_api.GithubException as e:
            error_msg = f"GitHub API error: {e}"
            return SyncResult(
                success=False,
                project_id=project_id,
                project_name=project.name,
                error=error_msg,
                duration_seconds=time.time() - start_time
            )
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            return SyncResult(
                success=False,
                project_id=project_id,
                project_name=project.name,
                error=error_msg,
                duration_seconds=time.time() - start_time
            )

    def sync_all_enabled(self, batch_size: int = 10, update_metadata: bool = False) -> list[SyncResult]:
        """
        Sync all enabled projects in batches.

        Args:
            batch_size: Maximum number of projects to sync at once
            update_metadata: Whether to update project metadata

        Returns:
            List of SyncResult objects
        """
        enabled_projects = db.get_all_sync_enabled_projects()

        if not enabled_projects:
            display.print_info("No projects with sync enabled")
            return []

        results = []

        display.print_info(f"Syncing {len(enabled_projects)} projects...")

        for i, proj_data in enumerate(enabled_projects, 1):
            display.print_info(f"\n[{i}/{len(enabled_projects)}] Syncing {proj_data['name']}...")

            result = self.sync_project(
                project_id=proj_data['project_id'],
                update_metadata=update_metadata,
                force=True  # Force refresh when syncing all
            )

            results.append(result)

            # Small delay to avoid rate limiting
            if i < len(enabled_projects):
                time.sleep(0.5)

        return results

    def process_sync_queue(self, platform: str, batch_size: int = 10) -> int:
        """
        Process pending queue items for a platform.

        Args:
            platform: Platform to process ('github' or 'gitlab')
            batch_size: Maximum items to process

        Returns:
            Number of items processed
        """
        batch = self.queue.get_next_batch(platform, batch_size)

        if not batch:
            return 0

        processed = 0

        for item in batch:
            # Mark as processing
            self.queue.mark_processing(item.id)

            # Sync the project
            result = self.sync_project(item.project_id, force=True)

            # Update queue status
            if result.success:
                self.queue.mark_completed(item.id)
            else:
                self.queue.mark_failed(item.id)

            processed += 1

        return processed
