"""CLI commands for executions."""

import typer
from typing import Optional
from rich.console import Console
from rich import print as rprint
import json

from src.api_client.client import KestraAPIClient
from src.api_client.executions import ExecutionsAPI
from src.api_client.auth import AuthContext


console = Console()
app = typer.Typer()


@app.command()
def kill_running(
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace"),
    flow_id: Optional[str] = typer.Option(None, "--flow-id", "-f", help="Filter by flow ID (requires --namespace)"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """Kill all executions in RUNNING state.
    
    This command kills all running executions. You can optionally filter by
    namespace and/or flow ID to target specific executions.
    
    Note: If you use --flow-id, you must also provide --namespace, as flow IDs
    are only unique within a namespace.
    """
    try:
        # Validate that namespace is provided if flow_id is specified
        if flow_id and not namespace:
            console.print("[red]Error: --namespace is required when using --flow-id[/red]")
            console.print("[yellow]Flow IDs are only unique within a namespace.[/yellow]")
            raise typer.Exit(1)
        
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
        
        # Kill executions
        executions_api = ExecutionsAPI(client)
        result = executions_api.kill_by_query(
            state=["RUNNING"],
            namespace=namespace,
            flow_id=flow_id,
            tenant=tenant,
            context=context
        )
        
        if output == "json":
            rprint(json.dumps(result, indent=2))
        else:
            # Display success message
            console.print("[green]✓ Kill request sent successfully![/green]")
            
            # Build filter description
            filters = []
            if namespace:
                filters.append(f"namespace: {namespace}")
            if flow_id:
                filters.append(f"flow ID: {flow_id}")
            
            if filters:
                console.print(f"[cyan]Filters:[/cyan] {', '.join(filters)}")
            else:
                console.print("[cyan]Filters:[/cyan] None (all running executions)")
            
            console.print(f"[cyan]State:[/cyan] RUNNING")
            
            # Display result details if available
            if isinstance(result, dict):
                if 'count' in result:
                    console.print(f"[cyan]Executions killed:[/cyan] {result['count']}")
                elif 'message' in result:
                    console.print(f"[cyan]Message:[/cyan] {result['message']}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

