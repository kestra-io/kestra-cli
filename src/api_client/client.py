"""Base API client for Kestra."""

import httpx
from typing import Dict, Any, Optional
from .auth import AuthManager, AuthContext


class KestraAPIClient:
    """Base API client for Kestra."""
    
    def __init__(self, auth_manager: Optional[AuthManager] = None):
        """Initialize the API client.
        
        Args:
            auth_manager: AuthManager instance. If None, creates a new one.
        """
        self.auth_manager = auth_manager or AuthManager()
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self, context: Optional[AuthContext] = None) -> httpx.Client:
        """Get or create an HTTP client with authentication.
        
        Args:
            context: Auth context to use. If None, uses default context.
        
        Returns:
            Configured httpx.Client instance.
        """
        if context is None:
            context = self.auth_manager.get_context()
            if context is None:
                raise ValueError("No authentication context found. Please configure authentication.")
        
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            auth = None
            
            # Add authentication header
            if context.auth_method == "token" and context.token:
                headers["Authorization"] = f"Bearer {context.token}"
            elif context.auth_method == "username_password":
                # For basic auth, we'll use httpx's auth parameter
                auth = (context.username, context.password) if context.username and context.password else None
            
            self._client = httpx.Client(
                base_url=context.host,
                headers=headers,
                auth=auth,
                timeout=30.0
            )
        
        return self._client
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        context: Optional[AuthContext] = None,
        **kwargs
    ) -> httpx.Response:
        """Make an HTTP request to the Kestra API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            context: Auth context to use
            **kwargs: Additional arguments for httpx request
        
        Returns:
            httpx.Response object
        
        Raises:
            httpx.HTTPError: If the request fails
        """
        client = self._get_client(context)
        
        # Build full URL, handling trailing slashes properly
        base_url = str(client.base_url).rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}"
        
        try:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            # Add more detailed error information
            error_msg = f"API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.text
                    error_msg += f"\nResponse body: {error_body}"
                except:
                    pass
            raise httpx.HTTPError(error_msg)
    
    def get(self, endpoint: str, context: Optional[AuthContext] = None, **kwargs) -> httpx.Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, context, **kwargs)
    
    def post(self, endpoint: str, context: Optional[AuthContext] = None, **kwargs) -> httpx.Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, context, **kwargs)
    
    def put(self, endpoint: str, context: Optional[AuthContext] = None, **kwargs) -> httpx.Response:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, context, **kwargs)
    
    def delete(self, endpoint: str, context: Optional[AuthContext] = None, **kwargs) -> httpx.Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, context, **kwargs)
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
