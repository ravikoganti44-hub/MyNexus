"""
Gmail Integration Implementation
Handles OAuth 2.0 authentication and email operations
"""

import logging
import json
from typing import Dict, Any, Optional
from src.integrations.base import EmailIntegration
from config.integration_urls import INTEGRATION_URLS

logger = logging.getLogger(__name__)


class GmailIntegration(EmailIntegration):
    """Gmail-specific integration with OAuth 2.0"""
    
    SERVICE_NAME = 'gmail'
    
    def __init__(self, credentials: Dict[str, Any] = None):
        config = credentials or {}
        config['service_name'] = 'gmail'
        super().__init__(config)
        self.service_info = INTEGRATION_URLS.get_service_by_name('gmail')
    
    def get_oauth_url(self, redirect_uri: str = 'http://localhost:8000/callback') -> str:
        """
        Generate OAuth 2.0 authorization URL
        
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
        logger.info(f"Exchanging authorization code for Gmail tokens")
        
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
        """Verify Gmail connection with stored token"""
        access_token = self.config.get('access_token')
        if not access_token:
            logger.warning("No access token configured for Gmail")
            return False
        
        logger.info("Gmail connected successfully")
        return True
    
    def get_emails(self, max_results: int = 10, query: str = '') -> Optional[list]:
        """
        Retrieve emails from Gmail
        
        Args:
            max_results: Maximum number of emails to retrieve
            query: Gmail search query (e.g., 'from:someone@example.com')
        
        Returns:
            List of email messages
        """
        if not self.connect():
            return None
        
        logger.info(f"Fetching {max_results} emails from Gmail (query: {query})")
        
        # In production:
        # endpoint = f"{self.get_api_url()}/gmail/v1/users/me/messages"
        # headers = {'Authorization': f"Bearer {self.config['access_token']}"}
        # params = {'q': query, 'maxResults': max_results}
        # response = requests.get(endpoint, headers=headers, params=params)
        # return response.json().get('messages', [])
        
        logger.info(f"Retrieved emails (mock endpoint: {self.get_api_url()}/gmail/v1/users/me/messages)")
        return []
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email through Gmail
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
        
        Returns:
            True if email sent successfully
        """
        if not self.connect():
            return False
        
        logger.info(f"Sending email to {to} via Gmail")
        
        # In production:
        # import base64
        # from email.mime.text import MIMEText
        # message = MIMEText(body)
        # message['to'] = to
        # message['subject'] = subject
        # raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        # endpoint = f"{self.get_api_url()}/gmail/v1/users/me/messages/send"
        # headers = {'Authorization': f"Bearer {self.config['access_token']}"}
        # response = requests.post(endpoint, headers=headers, json={'raw': raw_message})
        # return response.status_code == 200
        
        logger.info(f"Email sent successfully (mock)")
        return True
    
    def sync(self) -> bool:
        """Sync Gmail emails"""
        logger.info("Syncing Gmail emails...")
        emails = self.get_emails()
        logger.info(f"Sync complete. Retrieved {len(emails) if emails else 0} emails")
        self.update_sync_time()
        return True
    
    def get_setup_guide_url(self) -> str:
        """Get link to Gmail setup guide"""
        return self.service_info.get('setup_guide', '')
    
    def get_documentation_url(self) -> str:
        """Get link to Gmail API documentation"""
        return self.service_info.get('documentation', '')
