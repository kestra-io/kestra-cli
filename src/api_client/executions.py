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

