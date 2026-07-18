"""
CONNECTED APPLICATIONS FEATURE
ProJ Connect - External Application Login Management
"""

# ============================================================================
# FEATURE OVERVIEW
# ============================================================================

## What is the Connected Applications Feature?

The Connected Applications feature allows you to securely manage login credentials
and quick access links for all your external applications in one place. This
includes banking, mortgage, insurance, medical, and subscription applications.

**Key Benefits:**
- 🔐 Centralized credential storage (with encryption ready)
- 🔗 Quick access links to applications
- 📝 Track account numbers and account holders
- 🏷️ Categorize by application type
- ⏱️ See last access time
- 🔍 Search and organize applications

---

## ============================================================================
## HOW TO USE
## ============================================================================

### Accessing Connected Applications

1. **From Main Menu**: Click the **🔐 Connected Apps** button in the sidebar
2. **Dashboard**: View quick access to your 5 most recent apps on the dashboard

### Adding a New Application

1. Click **+ Add Application** button
2. Fill in the application details:
   - **Application Name**: Your personal name for this connection (e.g., "My Mortgage Account")
   - **Application Type**: The company/service (e.g., "Better.com", "Chase Bank")
   - **Category**: Select from predefined categories or use "other"
   - **Website URL**: Main website URL
   - **Login URL**: Direct login page (if different from website)
   - **Username/Email**: Your login credentials
   - **Account Number**: Mortgage number, bank account number, etc.
   - **Account Holder**: Name on the account
   - **Icon Emoji**: Visual identifier (e.g., 🏠 🏦 💳 🏥 📱)
   - **Notes**: Any important information or reminders

3. Click **Save** to store the application

### Editing an Application

1. Find the application in the table
2. Click the **Edit** button
3. Update any information
4. Click **Save**

### Opening an Application

1. Click the **Open** button next to any application
2. Your default browser will open to the login URL or website

### Deleting an Application

1. Click the **Delete** button (red button)
2. Confirm the deletion
3. The application will be permanently removed

---

## ============================================================================
## AVAILABLE CATEGORIES
## ============================================================================

Organize your applications by type:

- **mortgage**: Mortgage lenders and servicers
- **banking**: Bank accounts and financial institutions
- **credit_card**: Credit card companies
- **investment**: Investment platforms and brokers
- **utilities**: Electric, gas, water, internet providers
- **insurance**: Home, auto, health, life insurance
- **medical**: Healthcare providers, pharmacies, health apps
- **subscription**: Subscription services and memberships
- **other**: Everything else

---

## ============================================================================
## EXAMPLE SCENES
## ============================================================================

### Scenario 1: Mortgage Account Management

You have a mortgage with Better.com:

| Field | Value |
|-------|-------|
| Application Name | My Primary Mortgage |
| Application Type | Better.com |
| Category | mortgage |
| Website URL | https://www.better.com |
| Login URL | https://app.better.com/login |
| Username | john.doe@email.com |
| Account Number | MG-123456789 |
| Account Holder | John Doe |
| Icon | 🏠 |
| Notes | Primary home loan, refinanced 2024 |

### Scenario 2: Banking Portal

Chase checking account:

| Field | Value |
|-------|-------|
| Application Name | Chase Checking |
| Application Type | Chase Bank |
| Category | banking |
| Website URL | https://www.chase.com |
| Login URL | https://secure06a.chase.com/id/client/login |
| Username | john.doe@email.com |
| Account Number | 1234567890 |
| Account Holder | John Doe |
| Icon | 🏦 |
| Notes | Main checking account |

### Scenario 3: Insurance Portal

State Farm home insurance:

| Field | Value |
|-------|-------|
| Application Name | State Farm Insurance |
| Application Type | State Farm |
| Category | insurance |
| Website URL | https://www.statefarm.com |
| Login URL | https://www.statefarm.com/login |
| Username | john.doe@email.com |
| Account Number | HO-98765432 |
| Account Holder | John Doe |
| Icon | 📋 |
| Notes | Home and auto insurance |

---

## ============================================================================
## SECURITY CONSIDERATIONS
## ============================================================================

### Current Implementation (Development)
- Credentials stored in local database
- Ready for encryption implementation

### Best Practices
1. **Use Strong Passwords**: Don't use easily guessable passwords
2. **Update Regularly**: Change passwords periodically
3. **Backup Database**: Regularly backup your ProJ Connect database
4. **Secure Your Computer**: Ensure your computer has antivirus/malware protection
5. **Logout**: Always logout from ProJ Connect when finished
6. **Avoid Public WiFi**: Don't access sensitive information on public networks

### Future Security Enhancements
- Password encryption at rest
- Master password protection
- Encrypted database backups
- Activity audit logging
- Two-factor authentication support

---

## ============================================================================
## DATABASE SCHEMA
## ============================================================================

### ConnectedApplication Table

