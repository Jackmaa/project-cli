"""TUI Dashboard module."""

import signal
import sys
import termios
import tty

from .app import ProjectDashboardApp


def run_dashboard():
    """Entry point for TUI dashboard."""
    original_attrs = None
    cleanup_done = False

    def cleanup_terminal():
        """Restore terminal to original state."""
        nonlocal cleanup_done
        if cleanup_done:
            return
        cleanup_done = True

        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                # Disable enhanced keyboard protocols that may have been enabled
                # CSI > 0 m - Disable Kitty keyboard protocol
                sys.stdout.write("\x1b[>0m")
                # CSI ? 1004 l - Disable focus events
                sys.stdout.write("\x1b[?1004l")
                sys.stdout.flush()

                # Restore original terminal attributes
                if original_attrs is not None:
                    termios.tcsetattr(sys.stdin, termios.TCSANOW, original_attrs)
            except Exception:
                pass  # Ignore cleanup errors

    def signal_handler(signum, frame):
        """Handle interrupt signal gracefully."""
        cleanup_terminal()
        sys.exit(0)

    # Save original terminal state
    if sys.stdin.isatty():
        try:
            original_attrs = termios.tcgetattr(sys.stdin)
        except Exception:
            pass  # Ignore if we can't get attrs

        # Flush stdin to clear any pending escape sequences
        try:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass  # Ignore if flush fails

    # Register signal handler for clean exit on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        app = ProjectDashboardApp()
        # Disable mouse support to prevent phantom inputs from mouse sequences
        app.run(mouse=False)
    finally:
        # Always restore terminal state, even on exception
        cleanup_terminal()


__all__ = ["run_dashboard", "ProjectDashboardApp"]
