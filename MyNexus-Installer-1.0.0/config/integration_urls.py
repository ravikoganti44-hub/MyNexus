"""
Integration URLs and Configuration
Central repository for all external service endpoints and authentication URLs
"""

# ============================================================================
# EMAIL INTEGRATIONS
# ============================================================================

EMAIL_SERVICES = {
    "gmail": {
        "name": "Gmail",
        "base_url": "https://mail.google.com",
        "api_url": "https://www.googleapis.com/gmail/v1",
        "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send"
        ],
        "documentation": "https://developers.google.com/gmail/api",
        "setup_guide": "https://support.google.com/accounts/answer/185833"
    },
    "outlook": {
        "name": "Outlook / Microsoft 365",
        "base_url": "https://outlook.office.com",
        "api_url": "https://graph.microsoft.com/v1.0",
        "oauth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": [
            "Mail.Read",
            "Mail.Send"
        ],
        "documentation": "https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview",
        "setup_guide": "https://support.microsoft.com/en-us/account-billing/sign-in-to-outlook-com"
    },
    "imap": {
        "name": "Generic IMAP (Thunderbird, Apple Mail, etc.)",
        "imap_server": "mail.{domain}.com",
        "imap_port": 993,
        "smtp_server": "smtp.{domain}.com",
        "smtp_port": 587,
        "documentation": "https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol",
        "common_servers": {
            "icloud": {"imap": "imap.mail.me.com", "smtp": "smtp.mail.me.com"},
            "yahoo": {"imap": "imap.mail.yahoo.com", "smtp": "smtp.mail.yahoo.com"},
            "aol": {"imap": "imap.aol.com", "smtp": "smtp.aol.com"},
        }
    }
}

# ============================================================================
# CALENDAR INTEGRATIONS
# ============================================================================

CALENDAR_SERVICES = {
    "google_calendar": {
        "name": "Google Calendar",
        "base_url": "https://calendar.google.com",
        "api_url": "https://www.googleapis.com/calendar/v3",
        "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ],
        "documentation": "https://developers.google.com/calendar/api",
        "setup_guide": "https://support.google.com/calendar/answer/99358"
    },
    "outlook_calendar": {
        "name": "Outlook Calendar",
        "base_url": "https://outlook.office.com/calendar",
        "api_url": "https://graph.microsoft.com/v1.0",
        "oauth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": [
            "Calendars.Read",
            "Calendars.ReadWrite"
        ],
        "documentation": "https://docs.microsoft.com/en-us/graph/api/resources/calendar",
        "setup_guide": "https://support.microsoft.com/en-us/office/calendar-sync"
    },
    "ical": {
        "name": "iCalendar (CalDAV)",
        "protocol": "CalDAV",
        "port": 443,
        "documentation": "https://en.wikipedia.org/wiki/CalDAV",
        "common_servers": {
            "apple": {"url": "https://caldav.icloud.com/"},
            "nextcloud": {"url": "https://nextcloud.example.com/remote.php/dav/"},
            "owncloud": {"url": "https://owncloud.example.com/remote.php/dav/"},
        }
    }
}

# ============================================================================
# PAYMENT & BANKING INTEGRATIONS
# ============================================================================

PAYMENT_SERVICES = {
    "stripe": {
        "name": "Stripe",
        "base_url": "https://stripe.com",
        "api_url": "https://api.stripe.com/v1",
        "webhook_url": "https://api.stripe.com/v1/webhook_endpoints",
        "documentation": "https://stripe.com/docs/api",
        "dashboard": "https://dashboard.stripe.com",
        "api_key_location": "Dashboard → Developers → API keys",
        "setup_guide": "https://stripe.com/docs/keys"
    },
    "paypal": {
        "name": "PayPal",
        "base_url": "https://www.paypal.com",
        "api_url": "https://api.paypal.com/v1",
        "sandbox_url": "https://api.sandbox.paypal.com/v1",
        "oauth_url": "https://www.paypal.com/signin/authorize",
        "documentation": "https://developer.paypal.com/docs/api/overview/",
        "dashboard": "https://developer.paypal.com",
        "setup_guide": "https://developer.paypal.com/docs/platforms/get-started/"
    },
    "square": {
        "name": "Square",
        "base_url": "https://squareup.com",
        "api_url": "https://connect.squareup.com/v2",
        "documentation": "https://developer.squareup.com/docs",
        "dashboard": "https://squareup.com/dashboard",
        "setup_guide": "https://developer.squareup.com/docs/build-basics"
    },
    "plaid": {
        "name": "Plaid (Banking)",
        "base_url": "https://plaid.com",
        "api_url": "https://api.plaid.com",
        "sandbox_url": "https://sandbox.plaid.com",
        "documentation": "https://plaid.com/docs/api/overview/",
        "dashboard": "https://dashboard.plaid.com",
        "setup_guide": "https://plaid.com/docs/quickstart/"
    }
}

