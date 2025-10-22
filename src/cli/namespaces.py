"""CLI commands for namespaces."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json

from src.api_client.client import KestraAPIClient
from src.api_client.namespaces import NamespacesAPI
from src.api_client.auth import AuthContext


console = Console()
app = typer.Typer()


@app.command()
def list(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Filter namespaces by search query"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """List all namespaces in the Kestra instance."""
    try:
        # Initialize API client
        client = KestraAPIClient()
        
        # Create temporary context if credentials provided via CLI
        context = None
        if host or token:
            context = AuthContext(
                name="temp",
                host=host or "http://localhost:8080",
                tenant=tenant or "main",
                auth_method="token",
                token=token
            )
        
        # Get namespaces
        namespaces_api = NamespacesAPI(client)
        namespaces = namespaces_api.list_namespaces(tenant, context, query=query)
        
        if output == "json":
            rprint(json.dumps(namespaces, indent=2))
        else:
            # Create table
            table = Table(title="Namespaces")
            table.add_column("ID", style="cyan")
            table.add_column("Deleted", style="yellow")
            
            for namespace in namespaces:
                # Handle both string format and dictionary format
                if isinstance(namespace, str):
                    table.add_row(namespace, "false")
                else:
                    deleted_status = "true" if namespace.get("deleted", False) else "false"
                    table.add_row(
                        namespace.get("id", ""),
                        deleted_status
                    )
            
            console.print(table)
            console.print(f"\n[dim]Total namespaces: {len(namespaces)}[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

