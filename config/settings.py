# MyNexus Configuration

# Application Settings
APP_NAME = "MyNexus"
APP_TITLE = "MyNexus - Personal Organizer"
APP_TAGLINE = "Life organized in one place"
APP_VERSION = "2026.v1"

# UI Configuration
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Theme
THEME = "dark"  # Options: "dark", "light"
PRIMARY_COLOR = "#00d4ff"
ACCENT_COLOR = "#f59e0b"

# Database
DATABASE_TYPE = "sqlite"  # Options: "sqlite", "postgresql"
DATABASE_NAME = "projconnect.db"
DATABASE_AUTO_BACKUP = True
BACKUP_INTERVAL_DAYS = 7

# Reminders & Notifications
CHECK_INTERVAL_MINUTES = 1  # How often to check for due reminders
NOTIFICATION_TIMEOUT_SECONDS = 10
ENABLE_SYSTEM_NOTIFICATIONS = True
ENABLE_SOUND_ALERTS = False

# Activity Defaults
DEFAULT_REMINDER_DAYS_BEFORE = 1
DEFAULT_REMINDER_HOURS_BEFORE = 0
DEFAULT_RECURRENCE = "monthly"

# Integrations
INTEGRATION_SYNC_INTERVAL_HOURS = 24
ENABLE_AUTO_SYNC = True

# Logging
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_FILE = "logs/projconnect.log"
LOG_MAX_SIZE_MB = 10
LOG_BACKUP_COUNT = 5

# Security
ENABLE_PASSWORD_PROTECTION = True
ENCRYPT_CREDENTIALS = True
AUTO_LOCK_MINUTES = 30

# Performance
USE_THREADING = True
CACHE_TIMEOUT_SECONDS = 300
MAX_NOTIFICATIONS_HISTORY = 100
