"""Authentication management for Kestra CLI."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class AuthContext:
    """Represents an authentication context."""
    name: str
    host: str
    tenant: str
    auth_method: str  # 'token' or 'username_password'
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class AuthManager:
    """Manages authentication contexts and credentials."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the auth manager.
        
        Args:
            config_dir: Custom config directory path. Defaults to ~/.kestra
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".kestra"
        
        self.config_file = self.config_dir / "config"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {"contexts": {}, "default_context": None}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"contexts": {}, "default_context": None}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def add_context(self, context: AuthContext):
        """Add or update an authentication context."""
        config = self.load_config()
        config["contexts"][context.name] = {
            "host": context.host,
            "tenant": context.tenant,
            "auth_method": context.auth_method,
            "token": context.token,
            "username": context.username,
            "password": context.password,
        }
        self.save_config(config)
    
    def get_context(self, name: Optional[str] = None) -> Optional[AuthContext]:
        """Get an authentication context by name.
        
        Args:
            name: Context name. If None, returns the default context.
        
        Returns:
            AuthContext if found, None otherwise.
        """
        config = self.load_config()
        
        if name is None:
            name = config.get("default_context")
            if not name:
                return None
        
        context_data = config.get("contexts", {}).get(name)
        if not context_data:
            return None
        
        return AuthContext(
            name=name,
            host=context_data["host"],
            tenant=context_data["tenant"],
            auth_method=context_data["auth_method"],
            token=context_data.get("token"),
            username=context_data.get("username"),
            password=context_data.get("password"),
        )
    
    def set_default_context(self, name: str):
        """Set the default context."""
        config = self.load_config()
        if name not in config.get("contexts", {}):
            raise ValueError(f"Context '{name}' does not exist")
        
        config["default_context"] = name
        self.save_config(config)
    
    def list_contexts(self) -> Dict[str, AuthContext]:
        """List all available contexts."""
        config = self.load_config()
        contexts = {}
        
        for name, data in config.get("contexts", {}).items():
            contexts[name] = AuthContext(
                name=name,
                host=data["host"],
                tenant=data["tenant"],
                auth_method=data["auth_method"],
                token=data.get("token"),
                username=data.get("username"),
                password=data.get("password"),
            )
        
        return contexts
    
    def delete_context(self, name: str):
        """Delete a context."""
        config = self.load_config()
        if name in config.get("contexts", {}):
            del config["contexts"][name]
            if config.get("default_context") == name:
                config["default_context"] = None
            self.save_config(config)
