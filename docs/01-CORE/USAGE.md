# ProJ Connect - Getting Started Guide

## Overview

**ProJ Connect** is a professional desktop application designed to help you manage recurring activities, payments, and reminders across multiple integrated applications. Whether you need to track insurance payments, subscription renewals, maintenance schedules, or any other recurring task, ProJ Connect automates notifications and tracks completion history.

## Key Features

### 🎯 Activity Management
- Create unlimited activities with customizable recurrence patterns
- Support for one-time, daily, weekly, monthly, quarterly, and yearly reminders
- Categorize activities (Payments, Subscriptions, Maintenance, Health, Tasks, etc.)
- Track completion history and renewal dates

### 🔔 Intelligent Reminders
- Automatic notifications before due dates
- Customizable reminder intervals (days and hours)
- Desktop notifications that appear on Windows taskbar
- Visual indicators for overdue items

### 📊 Professional Dashboard
- Real-time overview of all activities
- Statistics cards showing:
  - Total active activities
  - Items due this week
  - Overdue items count
  - Today's completions
- Color-coded tables for quick status assessment

### 🔗 Multi-App Integration
- Connect your email, calendar, and payment services
- Support for Gmail, Outlook, Google Calendar, Todoist, and more
- Extensible integration framework for custom APIs
- Secure local credential storage

### 📱 Clean Modern UI
- Professional dark theme with cyan accents
- Responsive design that adapts to window size
- Intuitive navigation sidebar
- Organized tabbed interface

## Installation & Setup

### Prerequisites
- Windows 10/11 or Linux/Mac with Python 3.9+
- 100MB free disk space

### Quick Start (Windows)

1. **Download and Extract** the project
2. **Run the launcher**:
   ```bash
   run.bat
   ```
   Or for first-time setup:
   ```bash
   python app.py
   ```

3. **Application opens automatically** - the setup is complete!

