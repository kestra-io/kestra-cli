"""CLI commands for flows."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json

from api_client.client import KestraAPIClient
from api_client.flows import FlowsAPI
from api_client.auth import AuthContext


console = Console()
app = typer.Typer()


@app.command()
def list(
    namespace: str = typer.Argument(..., help="Namespace to list flows from"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """List flows in a namespace."""
    try:
        # Initialize API client
        client = KestraAPIClient()
        
        # Create temporary context if credentials provided via CLI
        context = None
        if host or token:
            from api_client.auth import AuthContext
            context = AuthContext(
                name="temp",
                host=host or "http://localhost:8080",
                tenant=tenant or "main",
                auth_method="token",
                token=token
            )
        
        # Get flows
        flows_api = FlowsAPI(client)
        flows = flows_api.list_flows(namespace, tenant, context)
        
        if output == "json":
            rprint(json.dumps(flows, indent=2))
        else:
            # Create table
            table = Table(title=f"Flows in namespace '{namespace}'")
            table.add_column("ID", style="cyan")
            table.add_column("Namespace", style="magenta")
            table.add_column("Description", style="green")
            table.add_column("Revision", style="yellow")
            
            for flow in flows:
                table.add_row(
                    flow.get("id", ""),
                    flow.get("namespace", ""),
                    flow.get("description", ""),
                    str(flow.get("revision", ""))
                )
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def get(
    namespace: str = typer.Argument(..., help="Namespace of the flow"),
    flow_id: str = typer.Argument(..., help="Flow ID"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("json", "--output", "-o", help="Output format (table or json)")
):
    """Get a specific flow."""
    try:
        # Initialize API client
        client = KestraAPIClient()
        
        # Create temporary context if credentials provided via CLI
        context = None
        if host or token:
            from api_client.auth import AuthContext
            context = AuthContext(
                name="temp",
                host=host or "http://localhost:8080",
                tenant=tenant or "main",
                auth_method="token",
                token=token
            )
        
        # Get flow
        flows_api = FlowsAPI(client)
        flow = flows_api.get_flow(namespace, flow_id, tenant, context)
        
        if output == "json":
            rprint(json.dumps(flow, indent=2))
        else:
            # Create table for flow details
            table = Table(title=f"Flow: {flow_id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in flow.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, indent=2)
                table.add_row(key, str(value))
            
            console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
