"""Main CLI entrypoint for Kestra CLI."""

import typer
from rich.console import Console

from cli.flows import app as flows_app

console = Console()

# Create the main Typer app
app = typer.Typer(
    name="kestra",
    help="Kestra CLI - Manage flows",
    no_args_is_help=True
)

# Add subcommands
app.add_typer(flows_app, name="flows", help="Manage flows")

# Add a version command
@app.command()
def version():
    """Show version information."""
    console.print("Kestra CLI v0.1.0")

# Create config subcommand group
config_app = typer.Typer(help="Manage configuration and authentication")

@config_app.command()
def show():
    """Show current configuration."""
    from api_client.auth import AuthManager
    
    auth_manager = AuthManager()
    
    # Show current configuration
    contexts = auth_manager.list_contexts()
    default_context = auth_manager.get_context()
    
    if not contexts:
        console.print("[yellow]No authentication contexts configured.[/yellow]")
        console.print("Use 'config add' to add a new context.")
        return
    
    console.print("[bold]Current Configuration:[/bold]")
    console.print(f"Default context: {default_context.name if default_context else 'None'}")
    console.print()
    
    for name, context in contexts.items():
        status = "✓" if default_context and default_context.name == name else " "
        console.print(f"{status} {name}: {context.host} (tenant: {context.tenant})")

@config_app.command()
def add(
    name: str = typer.Argument(..., help="Context name"),
    host: str = typer.Argument(..., help="Kestra host URL"),
    tenant: str = typer.Argument(..., help="Tenant name"),
    token: str = typer.Option(..., "--token", "-t", help="API token"),
    set_default: bool = typer.Option(False, "--default", help="Set as default context")
):
    """Add a new authentication context."""
    from api_client.auth import AuthManager, AuthContext
    
    auth_manager = AuthManager()
    
    # Create context
    context = AuthContext(
        name=name,
        host=host,
        tenant=tenant,
        auth_method="token",
        token=token
    )
    
    # Add context
    auth_manager.add_context(context)
    
    if set_default:
        auth_manager.set_default_context(name)
        console.print(f"[green]Context '{name}' added and set as default.[/green]")
    else:
        console.print(f"[green]Context '{name}' added.[/green]")
    
    console.print(f"Host: {host}")
    console.print(f"Tenant: {tenant}")
    console.print("Token: [REDACTED]")

@config_app.command()
def remove(
    name: str = typer.Argument(..., help="Context name to remove")
):
    """Remove an authentication context."""
    from api_client.auth import AuthManager
    
    auth_manager = AuthManager()
    
    try:
        auth_manager.delete_context(name)
        console.print(f"[green]Context '{name}' removed.[/green]")
    except KeyError:
        console.print(f"[red]Context '{name}' not found.[/red]")
        raise typer.Exit(1)

@config_app.command()
def use(
    name: str = typer.Argument(..., help="Context name to use as default")
):
    """Set a context as the default."""
    from api_client.auth import AuthManager
    
    auth_manager = AuthManager()
    
    try:
        auth_manager.set_default_context(name)
        console.print(f"[green]Default context set to '{name}'.[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

# Add config subcommand to main app
app.add_typer(config_app, name="config", help="Manage configuration and authentication")
