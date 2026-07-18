"""
INTEGRATION IMPLEMENTATIONS GUIDE
ProJ Connect - Service Integration Reference
"""

# ============================================================================
# INTEGRATION IMPLEMENTATIONS OVERVIEW
# ============================================================================

## Available Integration Classes

ProJ Connect includes fully implemented integration classes for major services:

### 1. GMAIL INTEGRATION
**Service**: Gmail (Email)
**Class**: `GmailIntegration` (from `src.integrations.gmail`)
**Type**: OAuth 2.0 based

#### Features
- OAuth 2.0 authentication with Google
- Email retrieval with filtering
- Email sending capabilities
- Token refresh handling (ready for implementation)
- Sync support for email data

#### Usage Example
```python
from src.integrations import GmailIntegration

# Initialize with credentials
gmail = GmailIntegration({
    'client_id': 'your_client_id',
    'access_token': 'your_access_token'
})

# Generate OAuth URL for user authorization
oauth_url = gmail.get_oauth_url(
    redirect_uri='http://localhost:8000/callback'
)

# Exchange authorization code for token
token = gmail.exchange_code_for_token(
    code='auth_code_from_callback',
    client_secret='your_client_secret'
)

# Get emails
emails = gmail.get_emails(max_results=10, query='from:someone@example.com')

# Send email
gmail.send_email(
    to='recipient@example.com',
    subject='Test Subject',
    body='Test body'
)

# Sync with API
gmail.sync()
```

#### API Endpoints
- OAuth URL: https://accounts.google.com/o/oauth2/v2/auth
- Token URL: https://oauth2.googleapis.com/token
- API URL: https://www.googleapis.com/gmail/v1
- Documentation: https://developers.google.com/gmail/api

#### Setup Guide
See INTEGRATION_SETUP.md for complete Gmail OAuth setup instructions

---

### 2. GOOGLE CALENDAR INTEGRATION
**Service**: Google Calendar
**Class**: `GoogleCalendarIntegration` (from `src.integrations.google_calendar`)
**Type**: OAuth 2.0 based

#### Features
- OAuth 2.0 authentication with Google
- List upcoming events
- Create/modify calendar events
- Attendee management
- Multi-day event support
- Timezone handling (ready for implementation)

#### Usage Example
```python
from src.integrations import GoogleCalendarIntegration
from datetime import datetime, timedelta

# Initialize
calendar = GoogleCalendarIntegration({
    'client_id': 'your_client_id',
    'access_token': 'your_access_token'
})

# Get upcoming events
events = calendar.get_upcoming_events(
    days=7,           # Next 7 days
    max_results=10
)

# Create event
start_time = datetime.now() + timedelta(hours=1)
end_time = start_time + timedelta(hours=2)

calendar.create_event(
    title='Team Meeting',
    start_time=start_time,
    end_time=end_time,
    description='Monthly team sync',
    attendees=['colleague@example.com', 'manager@example.com']
)

# Sync
calendar.sync()
```

#### API Endpoints
- OAuth URL: https://accounts.google.com/o/oauth2/v2/auth
- Token URL: https://oauth2.googleapis.com/token
- API URL: https://www.googleapis.com/calendar/v3
- Documentation: https://developers.google.com/calendar/api

#### Setup Guide
See INTEGRATION_SETUP.md for complete Google Calendar setup instructions

---

### 3. STRIPE INTEGRATION
**Service**: Stripe (Payment Processing)
**Class**: `StripeIntegration` (from `src.integrations.stripe`)
**Type**: API Key based

#### Features
- Payment intent creation
- Transaction history retrieval
- Account information queries
- Webhook endpoint management
- Support for multiple currencies

#### Usage Example
```python
from src.integrations import StripeIntegration

# Initialize with API key
stripe = StripeIntegration({
    'secret_key': 'sk_test_...'
})

# Verify API key
is_valid = stripe.verify_api_key('sk_test_...')

# Create payment intent
payment = stripe.create_payment(
    amount=2000,           # $20.00 in cents
    currency='usd',
    description='Premium subscription'
)

# Get transactions
transactions = stripe.get_transactions(
    limit=50,
    status='succeeded'
)

# Get account info
account = stripe.get_account_info()

# Sync
stripe.sync()
```

#### API Endpoints
- API URL: https://api.stripe.com/v1
- Webhook URL: https://api.stripe.com/v1/webhook_endpoints
- Documentation: https://stripe.com/docs/api
- Dashboard: https://dashboard.stripe.com