```sql
CREATE TABLE connected_applications (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,           -- User's name for the app
    app_type VARCHAR(100) NOT NULL,        -- Application category
    app_name VARCHAR(255),                 -- Company/service name
    website_url VARCHAR(500),              -- Main website
    login_url VARCHAR(500),                -- Direct login URL
    username VARCHAR(255) NOT NULL,        -- Login username/email
    password_encrypted TEXT,               -- Encrypted password
    email VARCHAR(255),                    -- Alternative email
    account_number VARCHAR(255),           -- Account/customer number
    account_holder VARCHAR(255),           -- Name on account
    security_question TEXT,                -- Security question for reference
    security_answer_encrypted TEXT,        -- Encrypted answer
    category VARCHAR(100),                 -- Category (mortgage, banking, etc.)
    icon_emoji VARCHAR(10),                -- Visual icon (emoji)
    is_active BOOLEAN DEFAULT TRUE,        -- Active/inactive flag
    last_accessed DATETIME,                -- Last access timestamp
    created_at DATETIME DEFAULT NOW,       -- Creation timestamp
    updated_at DATETIME DEFAULT NOW        -- Last update timestamp
    notes TEXT                             -- User notes
);
```

---

## ============================================================================
## API / DATABASE OPERATIONS
## ============================================================================

### Using ConnectedApplicationManager

```python
from src.database.operations import ConnectedApplicationManager
from src.database.config import get_session

session = get_session()

# Create a new application
app = ConnectedApplicationManager.create_connected_app(
    session,
    name='My Mortgage',
    app_name='Better.com',
    username='user@email.com',
    account_number='MG-123456',
    category='mortgage',
    icon_emoji='🏠',
    website_url='https://www.better.com'
)

# Get all applications
all_apps = ConnectedApplicationManager.get_all_connected_apps(session)

# Get applications by category
mortgage_apps = ConnectedApplicationManager.get_apps_by_category(
    session, 
    'mortgage'
)

# Update an application
ConnectedApplicationManager.update_connected_app(
    session,
    app_id=1,
    name='Updated Name'
)

# Search applications
results = ConnectedApplicationManager.search_connected_apps(
    session,
    'mortgage'
)

# Update last accessed
ConnectedApplicationManager.update_last_accessed(session, app_id)

# Delete application
ConnectedApplicationManager.delete_connected_app(session, app_id)
```

---

## ============================================================================
## UI COMPONENTS
## ============================================================================

### ConnectedAppsWidget
**File**: `src/ui/components/connected_apps.py`

Main widget for managing connected applications. Features:
- Table view of all applications
- Add/Edit/Delete buttons
- Quick open to login pages
- Last accessed tracking
- Search and filter

### ConnectedApplicationDialog
**File**: `src/ui/components/connected_apps.py`

Form dialog for adding/editing applications. Fields:
- Name, type, category
- URLs, credentials
- Account information
- Emoji icon
- Notes

### Dashboard Quick Access
**File**: `src/ui/components/dashboard.py`

Quick access section on dashboard showing:
- First 5 connected applications
- One-click access to open applications
- "View All" button to manage all applications

---

## ============================================================================
## WORKFLOW EXAMPLES
## ============================================================================

### Workflow 1: Quick Access from Dashboard

1. Open ProJ Connect → Dashboard loads
2. See "Quick Access - Connected Applications" section
3. Click application icon (e.g., "🏠 My Mortgage Account")
4. Browser opens to mortgage login page
5. Enter password (not stored) and login

### Workflow 2: Manage Multiple Mortgage Accounts

1. Click 🔐 Connected Apps in sidebar
2. See all mortgage accounts listed
3. Click Edit on one to update details
4. Click Delete to remove old account
5. Click Add Application to add new account

### Workflow 3: Organize by Category

1. In Connected Apps page
2. See table organized by category
3. Filter by "banking" to see all bank accounts
4. Quickly see all account numbers
5. Click Open to access any account

---

## ============================================================================
## TROUBLESHOOTING
## ============================================================================

### Application Won't Open
- **Check**: Ensure URL starts with http:// or https://
- **Fix**: Add prefix if missing (e.g., www.bettercom → https://www.bettercom)

### Can't Find Application
- **Check**: Use search feature to find by name or account number
- **Check**: Verify the application is marked as active
- **Fix**: Category may have changed - check all applications

### Last Accessed Never Updates
- **Reason**: You haven't clicked "Open" button yet
- **Fix**: Click "Open" to trigger last accessed update

### Password Saved but Won't Work
- **Note**: ProJ Connect stores your password for reference
- **Security**: Always change password if account is compromised
- **Update**: Edit application to update stored password

---

## ============================================================================
## FUTURE ENHANCEMENTS
## ============================================================================

### Planned Features

**Phase 2 (Q2 2024)**:
- ✅ Password encryption
- ✅ Master password protection
- ✅ Backup and restore functionality
- ✅ Application icons/avatars

**Phase 3 (Q3 2024)**:
- [ ] Two-factor authentication support
- [ ] OAuth auto-login integration
- [ ] Application health/status monitoring
- [ ] Renewal date reminders (insurance, subscriptions)

**Phase 4 (Q4 2024)**:
- [ ] Mobile companion app
- [ ] Cloud sync (encrypted)
- [ ] Sharing with family members
- [ ] Detailed audit logging
- [ ] Security breach notifications

---

## ============================================================================
## REFERENCE
## ============================================================================

### File Locations
- Database Model: `src/database/models.py` → `ConnectedApplication` class
- Database Operations: `src/database/operations.py` → `ConnectedApplicationManager` class
- UI Widget: `src/ui/components/connected_apps.py`
- Dashboard Integration: `src/ui/components/dashboard.py`

### Related Features
- Activities & Reminders: Set reminders for billing dates
- Integrations: Connect to OAuth-enabled applications
- Notifications: Get alerts for important events

---

**Feature Added**: March 2024
**Version**: 1.0
**Status**: Production Ready