# ============================================================================
# TASK MANAGEMENT INTEGRATIONS
# ============================================================================

TASK_SERVICES = {
    "todoist": {
        "name": "Todoist",
        "base_url": "https://todoist.com",
        "api_url": "https://api.todoist.com/rest/v2",
        "oauth_url": "https://todoist.com/oauth/authorize",
        "token_url": "https://todoist.com/oauth/access_token",
        "documentation": "https://developer.todoist.com/rest/v2/",
        "dashboard": "https://todoist.com/app",
        "setup_guide": "https://developer.todoist.com/guides/quickstart"
    },
    "asana": {
        "name": "Asana",
        "base_url": "https://asana.com",
        "api_url": "https://app.asana.com/api/1.0",
        "oauth_url": "https://app.asana.com/-/oauth_authorize",
        "token_url": "https://app.asana.com/-/oauth_token",
        "documentation": "https://developers.asana.com/docs",
        "dashboard": "https://app.asana.com",
        "setup_guide": "https://developers.asana.com/docs/personal-access-token"
    },
    "notion": {
        "name": "Notion",
        "base_url": "https://notion.so",
        "api_url": "https://api.notion.com/v1",
        "oauth_url": "https://api.notion.com/v1/oauth/authorize",
        "token_url": "https://api.notion.com/v1/oauth/token",
        "documentation": "https://developers.notion.com/reference/intro",
        "dashboard": "https://www.notion.so/integrations",
        "setup_guide": "https://developers.notion.com/docs/getting-started/overview"
    },
    "trello": {
        "name": "Trello",
        "base_url": "https://trello.com",
        "api_url": "https://api.trello.com/1",
        "authorization_url": "https://trello.com/app-key",
        "documentation": "https://developer.atlassian.com/cloud/trello/rest/api-group-actions/",
        "setup_guide": "https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/"
    }
}

# ============================================================================
# MESSAGING & NOTIFICATION INTEGRATIONS
# ============================================================================

MESSAGING_SERVICES = {
    "slack": {
        "name": "Slack",
        "base_url": "https://slack.com",
        "api_url": "https://slack.com/api",
        "oauth_url": "https://slack.com/oauth_authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": [
            "chat:write",
            "users:read",
            "team:read"
        ],
        "documentation": "https://api.slack.com/docs",
        "setup_guide": "https://api.slack.com/apps"
    },
    "teams": {
        "name": "Microsoft Teams",
        "base_url": "https://teams.microsoft.com",
        "api_url": "https://graph.microsoft.com/v1.0",
        "oauth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "documentation": "https://docs.microsoft.com/en-us/graph/api/resources/chat",
        "setup_guide": "https://docs.microsoft.com/en-us/microsoftteams/platform/tabs/how-to/authentication/auth-aad-sso"
    },
    "discord": {
        "name": "Discord",
        "base_url": "https://discord.com",
        "api_url": "https://discord.com/api/v10",
        "webhook_url": "https://discord.com/api/webhooks/{webhook_id}/{webhook_token}",
        "documentation": "https://discord.com/developers/docs/intro",
        "setup_guide": "https://discord.com/developers/applications"
    },
    "telegram": {
        "name": "Telegram",
        "base_url": "https://telegram.org",
        "bot_api": "https://api.telegram.org/bot{bot_token}/sendMessage",
        "webhook_url": "https://api.telegram.org/bot{bot_token}/setWebhook",
        "documentation": "https://core.telegram.org/bots/api",
        "setup_guide": "https://core.telegram.org/bots#6-botfather"
    }
}

# ============================================================================
# ACCOUNT & EXPENSE TRACKING
# ============================================================================

