"""
Core reminder engine and scheduler
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from src.database.config import get_session
from src.database.session_manager import db_session
from src.database.operations import ActivityManager, NotificationManager
from src.notifications.notify import NotificationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderEngine:
    """Core reminder scheduling and execution engine"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.notification_handler = NotificationHandler()
        self.running = False
        # Track sent reminders to avoid duplicates: {(activity_id, type): datetime}
        self._sent: dict[tuple, datetime] = {}
    
    def start(self):
        """Start the reminder engine"""
        if self.running:
            return
        
        logger.info("Starting Reminder Engine...")
        
        # Schedule periodic checks (every minute)
        self.scheduler.add_job(
            self.check_and_send_reminders,
            'interval',
            minutes=1,
            id='reminder_check',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.running = True
        logger.info("Reminder Engine started successfully")
    
    def stop(self):
        """Stop the reminder engine"""
        if not self.running:
            return
        
        logger.info("Stopping Reminder Engine...")
        self.scheduler.shutdown()
        self.running = False
        logger.info("Reminder Engine stopped")
    
    def check_and_send_reminders(self):
        """Check for activities that need reminders"""
        session = get_session()
        try:
            now = datetime.now()
            
            # Get all active activities
            activities = ActivityManager.get_all_activities(session)
            
            for activity in activities:
                if activity.next_due_date is None:
                    continue
                
                # Calculate reminder time
                reminder_delta = timedelta(
                    days=activity.reminder_days_before,
                    hours=activity.reminder_hours_before
                )
                reminder_time = activity.next_due_date - reminder_delta
                
                # Check if it's time to send reminder
                if reminder_time <= now < activity.next_due_date:
                    self._send_reminder(session, activity, "reminder")
                
                # Check if activity is due (within 1 hour)
                if activity.next_due_date <= now < activity.next_due_date + timedelta(hours=1):
                    if not activity.is_completed:
                        self._send_reminder(session, activity, "due")
                
                # Check if activity is overdue (2+ hours past due)
                if now > activity.next_due_date + timedelta(hours=2):
                    if not activity.is_completed:
                        self._send_reminder(session, activity, "overdue")
            
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
        finally:
            session.close()
    
    def _send_reminder(self, session: Session, activity, reminder_type: str):
        """Send a reminder notification (with deduplication)."""
        try:
            if not activity.send_notification:
                return

            # Deduplicate: only send once per (activity, type) per due-date cycle
            key = (activity.id, reminder_type)
            if key in self._sent:
                last = self._sent[key]
                # Suppress if already sent within the last 6 hours
                if (datetime.now() - last).total_seconds() < 6 * 3600:
                    return
            
            # Create notification record
            title_map = {
                "reminder": f"Reminder: {activity.title}",
                "due": f"Due Today: {activity.title}",
                "overdue": f"Overdue: {activity.title}"
            }
            
            message_map = {
                "reminder": f"Activity '{activity.title}' is due soon",
                "due": f"'{activity.title}' is due today",
                "overdue": f"'{activity.title}' is overdue"
            }
            
            notification = NotificationManager.create_notification(
                session=session,
                activity_id=activity.id,
                notification_type=reminder_type,
                title=title_map.get(reminder_type, activity.title),
                message=message_map.get(reminder_type, "Reminder")
            )
            
            # Send system notification
            self.notification_handler.show_notification(
                title=notification.title,
                message=notification.message,
                activity_id=activity.id,
                notification_type=reminder_type
            )
            
            logger.info(f"Sent {reminder_type} for activity: {activity.title}")
            self._sent[key] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def trigger_manual_reminder(self, activity_id: int):
        """Manually trigger a reminder for testing"""
        session = get_session()
        try:
            activity = ActivityManager.get_activity(session, activity_id)
            if activity:
                self._send_reminder(session, activity, "reminder")
        finally:
            session.close()


# Global reminder engine instance
_reminder_engine = None


def get_reminder_engine():
    """Get or create the global reminder engine"""
    global _reminder_engine
    if _reminder_engine is None:
        _reminder_engine = ReminderEngine()
    return _reminder_engine
