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


@app.command()
def run(
    namespace: str = typer.Argument(..., help="Namespace of the flow"),
    flow_id: str = typer.Argument(..., help="Flow ID to execute"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for execution to complete"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """Trigger a flow execution.
    
    This command triggers an execution of the specified flow. By default, it will
    return immediately after triggering (fire and forget). Use --wait to wait for
    the execution to complete.
    """
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
        
        # Trigger execution
        executions_api = ExecutionsAPI(client)
        
        if wait:
            console.print(f"[cyan]Triggering execution of flow '{flow_id}' in namespace '{namespace}'...[/cyan]")
            console.print("[yellow]Waiting for execution to complete...[/yellow]")
        
        execution = executions_api.trigger_execution(
            namespace=namespace,
            flow_id=flow_id,
            wait=wait,
            tenant=tenant,
            context=context
        )
        
        if output == "json":
            rprint(json.dumps(execution, indent=2))
        else:
            # Display execution information
            console.print("[green]✓ Execution triggered successfully![/green]")
            console.print()
            console.print(f"[cyan]Execution ID:[/cyan] {execution.get('id', 'N/A')}")
            console.print(f"[cyan]Flow:[/cyan] {execution.get('flowId', 'N/A')}")
            console.print(f"[cyan]Namespace:[/cyan] {execution.get('namespace', 'N/A')}")
            console.print(f"[cyan]State:[/cyan] {execution.get('state', {}).get('current', 'N/A')}")
            
            if 'startDate' in execution:
                console.print(f"[cyan]Started:[/cyan] {execution['startDate']}")
            
            if wait and 'endDate' in execution:
                console.print(f"[cyan]Ended:[/cyan] {execution['endDate']}")
                
                # Show duration if available
                state_info = execution.get('state', {})
                if 'duration' in state_info:
                    duration_ms = state_info['duration']
                    duration_sec = duration_ms / 1000
                    console.print(f"[cyan]Duration:[/cyan] {duration_sec:.2f}s")
            
            # Show URL if available
            if 'url' in execution:
                console.print(f"[cyan]URL:[/cyan] {execution['url']}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def get(
    execution_id: str = typer.Argument(..., help="Execution ID to retrieve"),
    tenant: Optional[str] = typer.Option(None, "--tenant", "-t", help="Tenant name"),
    host: Optional[str] = typer.Option(None, "--host", help="Kestra host URL"),
    token: Optional[str] = typer.Option(None, "--token", help="API token"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table or json)")
):
    """Get execution details by ID.
    
    This command retrieves detailed information about a specific execution.
    """
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
        
        # Get execution
        executions_api = ExecutionsAPI(client)
        execution = executions_api.get_execution(
            execution_id=execution_id,
            tenant=tenant,
            context=context
        )
        
        if output == "json":
            rprint(json.dumps(execution, indent=2))
        else:
            # Display execution information
            console.print(f"[bold]Execution Details[/bold]")
            console.print()
            console.print(f"[cyan]Execution ID:[/cyan] {execution.get('id', 'N/A')}")
            console.print(f"[cyan]Flow:[/cyan] {execution.get('flowId', 'N/A')}")
            console.print(f"[cyan]Namespace:[/cyan] {execution.get('namespace', 'N/A')}")
            console.print(f"[cyan]Flow Revision:[/cyan] {execution.get('flowRevision', 'N/A')}")
            
            # State information
            state_info = execution.get('state', {})
            current_state = state_info.get('current', 'N/A')
            console.print(f"[cyan]State:[/cyan] {current_state}")
            
            # Dates
            if 'startDate' in state_info:
                console.print(f"[cyan]Started:[/cyan] {state_info['startDate']}")
            
            if 'endDate' in state_info:
                console.print(f"[cyan]Ended:[/cyan] {state_info['endDate']}")
            
            # Duration
            if 'duration' in state_info:
                duration_str = state_info['duration']
                # Try to parse duration (format: PT0.123S)
                try:
                    # Simple parsing for PT format
                    if duration_str.startswith('PT') and duration_str.endswith('S'):
                        duration_sec = float(duration_str[2:-1])
                        console.print(f"[cyan]Duration:[/cyan] {duration_sec:.2f}s")
                    else:
                        console.print(f"[cyan]Duration:[/cyan] {duration_str}")
                except:
                    console.print(f"[cyan]Duration:[/cyan] {duration_str}")
            
            # Labels
            labels = execution.get('labels', [])
            if labels:
                console.print(f"[cyan]Labels:[/cyan]")
                for label in labels:
                    console.print(f"  • {label.get('key', 'N/A')}: {label.get('value', 'N/A')}")
            
            # URL - construct if not provided
            if 'url' in execution:
                console.print()
                console.print(f"[cyan]URL:[/cyan] {execution['url']}")
            else:
                # Construct URL from execution data
                exec_context = context if context else executions_api.client.auth_manager.get_context()
                if exec_context and execution.get('id') and execution.get('namespace') and execution.get('flowId'):
                    exec_tenant = tenant or exec_context.tenant
                    exec_host = exec_context.host.rstrip('/')
                    exec_url = f"{exec_host}/ui/{exec_tenant}/executions/{execution['namespace']}/{execution['flowId']}/{execution['id']}"
                    console.print()
                    console.print(f"[cyan]URL:[/cyan] {exec_url}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

