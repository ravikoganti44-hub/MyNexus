# ProJ Connect - Activity & Payment Reminder System

A professional desktop application for managing recurring activities, payment reminders, and multi-application integrations with automatic notifications.

## Features

- **Activity Management**: Create and track recurring activities (payments, subscriptions, maintenance, etc.)
- **Smart Reminders**: Customizable notification system with multiple reminder intervals
- **Recurring Events**: Automatic renewal tracking for recurring activities
- **Multi-App Integration**: Connect with various applications and services
- **Professional UI**: Modern, clean, and intuitive interface
- **Local Database**: SQLite for secure local data storage
- **System Notifications**: Desktop notifications powered by system tray
- **Activity Completion Tracking**: Mark activities as done and track completion history

## Project Structure

```
ProJ_connect/
├── src/
│   ├── ui/                  # User interface components
│   │   ├── components/      # Custom UI components
│   │   └── styles/          # QSS stylesheets
│   ├── core/                # Core business logic
│   ├── database/            # Database models and management
│   ├── integrations/        # API integrations
│   ├── notifications/       # Notification handlers
│   ├── utils/               # Utility functions
│   └── main.py              # Application entry point
├── config/                  # Configuration files
├── assets/                  # Icons and resources
└── requirements.txt         # Python dependencies
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python src/main.py
```

## Database Schema

The application uses SQLite with the following main tables:
- **Activities**: Stores activity/reminder definitions
- **Activity_Completions**: Tracks completion history
- **Integrations**: Stores connected application credentials
- **Notifications**: Notification settings and history

## Architecture

- **MVC Pattern**: Clean separation of Model, View, and Controller
- **Database Layer**: SQLAlchemy ORM for data management
- **Scheduler**: APScheduler for background task execution
- **Threading**: Separate threads for notifications and CRUD operations

## Technologies Used

- **UI Framework**: PyQt6 (modern desktop GUI)
- **Database**: SQLite3 with SQLAlchemy ORM
- **Task Scheduling**: APScheduler
- **Notifications**: WinToast (Windows), Plyer (cross-platform fallback)
- **API Integration**: Requests library

## Supported Integrations

- Email (Gmail, Outlook)
- Calendar (Google Calendar, Outlook)
- Task Management (Todoist)
- Banking & Payments
- Custom webhooks

## License

MIT License

## Author

ProJ Connect Team
