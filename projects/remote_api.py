"""Remote API integration for GitHub and GitLab."""

import subprocess
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    GithubException = Exception


def detect_remote_info(project_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Detect remote repository information from git config.

    Args:
        project_path: Path to project directory

    Returns:
        Tuple of (platform, owner, repo_name) or (None, None, None)
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return None, None, None

        remote_url = result.stdout.strip()

        # Parse GitHub URLs
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        if 'github.com' in remote_url:
            platform = 'github'
            if remote_url.startswith('https://'):
                # https://github.com/owner/repo.git
                parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            elif remote_url.startswith('git@'):
                # git@github.com:owner/repo.git
                parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
            else:
                return None, None, None

            if len(parts) >= 2:
                owner, repo_name = parts[0], parts[1]
                return platform, owner, repo_name

        # Parse GitLab URLs
        # https://gitlab.com/owner/repo.git
        # git@gitlab.com:owner/repo.git
        elif 'gitlab.com' in remote_url:
            platform = 'gitlab'
            if remote_url.startswith('https://'):
                parts = remote_url.replace('https://gitlab.com/', '').replace('.git', '').split('/')
            elif remote_url.startswith('git@'):
                parts = remote_url.replace('git@gitlab.com:', '').replace('.git', '').split('/')
            else:
                return None, None, None

            if len(parts) >= 2:
                owner, repo_name = parts[0], parts[1]
                return platform, owner, repo_name

    except Exception:
        pass

    return None, None, None


class RemoteAPI:
    """Abstraction layer for GitHub and GitLab APIs."""

    def __init__(self, platform: str, token: str):
        """
        Initialize remote API client.

        Args:
            platform: Platform name ('github' or 'gitlab')
            token: API token

        Raises:
            ValueError: If platform is not supported
        """
        self.platform = platform

        if platform == 'github':
            if not GITHUB_AVAILABLE:
                raise ImportError("PyGithub not installed")
            self.client = Github(token)
        elif platform == 'gitlab':
            # GitLab support deferred to Phase 3
            raise NotImplementedError("GitLab support coming soon")
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def get_repo_info(self, owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch repository metadata.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            Dictionary with repo info or None if failed
        """
        try:
            if self.platform == 'github':
                repo = self.client.get_repo(f"{owner}/{repo_name}")

                # Get topics (requires special accept header)
                try:
                    topics = repo.get_topics()
                except Exception:
                    topics = []

                return {
                    'owner': owner,
                    'name': repo_name,
                    'description': repo.description or '',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'watchers': repo.watchers_count,
                    'open_issues': repo.open_issues_count,
                    'language': repo.language or '',
                    'size_kb': repo.size,
                    'default_branch': repo.default_branch,
                    'license': repo.license.name if repo.license else None,
                    'topics': topics,
                    'created_at': repo.created_at,
                    'updated_at': repo.updated_at,
                    'pushed_at': repo.pushed_at,
                    'homepage': repo.homepage or '',
                    'archived': repo.archived,
                    'private': repo.private,
                }

        except GithubException as e:
            # Handle rate limiting, not found, etc.
            return None
        except Exception:
            return None

        return None

    def get_open_prs_count(self, owner: str, repo_name: str) -> int:
        """
        Get count of open pull requests.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            Number of open PRs, or 0 if failed
        """
        try:
            if self.platform == 'github':
                repo = self.client.get_repo(f"{owner}/{repo_name}")
                prs = repo.get_pulls(state='open')
                return prs.totalCount

        except Exception:
            return 0

        return 0

    def get_latest_workflow_status(self, owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get latest GitHub Actions workflow status.

        Args:
            owner: Repository owner
            repo_name: Repository name

        Returns:
            Dictionary with workflow info or None
        """
        try:
            if self.platform == 'github':
                repo = self.client.get_repo(f"{owner}/{repo_name}")

                # Get latest workflow runs
                workflows = repo.get_workflow_runs()

                if workflows.totalCount == 0:
                    return None

                latest = workflows[0]

                return {
                    'name': latest.name or 'Workflow',
                    'status': latest.status,  # 'completed', 'in_progress', 'queued'
                    'conclusion': latest.conclusion,  # 'success', 'failure', 'neutral', 'cancelled', 'skipped', 'timed_out', 'action_required'
                    'branch': latest.head_branch,
                    'commit_sha': latest.head_sha,
                    'started_at': latest.created_at,
                    'completed_at': latest.updated_at,
                    'url': latest.html_url,
                }

        except Exception:
            return None

        return None

    def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get API rate limit information.

        Returns:
            Dictionary with rate limit info
        """
        try:
            if self.platform == 'github':
                rate_limit = self.client.get_rate_limit()
                core = rate_limit.core

                return {
                    'limit': core.limit,
                    'remaining': core.remaining,
                    'reset_at': datetime.fromtimestamp(core.reset.timestamp()),
                    'used': core.limit - core.remaining,
                }

        except Exception:
            return {
                'limit': 5000,
                'remaining': 0,
                'reset_at': datetime.now(),
                'used': 0,
            }

        return {}

    def test_connection(self) -> bool:
        """
        Test if API connection is working.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            if self.platform == 'github':
                # Try to get authenticated user
                self.client.get_user().login
                return True

        except Exception:
            return False

        return False