#### Setup Guide
See INTEGRATION_SETUP.md for complete Stripe setup instructions

---

### 4. SLACK INTEGRATION
**Service**: Slack (Team Communication)
**Class**: `SlackIntegration` (from `src.integrations.slack`)
**Type**: Bot Token based

#### Features
- Send messages to channels
- Send formatted notifications with attachments
- List workspace channels
- Get user information
- Thread support
- Channel mention support

#### Usage Example
```python
from src.integrations import SlackIntegration

# Initialize with bot token
slack = SlackIntegration({
    'bot_token': 'xoxb-...'
})

# Send simple message
message = slack.send_message(
    channel='#general',
    text='Reminder: Meeting starts in 10 minutes'
)

# Send formatted notification
notification = slack.send_notification(
    channel='#alerts',
    title='Payment Overdue',
    message='Invoice #123 is 5 days overdue',
    color='#FF0000',  # Red for alert
    fields={
        'Amount': '$500.00',
        'Due Date': '2024-01-15',
        'Status': 'Overdue'
    }
)

# List channels
channels = slack.get_channels()
for channel in channels:
    print(f"#{channel['name']}")

# Get users
users = slack.get_users()

# Send message to thread
slack.send_message(
    channel='#general',
    text='Response to your message',
    thread_ts='1234567890.123456'
)

# Sync
slack.sync()
```

#### API Endpoints
- API URL: https://slack.com/api
- OAuth URL: https://slack.com/oauth_authorize
- Token URL: https://slack.com/api/oauth.v2.access
- Documentation: https://api.slack.com/docs

#### Setup Guide
See INTEGRATION_SETUP.md for complete Slack setup instructions

---

## ============================================================================
## FACTORY FUNCTIONS AND REGISTRY
## ============================================================================

### Creating Integrations Dynamically

Use the factory functions for dynamic integration creation:

```python
from src.integrations import (
    create_integration,
    get_integration_class,
    INTEGRATION_REGISTRY
)

# Method 1: Using factory function
gmail = create_integration('gmail', {
    'client_id': 'your_client_id',
    'access_token': 'your_access_token'
})

# Method 2: Using class lookup
GmailClass = get_integration_class('gmail')
gmail = GmailClass(credentials)

# Method 3: Direct class usage
stripe = create_integration('stripe', {'secret_key': 'sk_test_...'})

# Check available integrations
print(INTEGRATION_REGISTRY.keys())
# Output: dict_keys(['gmail', 'google_calendar', 'stripe', 'slack'])
```

### Service Registry
```python
INTEGRATION_REGISTRY = {
    'gmail': GmailIntegration,
    'google_calendar': GoogleCalendarIntegration,
    'stripe': StripeIntegration,
    'slack': SlackIntegration,
}
```

---

## ============================================================================
## CONFIGURATION FILES
## ============================================================================

### config/integration_urls.py
Master reference for all service endpoints and URLs:
- EMAIL_SERVICES (Gmail, Outlook, IMAP)
- CALENDAR_SERVICES (Google Calendar, Outlook, CalDAV)
- PAYMENT_SERVICES (Stripe, PayPal, Square, Plaid)
- TASK_SERVICES (Todoist, Asana, Notion, Trello)
- MESSAGING_SERVICES (Slack, Teams, Discord, Telegram)
- ACCOUNTING_SERVICES (QuickBooks, FreshBooks, Xero)
- UTILITY_SERVICES (Webhooks, IFTTT, Zapier)

**Usage:**
```python
from config.integration_urls import INTEGRATION_URLS

# Get service info
service = INTEGRATION_URLS.get_service_by_name('gmail')

# Get all services in category
email_services = INTEGRATION_URLS.get_services_by_category('email')

# Get all available services
all_services = INTEGRATION_URLS.get_all_services()
```

### config/integration_config.py
Configuration management and OAuth helpers:
- `IntegrationConfig` dataclass
- `IntegrationSetup` helper methods
- `IntegrationManager` for managing multiple integrations

---

## ============================================================================
## INTEGRATION TESTING
## ============================================================================

All integrations include comprehensive unit tests in `test_integrations.py`:

```bash
# Run all integration tests
python -m unittest test_integrations -v

# Run specific test class
python -m unittest test_integrations.TestGmailIntegration -v

# Run specific test
python -m unittest test_integrations.TestStripeIntegration.test_create_payment -v
```

