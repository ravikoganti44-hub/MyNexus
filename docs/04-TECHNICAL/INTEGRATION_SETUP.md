# ProJ Connect - Integration Setup Guide

Complete guide for connecting external applications and services to ProJ Connect.

---

## 📧 Email Integrations

### Gmail Setup

**Step 1: Enable Gmail API**
1. Go to: https://developers.google.com/gmail/api
2. Click "Enable the Gmail API"
3. Select "Create a new project"
4. Name it "ProJ Connect"
5. Click "Create Project"

**Step 2: Create OAuth 2.0 Credentials**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth Client ID"
3. Select "Desktop application"
4. Name: "ProJ Connect"
5. Click "Create"

**Step 3: Download Credentials**
1. Click the downloaded credentials file
2. Copy the `client_id` and `client_secret`
3. Enter in ProJ Connect: Integrations → Add Integration → Gmail

**Step 4: Configure in ProJ Connect**
- **Service Type**: Email
- **Service**: Gmail
- **Client ID**: [From credentials]
- **Client Secret**: [From credentials]
- **Redirect URI**: http://localhost:8080/callback

**Key URLs:**
- OAuth: https://accounts.google.com/o/oauth2/v2/auth
- API: https://www.googleapis.com/gmail/v1/users/me/messages
- Documentation: https://developers.google.com/gmail/api

---

### Outlook/Microsoft 365 Setup

**Step 1: Register Application**
1. Go to: https://portal.azure.com/
2. Click "Azure Active Directory → App registrations"
3. Click "New registration"
4. Name: "ProJ Connect"
5. Set Redirect URI: `http://localhost:8080/callback`

**Step 2: Get Credentials**
1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Copy the `client_id` and `client_secret`

**Step 3: Configure in ProJ Connect**
- **Service Type**: Email
- **Service**: Outlook
- **Client ID**: [From Azure]
- **Client Secret**: [From Azure]
- **Tenant ID**: [From Overview page]

**Key URLs:**
- OAuth: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
- API: https://graph.microsoft.com/v1.0/me/messages
- Documentation: https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview

---

### Generic IMAP Email Setup

**For Yahoo, Apple, AOL, or other providers:**

1. Go to your email provider's settings/security
2. Enable "App Passwords" or "Less Secure Accounts"
3. Generate an app-specific password if required

**Step 3: Configure in ProJ Connect**
- **Service Type**: Email
- **Service**: IMAP
- **Email**: your-email@provider.com
- **Username**: your-email@provider.com
- **Password**: [App password]
- **IMAP Server**: [See table below]
- **IMAP Port**: 993 (SSL)
- **SMTP Server**: [See table below]
- **SMTP Port**: 587 (TLS)

**Common IMAP Servers:**

| Provider | IMAP Server | SMTP Server |
|----------|-------------|-------------|
| **Yahoo** | imap.mail.yahoo.com | smtp.mail.yahoo.com |
| **Apple iCloud** | imap.mail.me.com | smtp.mail.me.com |
| **AOL** | imap.aol.com | smtp.aol.com |
| **Gmail (AppPass)** | imap.gmail.com | smtp.gmail.com |

---

## 📅 Calendar Integrations

### Google Calendar Setup

**Step 1: Enable Google Calendar API**
1. Go to: https://developers.google.com/calendar/api
2. Click "Enable the Google Calendar API"

**Step 2: Create OAuth Credentials** (Same as Gmail)
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Desktop credentials
3. Copy `client_id` and `client_secret`

**Step 3: Configure in ProJ Connect**
- **Service Type**: Calendar
- **Service**: Google Calendar
- **Client ID**: [From credentials]
- **Client Secret**: [From credentials]
- **Calendar ID**: primary (or specific calendar)

**Key URLs:**
- OAuth: https://accounts.google.com/o/oauth2/v2/auth
- API: https://www.googleapis.com/calendar/v3/calendars/primary/events
- Documentation: https://developers.google.com/calendar/api

**Calendar IDs:**
- Primary calendar: `primary`
- Specific calendar: found in Calendar Settings → Integrate calendar
- Format: `[calendarID]@group.calendar.google.com`

