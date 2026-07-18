# ProJ Connect - Developer Documentation

## Architecture Overview

ProJ Connect follows a clean, modular architecture with clear separation of concerns:

### Core Layers

1. **Presentation Layer** (`src/ui/`)
   - PyQt6-based modern UI
   - Component-based design
   - Professional dark theme

2. **Business Logic** (`src/core/`)
   - Reminder scheduling engine
   - Activity management logic
   - Event processing

3. **Data Layer** (`src/database/`)
   - SQLAlchemy ORM models
   - Database operations (CRUD)
   - Schema management

4. **Integration Layer** (`src/integrations/`)
   - Base integration framework
   - Email, Calendar, Payment adapters
   - Extensible for custom APIs

5. **Notifications** (`src/notifications/`)
   - System notification handlers
   - Platform-specific adapters (Windows, Linux, Mac)
   - Notification history tracking

## File Structure

```
src/
├── main.py                          # Application entry point
├── __init__.py
│
├── ui/                             # User Interface Layer
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py             # Navigation sidebar (SidebarWidget)
│   │   ├── dashboard.py           # Dashboard overview (DashboardWidget)
│   │   ├── activities.py          # Activity management (ActivitiesWidget, ActivityDialog)
│   │   └── integrations.py        # Integration settings (IntegrationsWidget, IntegrationDialog)
│   └── styles/
│       ├── __init__.py
│       └── theme.py               # Dark theme stylesheet
│
├── core/                           # Business Logic Layer
│   ├── __init__.py
│   └── reminder_engine.py         # Scheduler and reminder logic (ReminderEngine)
│
├── database/                       # Data Access Layer
│   ├── __init__.py
│   ├── config.py                  # Database setup and session management
│   ├── models.py                  # SQLAlchemy models (Activity, ActivityCompletion, etc.)
│   └── operations.py              # CRUD operations (ActivityManager, IntegrationManager, etc.)
│
├── integrations/                  # Integration Framework
│   ├── __init__.py
│   └── base.py                    # Base integration classes and adapters
│
├── notifications/                 # Notification System
│   ├── __init__.py
│   └── notify.py                  # Notification handlers (NotificationHandler)
│
└── utils/                         # Utility Functions
    ├── __init__.py
    └── helpers.py                 # Helper functions
```

## Database Schema

### Activities Table
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category ENUM(payment|subscription|maintenance|meeting|task|health|other),
    recurrence_type ENUM(once|daily|weekly|biweekly|monthly|quarterly|yearly|custom),
    recurrence_interval INTEGER,
    start_date DATETIME,
    next_due_date DATETIME,
    due_date DATETIME,
    reminder_days_before INTEGER,
    reminder_hours_before INTEGER,
    send_notification BOOLEAN,
    is_active BOOLEAN,
    is_completed BOOLEAN,
    integration_id INTEGER FOREIGN KEY,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Activity Completions Table
```sql
CREATE TABLE activity_completions (
    id INTEGER PRIMARY KEY,
    activity_id INTEGER FOREIGN KEY,
    completed_at DATETIME,
    notes TEXT
);
```

### Integrations Table
```sql
CREATE TABLE integrations (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    app_type VARCHAR(100),
    username VARCHAR(255),
    api_key TEXT,
    access_token TEXT,
    refresh_token TEXT,
    is_active BOOLEAN,
    config_data TEXT,
    created_at DATETIME,
    last_synced DATETIME
);
```

## Key Classes

### MainWindow
- Entry point for the application
- Manages main layout with sidebar and stacked pages
- Initializes reminder engine
- Handles window lifecycle

### DashboardWidget
- Statistics display (total, due, overdue, completed)
- Due activities table
- Overdue activities table
- Refresh functionality

### ActivitiesWidget & ActivityDialog
- List all activities in table format
- Add/edit/delete activities
- Form validation for activity creation
- Real-time updates

### IntegrationsWidget & IntegrationDialog
- Manage connected applications
- Store credentials securely
- Edit/delete integrations
- Sync status tracking

### ReminderEngine
- Background scheduler using APScheduler
- Periodic checks for due activities
- Automatic reminder notifications
- Recurring activity recalculation

### DatabaseManager Classes
- ActivityManager: Create, read, update, delete activities
- IntegrationManager: Manage integrations
- NotificationManager: Track notification history

## Important Algorithms

### Reminder Calculation
```python
reminder_time = next_due_date - (days_before + hours_before)
If now >= reminder_time and now < next_due_date:
    Send Reminder Notification
```

### Recurring Date Calculation
```python
def calculate_next_due_date(activity):
    base = activity.next_due_date
    if recurrence == DAILY: return base + 1 day
    if recurrence == WEEKLY: return base + 7 days
    if recurrence == MONTHLY: return base + 1 month
    if recurrence == YEARLY: return base + 1 year
```

### Activity Status Logic
```
Pending < Now - 2hr:    OVERDUE (red alert)
Pending >= Now - 2hr:   DUE SOON (amber warning)
Pending >= Next week:   UPCOMING (normal)
```

## Development Guidelines

### Adding New Features

1. **UI Component**
   - Create in `src/ui/components/`
   - Inherit from QWidget
   - Apply stylesheet theme
   - Connect signals/slots

2. **Database Model**
   - Add class to `src/database/models.py`
   - Inherit from Base
   - Add relationships
   - Create manager in `operations.py`

3. **Integration Type**
   - Inherit from BaseIntegration
   - Implement connect/disconnect/sync
   - Add to IntegrationDialog options

### Code Style
- PEP 8 compliant
- Type hints where possible
- Docstrings for all classes/functions
- Clear variable names

### Testing
- Test db operations manually initially
- Verify UI renders correctly
- Test reminder triggers at different intervals
- Validate integration connections

## Building Installers

### Windows EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

### Linux AppImage
```bash
pip install pyinstaller
pyinstaller src/main.py
# Use appimagetool to create AppImage
```

## Troubleshooting Development

### Import Errors
Solution: Ensure Python path includes project root
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### Database Locked
Solution: Ensure only one session per thread
```python
session = get_session()
try:
    # operations
finally:
    session.close()
```

### PyQt6 Issues
Solution: Ensure virtual environment has clean install
```bash
pip uninstall PyQt6 PyQt6-sip
pip install PyQt6
```

## Performance Optimization

Currently optimized for:
- Single-threaded UI with background reminder scheduler
- SQLite for local persistence
- In-memory caching of active activities
- Efficient table queries with indexes on next_due_date

## Future Optimizations
- Connection pooling for database
- UI pagination for large activity lists
- Lazy loading of completion history
- Batch notification processing

## Dependencies & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | 6.6.1+ | GUI Framework |
| SQLAlchemy | 2.0+ | ORM & DB |
| APScheduler | 3.10+ | Task Scheduling |
| requests | 2.31+ | HTTP Client |
| python-dateutil | 2.8+ | Date Handling |
| pytz | 2023.3+ | Timezone Support |
| Pillow | 10.1+ | Image Processing |

---

For API documentation and extension guides, see USAGE.md and README.md
