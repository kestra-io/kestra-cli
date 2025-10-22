"""Executions API endpoints for Kestra."""

from typing import Dict, Any, Optional, List
from src.api_client.client import KestraAPIClient
from src.api_client.auth import AuthContext


class ExecutionsAPI:
    """API client for executions endpoints."""
    
    def __init__(self, client: KestraAPIClient):
        """Initialize the executions API client.
        
        Args:
            client: KestraAPIClient instance
        """
        self.client = client
    
    def kill_by_query(
        self,
        state: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        flow_id: Optional[str] = None,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> Dict[str, Any]:
        """Kill executions matching the query parameters.
        
        Args:
            state: List of execution states to filter by (e.g., ['RUNNING'])
            namespace: Optional namespace to filter executions
            flow_id: Optional flow ID to filter executions
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            Response dictionary with kill operation results
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        # Build query parameters
        params = {}
        if state:
            # Add state as array parameter (multiple values)
            params['state'] = state
        if namespace:
            params['namespace'] = namespace
        if flow_id:
            params['flowId'] = flow_id
        
        endpoint = f"/api/v1/{tenant}/executions/kill/by-query"
        response = self.client.delete(endpoint, context, params=params)
        return response.json()
    
    def trigger_execution(
        self,
        namespace: str,
        flow_id: str,
        wait: bool = False,
        inputs: Optional[Dict[str, Any]] = None,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> Dict[str, Any]:
        """Trigger a flow execution.
        
        Args:
            namespace: Namespace of the flow
            flow_id: Flow ID to execute
            wait: If True, wait for execution to complete before returning
            inputs: Optional inputs for the flow execution
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            Execution dictionary
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        # Build query parameters
        params = {}
        if wait:
            params['wait'] = 'true'
        
        endpoint = f"/api/v1/{tenant}/executions/{namespace}/{flow_id}"
        
        # If inputs are provided, send them as JSON body
        if inputs:
            response = self.client.post(endpoint, context, params=params, json=inputs)
        else:
            response = self.client.post(endpoint, context, params=params)
        
        return response.json()
    
    def get_execution(
        self,
        execution_id: str,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> Dict[str, Any]:
        """Get execution details by ID.
        
        Args:
            execution_id: Execution ID
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            Execution dictionary
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        endpoint = f"/api/v1/{tenant}/executions/{execution_id}"
        response = self.client.get(endpoint, context)
        return response.json()

