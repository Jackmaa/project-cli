"""Authentication command - Manage GitHub/GitLab tokens."""

import typer
from typing import Optional
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table

from .. import credentials
from .. import display

console = Console()


def register_command(app: typer.Typer):
    """Register the auth command."""

    @app.command()
    def auth(
        platform: Optional[str] = typer.Argument(None, help="Platform: 'github' or 'gitlab'"),
        token: Optional[str] = typer.Option(None, "--token", "-t", help="API token"),
        delete: bool = typer.Option(False, "--delete", "-d", help="Delete stored token"),
        show: bool = typer.Option(False, "--show", "-s", help="Show token status"),
        test: bool = typer.Option(False, "--test", help="Test token validity"),
        list_all: bool = typer.Option(False, "--list", "-l", help="List all stored platforms"),
        method: str = typer.Option("both", "--method", "-m", help="Storage method: 'keyring', 'encrypted_file', or 'both'"),
    ):
        """
        Manage GitHub/GitLab authentication tokens.

        Examples:
          # Store GitHub token in keyring
          projects auth github --token ghp_xxxxx

          # Store in encrypted config file only
          projects auth github --token ghp_xxxxx --method encrypted_file

          # Store in both keyring and config
          projects auth github --token ghp_xxxxx --method both

          # Test token validity
          projects auth github --test

          # Show token status
          projects auth github --show

          # Delete token
          projects auth github --delete

          # List all stored platforms
          projects auth --list
        """
        # List all stored platforms
        if list_all:
            platforms = credentials.list_stored_platforms()
            if not platforms:
                display.print_info("No stored credentials found")
                return

            table = Table(title="Stored Credentials")
            table.add_column("Platform", style="cyan")
            table.add_column("Status", style="green")

            for plat in platforms:
                table.add_row(plat, "✓ Stored")

            console.print(table)
            return

        # Validate platform (required for all other operations)
        if not platform:
            display.print_error("Platform argument is required (use --list to see all stored platforms)")
            raise typer.Exit(1)

        platform = platform.lower()
        if platform not in ['github', 'gitlab']:
            display.print_error(f"Invalid platform: {platform}. Must be 'github' or 'gitlab'")
            raise typer.Exit(1)

        # Delete token
        if delete:
            if credentials.delete_token(platform):
                display.print_success(f"Deleted {platform} token from all storage locations")
            else:
                display.print_error(f"No {platform} token found to delete")
            return

        # Test token
        if test:
            token_to_test = credentials.get_token(platform)
            if not token_to_test:
                display.print_error(f"No {platform} token found")
                display.print_info(f"Store a token first: projects auth {platform} --token YOUR_TOKEN")
                raise typer.Exit(1)

            display.print_info(f"Testing {platform} token...")

            if credentials.test_token(platform, token_to_test):
                display.print_success(f"{platform} token is valid!")
            else:
                display.print_error(f"{platform} token is invalid or expired")
            return

        # Show token status
        if show:
            token = credentials.get_token(platform)
            if token:
                # Mask token except last 4 characters
                masked = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
                display.print_info(f"{platform} token: {masked}")

                # Show where it's stored
                stored_platforms = credentials.list_stored_platforms()
                if platform in stored_platforms:
                    display.print_info("Token is stored securely")
            else:
                display.print_info(f"No {platform} token stored")
                display.print_info(f"Store a token: projects auth {platform} --token YOUR_TOKEN")
            return

        # Store token
        if not token:
            # Prompt for token (hidden input)
            console.print(f"[bold cyan]Enter {platform} API token:[/bold cyan]")
            console.print("[dim]Token input will be hidden[/dim]")
            token = Prompt.ask("Token", password=True)

            if not token:
                display.print_error("Token cannot be empty")
                raise typer.Exit(1)

        # Validate method
        if method not in ['keyring', 'encrypted_file', 'both']:
            display.print_error(f"Invalid method: {method}. Must be 'keyring', 'encrypted_file', or 'both'")
            raise typer.Exit(1)

        # Store the token
        if credentials.store_token(platform, token, method=method):
            display.print_success(f"Stored {platform} token securely using {method}")

            # Test the token
            display.print_info("Testing token validity...")
            if credentials.test_token(platform, token):
                display.print_success("Token is valid!")
            else:
                display.print_error("Warning: Token may be invalid or expired")
        else:
            display.print_error(f"Failed to store {platform} token")
            display.print_info("Make sure you have the required dependencies installed")
