"""
Integrations Module
Provides integration classes for various external services
"""

from src.integrations.base import (
    BaseIntegration,
    EmailIntegration,
    CalendarIntegration,
    PaymentIntegration,
    TaskIntegration,
    MessagingIntegration,
    WebhookIntegration
)

from src.integrations.gmail import GmailIntegration
from src.integrations.google_calendar import GoogleCalendarIntegration
from src.integrations.stripe import StripeIntegration
from src.integrations.slack import SlackIntegration

__all__ = [
    # Base classes
    'BaseIntegration',
    'EmailIntegration',
    'CalendarIntegration',
    'PaymentIntegration',
    'TaskIntegration',
    'MessagingIntegration',
    'WebhookIntegration',
    
    # Service implementations
    'GmailIntegration',
    'GoogleCalendarIntegration',
    'StripeIntegration',
    'SlackIntegration',
]

# Service registry for dynamic loading
INTEGRATION_REGISTRY = {
    'gmail': GmailIntegration,
    'google_calendar': GoogleCalendarIntegration,
    'stripe': StripeIntegration,
    'slack': SlackIntegration,
}


def get_integration_class(service_name: str):
    """
    Get integration class by service name
    
    Args:
        service_name: Name of the service (e.g., 'gmail', 'stripe')
    
    Returns:
        Integration class or None if not found
    """
    return INTEGRATION_REGISTRY.get(service_name.lower())


def create_integration(service_name: str, credentials: dict = None):
    """
    Create an integration instance
    
    Args:
        service_name: Name of the service
        credentials: Configuration/credentials dictionary
    
    Returns:
        Integration instance or None if service not found
    """
    integration_class = get_integration_class(service_name)
    if integration_class:
        return integration_class(credentials)
    return None