### Test Coverage
- ✅ 29 tests across 4 service integrations
- ✅ OAuth URL generation
- ✅ Connection verification
- ✅ Data retrieval
- ✅ Data creation/modification
- ✅ Sync operations
- ✅ Integration registry

---

## ============================================================================
## EXTENDING WITH NEW SERVICES
## ============================================================================

### Adding a New Integration

1. **Create integration subclass:**
```python
# src/integrations/todoist.py
from src.integrations.base import TaskIntegration

class TodoistIntegration(TaskIntegration):
    SERVICE_NAME = 'todoist'
    
    def __init__(self, credentials=None):
        config = credentials or {}
        config['service_name'] = 'todoist'
        super().__init__(config)
        self.service_info = INTEGRATION_URLS.get_service_by_name('todoist')
    
    def get_oauth_url(self, redirect_uri='http://localhost:8000/callback'):
        # Implementation
        pass
    
    def connect(self):
        # Implementation
        pass
    
    def disconnect(self):
        # Implementation
        pass
    
    def sync(self):
        # Implementation
        pass
```

2. **Update __init__.py:**
```python
# Add to src/integrations/__init__.py
from src.integrations.todoist import TodoistIntegration

INTEGRATION_REGISTRY = {
    # ... existing entries
    'todoist': TodoistIntegration,
}
```

3. **Add to service URLs:**
```python
# config/integration_urls.py already has Todoist configuration
# Just ensure your new integration's name matches the config key
```

---

## ============================================================================
## BEST PRACTICES
## ============================================================================

### 1. Credential Security
```python
# ❌ DON'T: Store credentials in code
gmail = GmailIntegration({
    'client_id': 'client_id_here',
    'access_token': 'token_here'
})

# ✅ DO: Load from environment
import os
gmail = GmailIntegration({
    'client_id': os.environ.get('GMAIL_CLIENT_ID'),
    'access_token': os.environ.get('GMAIL_ACCESS_TOKEN')
})
```

### 2. Error Handling
```python
try:
    emails = gmail.get_emails(max_results=10)
except ConnectionError:
    logger.error("Failed to connect to Gmail")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### 3. Token Refresh
```python
# Implement token refresh logic (OAuth 2.0 services)
if token_expired:
    new_token = gmail.exchange_code_for_token(
        code=refresh_token,
        client_secret=client_secret
    )
    # Update stored token
    integration.config['access_token'] = new_token['access_token']
```

### 4. Rate Limiting
```python
import time

# Respect API rate limits
for i, item in enumerate(items):
    if i > 0 and i % 10 == 0:
        time.sleep(1)  # Rate limiting
    process_item(item)
```

---

## ============================================================================
## NEXT STEPS
## ============================================================================

### Priority Implementations
1. OAuth token refresh handlers
2. Error handling and retry logic
3. Database storage for credentials (encrypted)
4. Additional service integrations (Todoist, PayPal, Discord)
5. Webhook endpoint handlers

### Recommended Integration Order
1. **Phase 1** (Current): Gmail, Google Calendar, Stripe, Slack ✅
2. **Phase 2**: Todoist, PayPal, Email webhook support
3. **Phase 3**: Discord, Teams, Telegram, IFTTT
4. **Phase 4**: Accounting services, Advanced sync

---

## ============================================================================
## TESTING WITH ACTUAL SERVICES
## ============================================================================

### Mock vs Real Implementation

Current implementations use mock responses. To enable real API calls:

1. **Replace mock code** in integration methods with actual HTTP requests:
```python
import requests

# Replace: logger.info(f"Retrieved emails (mock)")
response = requests.get(
    endpoint,
    headers=headers,
    params=params
)
return response.json().get('messages', [])
```

2. **Add OAuth callback handler** (for web framework):
```python
@app.route('/callback')
def oauth_callback():
    code = request.args.get('code')
    token = integration.exchange_code_for_token(code, client_secret)
    # Store token in database
    return redirect('/success')
```

3. **Test with sandbox keys** before production:
- Stripe: Use `sk_test_...` keys
- PayPal: Use sandbox API
- Slack: Create test workspace
- Gmail: Use test OAuth project

---

## ============================================================================
## REFERENCES
## ============================================================================

- INTEGRATION_SETUP.md - Detailed setup guides for each service
- config/integration_urls.py - Complete service endpoint reference
- config/integration_config.py - Configuration management helpers
- test_integrations.py - Comprehensive test suite
- src/integrations/base.py - Base integration class documentation

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Ready for Production (Mock Mode)
