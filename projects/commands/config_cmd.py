"""Config command - Manage project-cli configuration."""

import typer

from .. import config
from .. import display


def register_command(app: typer.Typer):
    """Register the 'config' command with the Typer app."""

    @app.command(name="config")
    def config_command(
        show: bool = typer.Option(False, "--show", help="Show current configuration"),
        set_ide: bool = typer.Option(False, "--set-ide", help="Set IDE preference interactively"),
    ):
        """Manage project-cli configuration."""

        if set_ide:
            # Interactive IDE setup
            display.print_info("Setting up your IDE preference...")
            ide = config.interactive_ide_setup()
            display.print_success(f"IDE configured: {ide}")
            return

        if show:
            # Show current configuration
            current_config = config.load_config()

            if not current_config:
                display.print_info("No configuration found")
                display.print_info("Run 'projects config --set-ide' to configure your IDE")
                return

            display.print_info("Current configuration:")
            for key, value in current_config.items():
                print(f"  {key}: {value}")
            return

        # Default behavior - show current IDE and offer to change
        current_ide = config.get_ide()

        if current_ide:
            display.print_info(f"Current IDE: {current_ide}")
            display.print_info("Run 'projects config --set-ide' to change it")
        else:
            display.print_info("No IDE configured")
            display.print_info("Run 'projects config --set-ide' to configure your IDE")