### Manual Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   source venv/bin/activate # Linux/Mac
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```

## How to Use

### Creating Your First Activity

1. **Open the Application** and navigate to "My Activities" tab
2. **Click "+ Add Activity"** button
3. **Fill in the Details**:
   - **Title**: E.g., "Car Insurance Payment"
   - **Description**: Optional details about the activity
   - **Category**: Select the appropriate category
   - **Recurrence**: Choose how often this repeats (Monthly, Yearly, etc.)
   - **Start Date**: When the activity begins
   - **Next Due Date**: When it's next due
   - **Reminders**: Set how many days/hours before you want to be notified
   - **Active**: Toggle to enable/disable tracking

4. **Click "Save"** - Your activity is now tracked!

### Managing Activities

**Dashboard View**:
- See all due activities at a glance
- Color-coded status indicators
- Quick access to mark items complete

**Activities List**:
- Edit any activity by clicking "Edit"
- Delete activities you no longer need
- See full details including recurrence and due dates

**Marking Complete**:
- Click on an activity and mark as complete
- The system automatically calculates the next renewal date
- Completion history is maintained for reference

### Setting Up Integrations

1. **Navigate to "Integrations"** tab
2. **Click "+ Add Integration"**
3. **Enter Integration Details**:
   - **Name**: e.g., "Gmail", "Google Calendar"
   - **Type**: Select the service type
   - **Credentials**: Enter username and API key/password
   - **Status**: Mark as Active to enable sync

4. **Link Activities**: When creating activities, optionally link them to integrations for automatic sync

### Understanding the Dashboard

**Stat Cards** (Top Section):
- **Total Activities**: Count of all active items being tracked
- **Due This Week**: Items coming due in the next 7 days
- **Overdue**: Items past their due date that need attention
- **Completed Today**: Successfully completed items

**Due This Week Table**:
- Lists all upcoming activities sorted by due date
- Shows days remaining until due
- Quickly identify what needs attention

**Overdue Activities Table**:
- Shows past-due items that require immediate attention
- Displays how many days overdue each is
- Color-coded in red for urgency

## Recurrence Patterns

### Available Patterns
| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Once** | No recurring (one-time) | One-time tasks or events |
| **Daily** | Every day | Daily medications, vitamins |
| **Weekly** | Every week on the same day | Weekly meetings, yoga class |
| **Bi-Weekly** | Every 2 weeks | Alternating two-week tasks |
| **Monthly** | Same day each month | Monthly subscriptions, rent |
| **Quarterly** | Every 3 months | Tax filings, car maintenance |
| **Yearly** | Every year | Annual insurance, birthdays |
| **Custom** | Custom interval in days | Any specific pattern |

## Activity Categories

### Pre-defined Categories
- **Payment**: Bills, subscriptions, loans
- **Subscription**: Renewals (software, services, memberships)
- **Maintenance**: Vehicle, home, appliance servicing
- **Meeting**: Appointments, calls, reviews
- **Task**: General to-do items
- **Health**: Medications, checkups, appointments
- **Other**: Miscellaneous activities

## Database & Data Security

- **Local Storage**: All data stored in SQLite database on your computer
- **No Cloud Sync**: Your information never leaves your device
- **Automatic Backups**: Data directory: `./data/projconnect.db`
- **Manual Backup**: Copy `data/` folder to external drive regularly

## Tips & Best Practices

### Organization
✅ **Use clear titles** - "Car Insurance Premium" instead of "Insurance"
✅ **Categorize properly** - Helps with filtering and reporting
✅ **Set realistic reminders** - 1-2 days before for payments, immediately for tickets
✅ **Include notes** - Use description field for important details (account numbers, contacts)

### Notifications
✅ **Desktop notifications** appear even when app is minimized
✅ **Check the Dashboard daily** - Make a habit of reviewing what's due
✅ **Mark items as complete** - Keeps records accurate and maintains history

### Integration
✅ **Start small** - Add one integration at a time
✅ **Test credentials** - Verify access before linking activities
✅ **Update regularly** - Refresh integrations if credentials change

## Troubleshooting

### Application Won't Start
- **Solution**: Ensure Python 3.9+ is installed
- **Check**: Run `python --version` in terminal
- **Fix**: Reinstall dependencies: `pip install -r requirements.txt`

### Notifications Not Showing
- **Check**: Ensure "Send notifications" is enabled for your activity
- **Windows**: Check notification center settings
- **Fix**: Try closing and reopening the application

### Activities Not Showing Up
- **Check**: Verify activity is marked as "Active"
- **Try**: Click "Refresh" button on dashboard
- **Fix**: Check database file exists in `data/` folder

### Can't Add Integration
- **Verify**: Credentials are correct (copy-paste to avoid typos)
- **Check**: App type dropdown matches your service
- **Fix**: Some services require app-specific passwords (Gmail, Outlook)

## System Requirements

### Minimum
- **OS**: Windows 10, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.9 or higher
- **RAM**: 256MB
- **Storage**: 100MB

### Recommended
- **OS**: Windows 11, Linux (Ubuntu 22.04+), macOS 12+
- **Python**: 3.11 or higher
- **RAM**: 512MB
- **Storage**: 200MB

## Project Structure

```
ProJ_Connect/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/                     # User interface
│   │   ├── components/         # UI components
│   │   │   ├── dashboard.py   # Dashboard widget
│   │   │   ├── activities.py  # Activities management
│   │   │   ├── integrations.py# Integrations panel
│   │   │   └── sidebar.py     # Navigation sidebar
│   │   └── styles/
│   │       └── theme.py       # Dark theme stylesheet
│   ├── core/
│   │   └── reminder_engine.py # Reminder scheduling engine
│   ├── database/
│   │   ├── config.py          # Database configuration
│   │   ├── models.py          # SQLAlchemy models
│   │   └── operations.py      # Database CRUD operations
│   ├── integrations/
│   │   └── base.py            # Integration framework
│   └── notifications/
│       └── notify.py          # Notification handler
├── config/                     # Configuration files
├── data/                       # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── USAGE.md                    # This file
├── app.py                      # Application launcher
└── run.bat / run.sh            # Platform-specific runners
```

## Advanced Configuration

### Custom Themes
Edit `src/ui/styles/theme.py` to customize colors

### Database Location
Edit `src/database/config.py` to change database path

### Integration Plugins
Add new integration types in `src/integrations/base.py`

## Support & Feedback

For issues, suggestions, or contributions:
1. Check the Troubleshooting section above
2. Review activity configuration settings
3. Ensure all dependencies are properly installed

## License

This project is provided as-is for personal use.

## Future Features

Planned enhancements:
- 📈 Advanced reporting and analytics
- 🌐 Cloud backup option
- 📧 Email notifications
- 📱 Mobile companion app
- 🔐 Encrypted credential storage
- 📅 Calendar export (iCal format)
- 💬 Slack/Teams integration
- 🎨 Multiple theme options

---

**Last Updated**: March 28, 2026  
**Version**: 1.0.0
