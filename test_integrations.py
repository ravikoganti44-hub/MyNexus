"""
Integration Testing Module
Tests for all service integrations
"""

import unittest
import logging
from datetime import datetime, timedelta
from src.integrations import (
    GmailIntegration,
    GoogleCalendarIntegration,
    StripeIntegration,
    SlackIntegration,
    get_integration_class,
    create_integration
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGmailIntegration(unittest.TestCase):
    """Test Gmail integration"""
    
    def setUp(self):
        self.credentials = {
            'client_id': 'test_client_id',
            'access_token': 'test_token'
        }
        self.gmail = GmailIntegration(self.credentials)
    
    def test_initialization(self):
        """Test Gmail instance creation"""
        self.assertIsNotNone(self.gmail)
        self.assertEqual(self.gmail.SERVICE_NAME, 'gmail')
    
    def test_oauth_url_generation(self):
        """Test OAuth URL generation"""
        oauth_url = self.gmail.get_oauth_url()
        self.assertIn('client_id=test_client_id', oauth_url)
        self.assertIn('response_type=code', oauth_url)
        self.assertIn('access_type=offline', oauth_url)
    
    def test_connection(self):
        """Test Gmail connection"""
        result = self.gmail.connect()
        self.assertTrue(result)
    
    def test_sync(self):
        """Test Gmail sync"""
        result = self.gmail.sync()
        self.assertTrue(result)
    
    def test_documentation_url(self):
        """Test documentation URL retrieval"""
        url = self.gmail.get_documentation_url()
        self.assertIsNotNone(url)
        self.assertIn('gmail', url.lower())


class TestGoogleCalendarIntegration(unittest.TestCase):
    """Test Google Calendar integration"""
    
    def setUp(self):
        self.credentials = {
            'client_id': 'test_client_id',
            'access_token': 'test_token'
        }
        self.calendar = GoogleCalendarIntegration(self.credentials)
    
    def test_initialization(self):
        """Test Google Calendar instance creation"""
        self.assertIsNotNone(self.calendar)
        self.assertEqual(self.calendar.SERVICE_NAME, 'google_calendar')
    
    def test_oauth_url_generation(self):
        """Test OAuth URL generation"""
        oauth_url = self.calendar.get_oauth_url()
        self.assertIn('client_id=test_client_id', oauth_url)
        self.assertIn('scope=', oauth_url)
    
    def test_connection(self):
        """Test Google Calendar connection"""
        result = self.calendar.connect()
        self.assertTrue(result)
    
    def test_get_upcoming_events(self):
        """Test retrieving upcoming events"""
        events = self.calendar.get_upcoming_events(days=7, max_results=10)
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
    
    def test_create_event(self):
        """Test creating calendar event"""
        start = datetime.now() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        result = self.calendar.create_event(
            title='Test Event',
            start_time=start,
            end_time=end,
            description='Test event description'
        )
        self.assertTrue(result)
    
    def test_sync(self):
        """Test Google Calendar sync"""
        result = self.calendar.sync()
        self.assertTrue(result)


class TestStripeIntegration(unittest.TestCase):
    """Test Stripe integration"""
    
    def setUp(self):
        self.credentials = {
            'secret_key': 'sk_test_mock'
        }
        self.stripe = StripeIntegration(self.credentials)
    
    def test_initialization(self):
        """Test Stripe instance creation"""
        self.assertIsNotNone(self.stripe)
        self.assertEqual(self.stripe.SERVICE_NAME, 'stripe')
    
    def test_connection(self):
        """Test Stripe connection"""
        result = self.stripe.connect()
        self.assertTrue(result)
    
    def test_verify_api_key(self):
        """Test API key verification"""
        result = self.stripe.verify_api_key('sk_test_valid')
        self.assertTrue(result)
    
    def test_create_payment(self):
        """Test payment creation"""
        payment = self.stripe.create_payment(
            amount=2000.0,  # $20.00
            currency='usd',
            description='Test payment'
        )
        self.assertIsNotNone(payment)
        self.assertEqual(payment['amount'], 2000)
        self.assertEqual(payment['currency'], 'usd')
    
    def test_get_transactions(self):
        """Test retrieving transactions"""
        transactions = self.stripe.get_transactions(limit=10, status='all')
        self.assertIsNotNone(transactions)
        self.assertIsInstance(transactions, list)
    
    def test_get_account_info(self):
        """Test getting account info"""
        account = self.stripe.get_account_info()
        self.assertIsNotNone(account)
        self.assertIn('id', account)
    
    def test_sync(self):
        """Test Stripe sync"""
        result = self.stripe.sync()
        self.assertTrue(result)


class TestSlackIntegration(unittest.TestCase):
    """Test Slack integration"""
    
    def setUp(self):
        self.credentials = {
            'bot_token': 'xoxb-mock-token'
        }
        self.slack = SlackIntegration(self.credentials)
    
    def test_initialization(self):
        """Test Slack instance creation"""
        self.assertIsNotNone(self.slack)
        self.assertEqual(self.slack.SERVICE_NAME, 'slack')
    
    def test_connection(self):
        """Test Slack connection"""
        result = self.slack.connect()
        self.assertTrue(result)
    
    def test_send_message(self):
        """Test sending message"""
        message = self.slack.send_message(
            channel='#general',
            text='Test message'
        )
        self.assertIsNotNone(message)
        self.assertTrue(message['ok'])
    
    def test_send_notification(self):
        """Test sending notification"""
        notification = self.slack.send_notification(
            channel='#alerts',
            title='Test Notification',
            message='This is a test notification',
            color='#0099FF',
            fields={'Status': 'Active', 'Count': '5'}
        )
        self.assertIsNotNone(notification)
        self.assertTrue(notification['ok'])
    
    def test_get_channels(self):
        """Test retrieving channels"""
        channels = self.slack.get_channels()
        self.assertIsNotNone(channels)
        self.assertIsInstance(channels, list)
    
    def test_get_users(self):
        """Test retrieving users"""
        users = self.slack.get_users()
        self.assertIsNotNone(users)
        self.assertIsInstance(users, list)
    
    def test_sync(self):
        """Test Slack sync"""
        result = self.slack.sync()
        self.assertTrue(result)


class TestIntegrationRegistry(unittest.TestCase):
    """Test integration registry and factory functions"""
    
    def test_get_integration_class(self):
        """Test getting integration classes"""
        gmail_class = get_integration_class('gmail')
        self.assertEqual(gmail_class, GmailIntegration)
        
        stripe_class = get_integration_class('stripe')
        self.assertEqual(stripe_class, StripeIntegration)
    
    def test_create_integration(self):
        """Test creating integrations"""
        gmail = create_integration('gmail', {'client_id': 'test'})
        self.assertIsInstance(gmail, GmailIntegration)
        
        slack = create_integration('slack', {'bot_token': 'test'})
        self.assertIsInstance(slack, SlackIntegration)
    
    def test_case_insensitive_lookup(self):
        """Test case-insensitive service lookup"""
        gmail_lower = get_integration_class('gmail')
        gmail_upper = get_integration_class('GMAIL')
        self.assertEqual(gmail_lower, gmail_upper)
    
    def test_invalid_service(self):
        """Test invalid service lookup"""
        integration = get_integration_class('nonexistent')
        self.assertIsNone(integration)


if __name__ == '__main__':
    unittest.main()
