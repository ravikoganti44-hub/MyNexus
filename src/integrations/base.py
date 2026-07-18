"""
Integration framework base classes
Supports connecting to external services like Gmail, Google Calendar, Stripe, PayPal, etc.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config.integration_urls import get_service_by_name, ALL_SERVICES

logger = logging.getLogger(__name__)


class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_synced = None
        self.service_info = None
        self._get_service_info()
    
    def _get_service_info(self):
        """Get service information from URLs config"""
        service_name = self.config.get('service_name')
        if service_name:
            self.service_info = get_service_by_name(service_name)
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the external service"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the external service"""
        pass
    
    @abstractmethod
    def sync(self) -> bool:
        """Sync data with the external service"""
        pass
    
    def update_sync_time(self):
        """Update last synced time"""
        self.last_synced = datetime.now()
    
    def get_api_url(self) -> Optional[str]:
        """Get API base URL from service info"""
        if self.service_info:
            return self.service_info.get("api_url")
        return None
    
    def get_documentation_url(self) -> Optional[str]:
        """Get documentation URL"""
        if self.service_info:
            return self.service_info.get("documentation")
        return None
    
    def get_setup_guide_url(self) -> Optional[str]:
        """Get setup guide URL"""
        if self.service_info:
            return self.service_info.get("setup_guide")
        return None
    
    def get_oauth_url(self) -> Optional[str]:
        """Get OAuth authorization URL"""
        if self.service_info:
            return self.service_info.get("oauth_url")
        return None


class EmailIntegration(BaseIntegration):
    """Email service integration"""
    
    def connect(self) -> bool:
        service_name = self.config.get('service_name', 'Unknown')
        logger.info(f"Connecting to email service: {service_name}")
        logger.info(f"API URL: {self.get_api_url()}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Disconnected from email service")
        return True
    
    def sync(self) -> bool:
        logger.info("Syncing emails...")
        logger.info(f"API Endpoint: {self.get_api_url()}")
        self.update_sync_time()
        return True


class CalendarIntegration(BaseIntegration):
    """Calendar service integration"""
    
    def connect(self) -> bool:
        service_name = self.config.get('service_name', 'Unknown')
        logger.info(f"Connecting to calendar: {service_name}")
        logger.info(f"API URL: {self.get_api_url()}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Disconnected from calendar service")
        return True
    
    def sync(self) -> bool:
        logger.info("Syncing calendar events...")
        logger.info(f"API Endpoint: {self.get_api_url()}")
        self.update_sync_time()
        return True


class PaymentIntegration(BaseIntegration):
    """Payment service integration"""
    
    def connect(self) -> bool:
        service_name = self.config.get('service_name', 'Unknown')
        logger.info(f"Connecting to payment service: {service_name}")
        logger.info(f"API URL: {self.get_api_url()}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Disconnected from payment service")
        return True
    
    def sync(self) -> bool:
        logger.info("Syncing payment data...")
        logger.info(f"API Endpoint: {self.get_api_url()}")
        self.update_sync_time()
        return True


class TaskIntegration(BaseIntegration):
    """Task management service integration"""
    
    def connect(self) -> bool:
        service_name = self.config.get('service_name', 'Unknown')
        logger.info(f"Connecting to task service: {service_name}")
        logger.info(f"API URL: {self.get_api_url()}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Disconnected from task service")
        return True
    
    def sync(self) -> bool:
        logger.info("Syncing tasks...")
        logger.info(f"API Endpoint: {self.get_api_url()}")
        self.update_sync_time()
        return True


class MessagingIntegration(BaseIntegration):
    """Messaging service integration (Slack, Teams, Discord, Telegram)"""
    
    def connect(self) -> bool:
        service_name = self.config.get('service_name', 'Unknown')
        logger.info(f"Connecting to messaging service: {service_name}")
        logger.info(f"API URL: {self.get_api_url()}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Disconnected from messaging service")
        return True
    
    def sync(self) -> bool:
        logger.info("Syncing messages...")
        logger.info(f"API Endpoint: {self.get_api_url()}")
        self.update_sync_time()
        return True


class WebhookIntegration(BaseIntegration):
    """Generic webhook integration"""
    
    def connect(self) -> bool:
        webhook_url = self.config.get('webhook_url')
        logger.info(f"Configuring webhook: {webhook_url}")
        return True
    
    def disconnect(self) -> bool:
        logger.info("Webhook integration disconnected")
        return True
    
    def sync(self) -> bool:
        logger.info("Webhook integration ready to send events")
        self.update_sync_time()
        return True