---

### Outlook Calendar Setup

1. Go to: https://portal.azure.com/
2. Register application (same as Outlook email)
3. Add permission: `Calendars.ReadWrite`

**Configure in ProJ Connect:**
- **Service Type**: Calendar
- **Service**: Outlook Calendar
- **Client ID**: [From Azure]
- **Client Secret**: [From Azure]
- **Tenant ID**: [From Overview]

**Key URLs:**
- API: https://graph.microsoft.com/v1.0/me/events
- Documentation: https://docs.microsoft.com/en-us/graph/api/resources/calendar

---

### CalDAV/iCal Setup (Nextcloud, ownCloud, Apple iCloud)

**For Nextcloud/ownCloud:**

1. Go to Settings → Users → Create App Password
2. Note the app password

**Configure in ProJ Connect:**
- **Service Type**: Calendar
- **Service**: CalDAV
- **URL**: https://your-nextcloud.com/remote.php/dav/
- **Username**: username
- **Password**: app-password
- **Calendar Path**: calendars/username/personal/

**For Apple iCloud:**
- **URL**: https://caldav.icloud.com/
- **Username**: your-apple-id@icloud.com
- **Password**: your-app-specific-password

---

## 💳 Payment & Billing Integrations

### Stripe Setup

**Step 1: Create Account**
1. Go to: https://dashboard.stripe.com/register
2. Create account and verify email

**Step 2: Get API Keys**
1. Go to: https://dashboard.stripe.com/apikeys
2. Copy "Publishable key" and "Secret key"

**Step 3: Create Webhook**
1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. URL: `https://your-domain.com/webhook/stripe`
4. Events: `invoice.payment_succeeded`, `invoice.payment_failed`

**Configure in ProJ Connect:**
- **Service Type**: Payment
- **Service**: Stripe
- **Publishable Key**: [From API Keys]
- **Secret Key**: [From API Keys]
- **Webhook URL**: [Your endpoint]
- **Webhook Secret**: [From webhook details]

**Key URLs:**
- Dashboard: https://dashboard.stripe.com
- API: https://api.stripe.com/v1
- Documentation: https://stripe.com/docs/api

**API Endpoints:**
- Charges: POST https://api.stripe.com/v1/charges
- Invoices: GET https://api.stripe.com/v1/invoices
- Subscriptions: GET https://api.stripe.com/v1/subscriptions

---

### PayPal Setup

**Step 1: Create Developer Account**
1. Go to: https://developer.paypal.com/
2. Sign in or create account
3. Dashboard → Sandbox account

**Step 2: Create App**
1. Go to: https://developer.paypal.com/dashboard/apps/
2. Click "Create App"
3. Name: "ProJ Connect"
4. Type: "Merchant"

**Step 3: Get Credentials**
1. Copy `Client ID` and `Secret`

**Configure in ProJ Connect:**
- **Service Type**: Payment
- **Service**: PayPal
- **Client ID**: [From app]
- **Client Secret**: [From app]
- **Environment**: sandbox or live

**Key URLs:**
- Sandbox: https://api.sandbox.paypal.com/v1
- Production: https://api.paypal.com/v1
- OAuth: https://www.paypal.com/signin/authorize
- Dashboard: https://developer.paypal.com

---

## ✅ Task Management Integrations

### Todoist Setup

**Step 1: Get API Token**
1. Go to: https://todoist.com/app/settings/integrations/developer
2. Click "Create token"
3. Copy the token

**Step 2: Configure in ProJ Connect**
- **Service Type**: Tasks
- **Service**: Todoist
- **API Token**: [Your token]

**Key URLs:**
- API: https://api.todoist.com/rest/v2
- Project list: GET https://api.todoist.com/rest/v2/projects
- Add task: POST https://api.todoist.com/rest/v2/tasks
- Documentation: https://developer.todoist.com/rest/v2/

---

### Asana Setup

**Step 1: Create Personal Access Token**
1. Go to: https://app.asana.com/-/account_settings/developer_console
2. Click "Create token"
3. Name: "ProJ Connect"
4. Copy token

