"""
System notification handler
"""
import logging
import sys

logger = logging.getLogger(__name__)


class NotificationHandler:
    """Handle system notifications"""
    
    def __init__(self):
        self.platform = sys.platform
        self._setup_notifications()
    
    def _setup_notifications(self):
        """Setup platform-specific notification system"""
        try:
            if self.platform == 'win32':
                # Check optional dependency pkg_resources used by some win-toast builds
                try:
                    import pkg_resources  # presence indicates setuptools installed
                except Exception:
                    logger.warning('pkg_resources not available; skipping WinToast setup')
                    return

                from wintoast import Toast
                self.toast = Toast()
                logger.info("Using WinToast for notifications")
            else:
                logger.info("Using Plyer for notifications")
        except ImportError as e:
            logger.warning(f"Notification library not available: {e}")
    
    def show_notification(self, title: str, message: str, activity_id: str = None, 
                         notification_type: str = "reminder", icon: str = None):
        """Show a system notification"""
        try:
            if self.platform == 'win32':
                self._show_windows_notification(title, message, notification_type)
            else:
                self._show_plyer_notification(title, message)
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def _show_windows_notification(self, title: str, message: str, notification_type: str = "reminder"):
        """Show Windows notification using WinToast"""
        try:
            from wintoast import Toast
            
            # Set icon based on notification type
            icon_emoji = {
                "reminder": "🔔",
                "due": "⚠️",
                "overdue": "🚨",
                "completed": "✅"
            }
            
            toast = Toast()
            toast.show_toast(
                title=f"{icon_emoji.get(notification_type, '📌')} MyNexus - {title}",
                msg=message,
                threaded=True,
                duration='short'
            )
        except Exception as e:
            logger.error(f"WinToast notification failed: {e}")
            self._show_plyer_notification(title, message)
    
    def _show_plyer_notification(self, title: str, message: str):
        """Show notification using Plyer (cross-platform)"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="MyNexus",
                timeout=10
            )
        except Exception as e:
            logger.error(f"Plyer notification failed: {e}")
    
    def show_success(self, message: str):
        """Show success notification"""
        self.show_notification("Success", message, notification_type="completed")
    
    def show_error(self, message: str):
        """Show error notification"""
        self.show_notification("Error", message, notification_type="error")
    
    def show_info(self, title: str, message: str):
        """Show info notification"""
        self.show_notification(title, message, notification_type="info")