ACCOUNTING_SERVICES = {
    "quickbooks": {
        "name": "QuickBooks",
        "base_url": "https://quickbooks.intuit.com",
        "api_url": "https://quickbooks.api.intuit.com",
        "oauth_url": "https://appcenter.intuit.com/connect/oauth2",
        "realm_id_required": True,
        "documentation": "https://developer.intuit.com/docs",
        "setup_guide": "https://developer.intuit.com/docs/get-started"
    },
    "freshbooks": {
        "name": "FreshBooks",
        "base_url": "https://www.freshbooks.com",
        "api_url": "https://api.freshbooks.com/accounting_account/account/{account_id}",
        "oauth_url": "https://api.freshbooks.com/oauth/authorize",
        "token_url": "https://api.freshbooks.com/oauth/token",
        "documentation": "https://www.freshbooks.com/api/start",
        "setup_guide": "https://www.freshbooks.com/api/tutorials"
    },
    "xero": {
        "name": "Xero",
        "base_url": "https://www.xero.com",
        "api_url": "https://api.xero.com/api.xro/2.0",
        "oauth_url": "https://login.xero.com/identity/connect/authorize",
        "token_url": "https://identity.xero.com/connect/token",
        "documentation": "https://developer.xero.com/documentation/",
        "setup_guide": "https://developer.xero.com/documentation/getting-started/"
    }
}

# ============================================================================
# UTILITIES & CONFIGURATION MANAGEMENT
# ============================================================================

UTILITY_SERVICES = {
    "webhooks": {
        "name": "Custom Webhooks",
        "description": "Send HTTP POST requests to custom endpoints",
        "example_url": "https://example.com/webhook/activity-reminder",
        "http_methods": ["POST", "PUT", "GET"],
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer {api_key}"
        },
        "documentation": "https://en.wikipedia.org/wiki/Webhook"
    },
    "ifttt": {
        "name": "IFTTT",
        "base_url": "https://ifttt.com",
        "api_url": "https://maker.ifttt.com",
        "webhook_url": "https://maker.ifttt.com/trigger/{event}/with/key/{key}",
        "setup_guide": "https://help.ifttt.com/hc/en-us/articles/115000968612"
    },
    "zapier": {
        "name": "Zapier",
        "base_url": "https://zapier.com",
        "api_url": "https://api.zapier.com/v1",
        "webhook_url": "https://hooks.zapier.com/hooks/catch/{zapier_id}/",
        "documentation": "https://zapier.com/page/webhooks/",
        "setup_guide": "https://zapier.com/help/docs/get-started/"
    }
}

# ============================================================================
# GLOBAL CONFIGURATION & DEFAULTS
# ============================================================================

DEFAULT_ENDPOINTS = {
    "timeout": 30,  # seconds
    "retry_attempts": 3,
    "retry_delay": 5,  # seconds
    "rate_limit_delay": 1,  # seconds between requests
}

# HTTP Headers for API requests
DEFAULT_HEADERS = {
    "User-Agent": "ProJ-Connect/1.0.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ============================================================================
# OAUTH COMMON PARAMETERS
# ============================================================================

OAUTH_COMMON_PARAMS = {
    "response_type": "code",
    "state": "{random_state}",  # Should be random for security
    "redirect_uri": "http://localhost:8080/callback",  # Local redirect URI
}

# ============================================================================
# COMPLETE SERVICE DIRECTORY
# ============================================================================

ALL_SERVICES = {
    "email": EMAIL_SERVICES,
    "calendar": CALENDAR_SERVICES,
    "payment": PAYMENT_SERVICES,
    "tasks": TASK_SERVICES,
    "messaging": MESSAGING_SERVICES,
    "accounting": ACCOUNTING_SERVICES,
    "utilities": UTILITY_SERVICES,
}


def get_service_by_name(name: str) -> dict:
    """Get service configuration by name"""
    for category in ALL_SERVICES.values():
        if name.lower() in category:
            return category[name.lower()]
    return None


def get_all_service_names() -> list:
    """Get list of all available service names"""
    names = []
    for category in ALL_SERVICES.values():
        names.extend(category.keys())
    return sorted(names)


def get_services_by_category(category: str) -> dict:
    """Get all services in a category"""
    return ALL_SERVICES.get(category.lower(), {})


# ============================================================================
# INTEGRATION URLS CLASS - Facade for accessing service configurations
# ============================================================================

class IntegrationURLs:
    """Facade class providing access to integration URLs and configurations"""
    
    @staticmethod
    def get_service_by_name(name: str) -> dict:
        """Get service configuration by name"""
        return get_service_by_name(name)
    
    @staticmethod
    def get_all_service_names() -> list:
        """Get list of all available service names"""
        return get_all_service_names()
    
    @staticmethod
    def get_services_by_category(category: str) -> dict:
        """Get all services in a category"""
        return get_services_by_category(category)
    
    @staticmethod
    def get_all_services() -> dict:
        """Get all services organized by category"""
        return ALL_SERVICES


# Create singleton instance for easy importing
INTEGRATION_URLS = IntegrationURLs()