**Step 2: Configure in ProJ Connect**
- **Service Type**: Tasks
- **Service**: Asana
- **Personal Access Token**: [Your token]
- **Workspace ID**: [From workspace settings]

**Key URLs:**
- API: https://app.asana.com/api/1.0
- Tasks: GET https://app.asana.com/api/1.0/projects/{project_id}/tasks
- Add task: POST https://app.asana.com/api/1.0/tasks
- Documentation: https://developers.asana.com/docs

---

### Notion Setup

**Step 1: Create Integration**
1. Go to: https://www.notion.so/my-integrations
2. Click "Create new integration"
3. Name: "ProJ Connect"
4. Capabilities: Read, Update, Insert, Create

**Step 2: Authorize Pages**
1. Share the Notion page with your integration
2. Copy the database ID (from page URL)

**Step 3: Configure in ProJ Connect**
- **Service Type**: Tasks
- **Service**: Notion
- **API Key**: [Your integration key]
- **Database ID**: [From page]

**Key URLs:**
- API: https://api.notion.com/v1
- Query database: POST https://api.notion.com/v1/databases/{database_id}/query
- Documentation: https://developers.notion.com/reference/intro

---

## 🔔 Messaging Integrations

### Slack Setup

**Step 1: Create App**
1. Go to: https://api.slack.com/apps
2. Click "Create New App"
3. Name: "ProJ Connect"
4. Select workspace

**Step 2: Configure OAuth**
1. Go to "OAuth & Permissions"
2. Scopes needed: `chat:write`, `users:read`, `team:read`
3. Set Redirect URL: `http://localhost:8080/callback`

**Step 3: Get Credentials**
1. Copy "Client ID" and "Client Secret"
2. Get "Bot User OAuth Token"

**Configure in ProJ Connect:**
- **Service Type**: Messaging
- **Service**: Slack
- **Bot Token**: [Bot User OAuth Token]
- **Client ID**: [For OAuth flow]
- **Webhook URL**: [Incoming webhook URL]

**Key URLs:**
- OAuth: https://slack.com/oauth_authorize
- API: https://slack.com/api/chat.postMessage
- Webhooks: https://api.slack.com/messaging/webhooks
- App Directory: https://api.slack.com/apps

**Send Message Example:**
```
POST https://slack.com/api/chat.postMessage
Authorization: Bearer xoxb-your-token
{
  "channel": "#general",
  "text": "Your activity is due: Car Insurance"
}
```

---

### Telegram Setup

**Step 1: Create Bot**
1. Message @BotFather on Telegram
2. Send: `/newbot`
3. Name: "ProJ Connect"
4. Get Bot Token

**Step 2: Get Chat ID**
1. Message your bot
2. Visit: `https://api.telegram.org/bot{BOT_TOKEN}/getMe`
3. Get your Chat ID

**Configure in ProJ Connect:**
- **Service Type**: Messaging
- **Service**: Telegram
- **Bot Token**: [From BotFather]
- **Chat ID**: [Your chat ID]

**Key URLs:**
- API: https://api.telegram.org/bot{token}/
- Send message: POST https://api.telegram.org/bot{token}/sendMessage
- Documentation: https://core.telegram.org/bots/api

**Send Message Example:**
```
POST https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage
{
  "chat_id": 123456789,
  "text": "🔔 Reminder: Car Insurance payment due in 3 days"
}
```

---

## 🪝 Custom Webhooks

### Generic Webhook Setup

**For any service with webhook support:**

**Step 1: Configure Webhook URL**
- URL: `https://your-domain.com/webhook/activity`
- Method: `POST`
- Headers:
  ```json
  {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-api-key"
  }
  ```

**Step 2: Payload Format**
```json
{
  "event": "activity_due",
  "activity": {
    "id": 1,
    "title": "Car Insurance",
    "due_date": "2026-03-31",
    "category": "payment"
  },
  "timestamp": "2026-03-28T16:00:00Z"
}
```

**Configure in ProJ Connect:**
- **Service Type**: Webhooks
- **Webhook URL**: [Your endpoint]
- **Authorization Header**: [API key]
- **Events**: Select which events trigger webhook

