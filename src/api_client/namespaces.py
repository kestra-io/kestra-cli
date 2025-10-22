"""Namespaces API endpoints for Kestra."""

from typing import List, Dict, Any, Optional
from src.api_client.client import KestraAPIClient
from src.api_client.auth import AuthContext


class NamespacesAPI:
    """API client for namespaces endpoints."""
    
    def __init__(self, client: KestraAPIClient):
        """Initialize the namespaces API client.
        
        Args:
            client: KestraAPIClient instance
        """
        self.client = client
    
    def list_namespaces(
        self,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """List all namespaces in the Kestra instance.
        
        Args:
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
            query: Optional search query to filter namespaces
            page: Page number (default: 1)
            size: Page size (default: 100)
        
        Returns:
            List of namespace dictionaries
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        endpoint = f"/api/v1/{tenant}/namespaces/search"
        
        # Build query parameters
        params = {
            "page": page,
            "size": size
        }
        if query:
            params["q"] = query
        
        response = self.client.get(endpoint, context, params=params)
        data = response.json()
        
        # Return the results from the paginated response
        return data.get("results", [])

