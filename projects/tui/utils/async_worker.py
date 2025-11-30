"""Async worker for long-running operations."""

import asyncio
from typing import Callable, Any, Optional


class AsyncWorker:
    """Manages async operations in TUI."""

    @staticmethod
    async def run_with_notification(
        screen,
        task: Callable,
        loading_msg: str,
        success_msg: str,
        error_msg: str = "Operation failed"
    ) -> Optional[Any]:
        """
        Run async task with notifications.

        Args:
            screen: Textual screen instance
            task: Callable to execute
            loading_msg: Message to show while loading
            success_msg: Message on success
            error_msg: Message on error

        Returns:
            Result of task or None on error
        """
        screen.notify(loading_msg, timeout=None, severity="information")

        try:
            # Run task in executor if not async
            if asyncio.iscoroutinefunction(task):
                result = await task()
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, task)

            screen.notify(success_msg, severity="information")
            return result

        except Exception as e:
            screen.notify(f"{error_msg}: {str(e)}", severity="error")
            return None
