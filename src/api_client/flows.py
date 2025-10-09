"""Flows API endpoints for Kestra."""

from typing import List, Dict, Any, Optional, Tuple
import yaml
from src.api_client.client import KestraAPIClient
from src.api_client.auth import AuthContext


def parse_flow_yaml(yaml_content: str) -> Tuple[str, str]:
    """Parse YAML content and extract flow ID and namespace.
    
    Args:
        yaml_content: YAML content of the flow
    
    Returns:
        Tuple of (namespace, flow_id)
    
    Raises:
        ValueError: If id or namespace is missing from the YAML
        yaml.YAMLError: If the YAML is invalid
    """
    try:
        flow_data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML content: {e}")
    
    if not isinstance(flow_data, dict):
        raise ValueError("YAML content must be a dictionary")
    
    flow_id = flow_data.get("id")
    namespace = flow_data.get("namespace")
    
    if not flow_id:
        raise ValueError("Flow YAML must contain an 'id' field")
    if not namespace:
        raise ValueError("Flow YAML must contain a 'namespace' field")
    
    return namespace, flow_id


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
    
    def flow_exists(
        self,
        namespace: str,
        flow_id: str,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None
    ) -> bool:
        """Check if a flow exists.
        
        Args:
            namespace: Namespace of the flow
            flow_id: Flow ID
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
        
        Returns:
            True if the flow exists, False otherwise
        """
        try:
            self.get_flow(namespace, flow_id, tenant, context)
            return True
        except Exception:
            return False
    
    def create_flow(
        self,
        yaml_content: str,
        tenant: Optional[str] = None,
        context: Optional[AuthContext] = None,
        override: bool = False
    ) -> Dict[str, Any]:
        """Create or update a flow from YAML content.
        
        Args:
            yaml_content: YAML content of the flow
            tenant: Tenant name. If None, uses tenant from context
            context: Auth context to use
            override: If True, updates the flow if it exists. If False, raises error if flow exists.
        
        Returns:
            Created or updated flow dictionary
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If flow exists and override is False
        """
        if context is None:
            context = self.client.auth_manager.get_context()
        
        if tenant is None:
            tenant = context.tenant if context else "main"
        
        # Parse YAML to get namespace and flow ID
        namespace, flow_id = parse_flow_yaml(yaml_content)
        
        # Check if flow exists
        exists = self.flow_exists(namespace, flow_id, tenant, context)
        
        if exists and not override:
            raise ValueError(
                f"Flow '{flow_id}' already exists in namespace '{namespace}'. "
                "Use --override to update the existing flow."
            )
        
        # Determine endpoint and method
        if exists and override:
            # Update existing flow
            endpoint = f"/api/v1/{tenant}/flows/{namespace}/{flow_id}"
            response = self.client.put(
                endpoint,
                context,
                content=yaml_content,
                headers={"Content-Type": "application/x-yaml"}
            )
        else:
            # Create new flow
            endpoint = f"/api/v1/{tenant}/flows"
            response = self.client.post(
                endpoint,
                context,
                content=yaml_content,
                headers={"Content-Type": "application/x-yaml"}
            )
        
        return response.json()