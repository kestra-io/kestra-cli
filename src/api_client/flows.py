"""Flows API endpoints for Kestra."""

from typing import List, Dict, Any, Optional
from src.api_client.client import KestraAPIClient
from src.api_client.auth import AuthContext


class FlowsAPI:
    """API client for flows endpoints."""
    
    def __init__(self, client: KestraAPIClient):
        """Initialize the flows API client.
        
        Args:
            client: KestraAPIClient instance
        """
        self.client = client
    
    def list_flows(
        self,
        namespace: str,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> List[Dict[str, Any]]:
        """List flows in a namespace.
        
        Args:
            namespace: Namespace to list flows from
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            List of flow dictionaries
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        endpoint = f"/api/v1/{tenant}/flows/{namespace}"
        response = self.client.get(endpoint, context)
        return response.json()
    
    def get_flow(
        self,
        namespace: str,
        flow_id: str,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> Dict[str, Any]:
        """Get a specific flow.
        
        Args:
            namespace: Namespace of the flow
            flow_id: Flow ID
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            Flow dictionary
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        endpoint = f"/api/v1/{tenant}/flows/{namespace}/{flow_id}"
        response = self.client.get(endpoint, context)
        return response.json()
