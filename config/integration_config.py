#!/usr/bin/env python3
"""
Integration Configuration and Setup
Handles OAuth flows and API credential management for all external services
"""
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from config.integration_urls import get_service_by_name, get_services_by_category


@dataclass
class IntegrationConfig:
    """Configuration for external service integration"""
    service_name: str
    service_type: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_url: Optional[str] = None
    custom_url: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None  # Only for basic auth, use with caution
    oauth_scope: Optional[str] = None
    extra_params: Dict[str, Any] = None


class IntegrationSetup:
    """Helper class for setting up integrations"""

    @staticmethod
    def get_oauth_url(service_name: str, redirect_uri: str = "http://localhost:8080/callback") -> str:
        """Get OAuth authorization URL for a service"""
        service = get_service_by_name(service_name)
        if not service:
            return None
        
        oauth_url = service.get("oauth_url")
        if not oauth_url:
            return None
        
        # Build OAuth parameters
        params = [
            f"response_type=code",
            f"redirect_uri={redirect_uri}",
            f"state=random_state_value"  # Should be random
        ]
        
        if "client_id" in service:
            params.append(f"client_id={service['client_id']}")
        
        return oauth_url + "?" + "&".join(params)

    @staticmethod
    def get_service_info(service_name: str) -> Dict[str, Any]:
        """Get complete information about a service"""
        return get_service_by_name(service_name)

    @staticmethod
    def get_api_url(service_name: str) -> str:
        """Get API base URL for a service"""
        service = get_service_by_name(service_name)
        if not service:
            return None
        return service.get("api_url")

    @staticmethod
    def get_documentation_url(service_name: str) -> str:
        """Get documentation URL for a service"""
        service = get_service_by_name(service_name)
        if not service:
            return None
        return service.get("documentation")

    @staticmethod
    def get_setup_guide_url(service_name: str) -> str:
        """Get setup guide URL for a service"""
        service = get_service_by_name(service_name)
        if not service:
            return None
        return service.get("setup_guide")


class IntegrationManager:
    """Manage integration configurations"""

    def __init__(self):
        self.integrations = {}

    def add_integration(self, config: IntegrationConfig) -> bool:
        """Add a new integration"""
        key = f"{config.service_type}_{config.service_name}"
        self.integrations[key] = config
        return True

    def get_integration(self, service_type: str, service_name: str) -> Optional[IntegrationConfig]:
        """Get integration configuration"""
        key = f"{service_type}_{service_name}"
        return self.integrations.get(key)

    def list_integrations(self, service_type: Optional[str] = None) -> list:
        """List all integrations, optionally filtered by type"""
        if service_type:
            prefix = f"{service_type}_"
            return [cfg for key, cfg in self.integrations.items() if key.startswith(prefix)]
        return list(self.integrations.values())

    def remove_integration(self, service_type: str, service_name: str) -> bool:
        """Remove an integration"""
        key = f"{service_type}_{service_name}"
        if key in self.integrations:
            del self.integrations[key]
            return True
        return False

    def export_configs(self) -> str:
        """Export configurations as JSON"""
        data = {}
        for key, config in self.integrations.items():
            data[key] = {
                "service_name": config.service_name,
                "service_type": config.service_type,
                "email": config.email,
                "webhook_url": config.webhook_url,
                # Don't export sensitive tokens
            }
        return json.dumps(data, indent=2)


# Global integration manager
_manager = IntegrationManager()


def get_integration_manager() -> IntegrationManager:
    """Get the global integration manager"""
    return _manager