---

## 🔗 IFTTT & Zapier Setup

### IFTTT Setup

**Step 1: Create Account**
1. Go to: https://ifttt.com/join
2. Create account

**Step 2: Activate Webhooks**
1. Search for "Webhooks"
2. Click "Connect"
3. Copy your Webhook Key

**Step 3: Create Applet**
1. Go to: https://ifttt.com/create
2. If This: Webhooks → "Receive a web request"
   - Event Name: `activity_due`
3. Then That: [Choose action - Email, SMS, Slack, etc.]

**Configure in ProJ Connect:**
- **Service Type**: Utilities
- **Service**: IFTTT
- **Webhook URL**: `https://maker.ifttt.com/trigger/activity_due/with/key/{your_key}`

**Trigger Webhook Example:**
```bash
curl -X POST https://maker.ifttt.com/trigger/activity_due/with/key/YOUR_KEY \
  -H "Content-Type: application/json" \
  -d '{"value1":"Car Insurance","value2":"Payment due in 3 days"}'
```

---

### Zapier Setup

**Step 1: Create Account**
1. Go to: https://zapier.com/sign-up
2. Create account

**Step 2: Create Zap**
1. Go to: https://zapier.com/app/zaps
2. Click "Create Zap"
3. Trigger: Webhooks by Zapier
4. Event: Catch Hook
5. Copy the Webhook URL

**Step 3: Configure Action**
- Choose: Email, SMS, Slack, etc.
- Map fields from webhook

**Configure in ProJ Connect:**
- **Service Type**: Utilities
- **Service**: Zapier
- **Webhook URL**: [From Zapier]

---

## 🔐 Security Best Practices

### API Key Management
✅ **DO:**
- Store API keys in environment variables
- Use app-specific passwords when available
- Rotate keys regularly
- Use OAuth tokens instead of passwords

❌ **DON'T:**
- Hardcode API keys in source code
- Share API keys in emails
- Store plain passwords
- Use master account credentials

### OAuth Security
✅ **DO:**
- Use PKCE flow for public clients
- Validate state parameter
- Use HTTPS only
- Store refresh tokens securely

❌ **DON'T:**
- Use implicit grant flow
- Skip state validation
- Store access tokens in cookies
- Share refresh tokens

---

## 📊 Testing Integrations

### Test Email Connection
```
Service: Gmail
Status: Testing...
Connection: OK ✓
Auth: Valid ✓
Folders: Inbox (15 new)
```

### Test Calendar Connection
```
Service: Google Calendar
Status: Testing...
Connection: OK ✓
Auth: Valid ✓
Calendars: Primary, Work, Personal
```

### Test Payment Connection
```
Service: Stripe
Status: Testing...
Connection: OK ✓
Auth: Valid ✓
Recent transactions: 5
```

---

## 🆘 Troubleshooting

### "Connection Failed"
- Check API endpoint URL
- Verify network connectivity
- Check firewall/proxy settings

### "Invalid Credentials"
- Verify API key/secret
- Check token expiration
- Regenerate tokens if needed
- Verify scope permissions

### "Webhook Not Received"
- Check webhook URL is publicly accessible
- Verify HTTPS certificate
- Check firewall allows webhooks
- Review service webhook logs

### "Rate Limit Exceeded"
- Reduce request frequency
- Implement exponential backoff
- Check service rate limits
- Consider higher tier plan

---

## 📚 Additional Resources

**API Documentation:**
- Gmail: https://developers.google.com/gmail/api
- Google Calendar: https://developers.google.com/calendar/api
- Microsoft Graph: https://docs.microsoft.com/en-us/graph
- Stripe: https://stripe.com/docs/api
- PayPal: https://developer.paypal.com/docs/api

**OAuth Standards:**
- OAuth 2.0: https://oauth.net/2/
- OpenID Connect: https://openid.net/connect/

---

**Last Updated**: March 28, 2026
**ProJ Connect Version**: 1.0.0

For support, visit the ProJ Connect documentation or GitHub repository.
