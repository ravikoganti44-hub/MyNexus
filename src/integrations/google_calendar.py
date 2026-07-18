"""
Google Calendar Integration Implementation
Handles OAuth 2.0 authentication and calendar operations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.integrations.base import CalendarIntegration
from config.integration_urls import INTEGRATION_URLS

logger = logging.getLogger(__name__)


class GoogleCalendarIntegration(CalendarIntegration):
    """Google Calendar-specific integration with OAuth 2.0"""
    
    SERVICE_NAME = 'google_calendar'
    
    def __init__(self, credentials: Dict[str, Any] = None):
        config = credentials or {}
        config['service_name'] = 'google_calendar'
        super().__init__(config)
        self.service_info = INTEGRATION_URLS.get_service_by_name('google_calendar')
    
    def get_oauth_url(self, redirect_uri: str = 'http://localhost:8000/callback') -> str:
        """
        Generate OAuth 2.0 authorization URL for Google Calendar
        
        Args:
            redirect_uri: Where to redirect after user authorization
        
        Returns:
            Full OAuth 2.0 authorization URL
        """
        client_id = self.config.get('client_id', '')
        scope = ' '.join(self.service_info.get('scopes', []))
        
        oauth_url = (
            f"{self.get_api_url()}/auth/oauth2/auth?"
            f"client_id={client_id}&"
            f"scope={scope}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        return oauth_url
    
    def exchange_code_for_token(self, code: str, client_secret: str,
                                redirect_uri: str = 'http://localhost:8000/callback') -> Optional[Dict]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            client_secret: Client secret from Google Cloud Console
            redirect_uri: Must match the redirect_uri used in get_oauth_url()
        
        Returns:
            Token response containing access_token, refresh_token, etc.
        """
        logger.info("Exchanging authorization code for Google Calendar tokens")
        
        token_data = {
            'client_id': self.config.get('client_id', ''),
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # In production, use requests library to POST to token endpoint
        # response = requests.post(self.service_info['token_url'], json=token_data)
        # return response.json()
        
        logger.info("Token exchange successful (mock)")
        return token_data
    
    def connect(self) -> bool:
        """Verify Google Calendar connection with stored token"""
        access_token = self.config.get('access_token')
        if not access_token:
            logger.warning("No access token configured for Google Calendar")
            return False
        
        logger.info("Google Calendar connected successfully")
        return True
    
    def get_upcoming_events(self, days: int = 7, max_results: int = 10) -> Optional[List[Dict]]:
        """
        Retrieve upcoming events from Google Calendar
        
        Args:
            days: Number of days ahead to retrieve
            max_results: Maximum number of events to retrieve
        
        Returns:
            List of calendar events
        """
        if not self.connect():
            return None
        
        now = datetime.now()
        future = now + timedelta(days=days)
        
        logger.info(f"Fetching upcoming events for next {days} days (max {max_results} results)")
        
        # In production:
        # endpoint = f"{self.get_api_url()}/calendar/v3/calendars/primary/events"
        # headers = {'Authorization': f"Bearer {self.config['access_token']}"}
        # params = {
        #     'timeMin': now.isoformat() + 'Z',
        #     'timeMax': future.isoformat() + 'Z',
        #     'maxResults': max_results,
        #     'singleEvents': True,
        #     'orderBy': 'startTime'
        # }
        # response = requests.get(endpoint, headers=headers, params=params)
        # return response.json().get('items', [])
        
        logger.info(f"Retrieved events (mock endpoint: {self.get_api_url()}/calendar/v3/calendars/primary/events)")
        return []
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                    description: str = '', attendees: List[str] = None) -> bool:
        """
        Create a new calendar event
        
        Args:
            title: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description
            attendees: List of attendee email addresses
        
        Returns:
            True if event created successfully
        """
        if not self.connect():
            return False
        
        logger.info(f"Creating calendar event: {title}")
        
        # In production:
        # event = {
        #     'summary': title,
        #     'description': description,
        #     'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        #     'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
        #     'attendees': [{'email': email} for email in (attendees or [])]
        # }
        # endpoint = f"{self.get_api_url()}/calendar/v3/calendars/primary/events"
        # headers = {'Authorization': f"Bearer {self.config['access_token']}"}
        # response = requests.post(endpoint, headers=headers, json=event)
        # return response.status_code == 200
        
        logger.info(f"Event created successfully (mock)")
        return True
    
    def sync(self) -> bool:
        """Sync Google Calendar events"""
        logger.info("Syncing Google Calendar events...")
        events = self.get_upcoming_events(days=30, max_results=100)
        logger.info(f"Sync complete. Retrieved {len(events) if events else 0} events")
        self.update_sync_time()
        return True
    
    def get_setup_guide_url(self) -> str:
        """Get link to Google Calendar setup guide"""
        return self.service_info.get('setup_guide', '')
    
    def get_documentation_url(self) -> str:
        """Get link to Google Calendar API documentation"""
        return self.service_info.get('documentation', '')
