"""CLI commands for flows."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json
from pathlib import Path

from src.api_client.client import KestraAPIClient
from src.api_client.flows import FlowsAPI
from src.api_client.auth import AuthContext


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
            from src.api_client.auth import AuthContext
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
            from src.api_client.auth import AuthContext
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


@app.command()
def deploy(
    filepath: str = typer.Argument(..., help="Path to the YAML flow file"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    override: bool = typer.Option(False, "--override", help="Override the flow if it already exists"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """Deploy a flow from a YAML file (creates or updates)."""
    try:
        # Check if file exists
        file_path = Path(filepath)
        if not file_path.exists():
            console.print(f"[red]Error: File '{filepath}' not found[/red]")
            raise typer.Exit(1)
        
        # Read YAML file
        try:
            yaml_content = file_path.read_text()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)
        
        # Initialize API client
        client = KestraAPIClient()
        
        # Create temporary context if credentials provided via CLI
        context = None
        if host or token:
            from src.api_client.auth import AuthContext
            context = AuthContext(
                name="temp",
                host=host or "http://localhost:8080",
                tenant=tenant or "main",
                auth_method="token",
                token=token
            )
        
        # Create flow
        flows_api = FlowsAPI(client)
        flow = flows_api.create_flow(yaml_content, tenant, context, override)
        
        if output == "json":
            rprint(json.dumps(flow, indent=2))
        else:
            # Display success message with flow details
            console.print(f"[green]✓ Flow deployed successfully![/green]")
            console.print(f"[cyan]Flow ID:[/cyan] {flow.get('id', 'N/A')}")
            console.print(f"[cyan]Namespace:[/cyan] {flow.get('namespace', 'N/A')}")
            console.print(f"[cyan]Revision:[/cyan] {flow.get('revision', 'N/A')}")
    
    except ValueError as e:
        # Handle validation errors (like flow already exists)
        console.print(f"[yellow]Warning: {e}[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
