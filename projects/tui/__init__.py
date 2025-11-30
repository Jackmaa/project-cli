"""TUI Dashboard module."""

import sys
import termios
import tty

from .app import ProjectDashboardApp


def run_dashboard():
    """Entry point for TUI dashboard."""
    # Flush stdin to clear any pending escape sequences
    if sys.stdin.isatty():
        try:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass  # Ignore if flush fails

    app = ProjectDashboardApp()
    # Disable mouse support to prevent phantom inputs from mouse sequences
    app.run(mouse=False)


__all__ = ["run_dashboard", "ProjectDashboardApp"]
