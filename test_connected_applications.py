"""
Connected Applications Feature - Comprehensive Test Suite
Tests for database operations, UI components, and feature functionality
"""

import unittest
import logging
from datetime import datetime, timedelta
import webbrowser

from src.database.config import get_session
from src.database.operations import ConnectedApplicationManager
from src.database.models import ConnectedApplication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestConnectedApplicationsDatabase(unittest.TestCase):
    """Test database operations for connected applications"""
    
    def setUp(self):
        """Setup test database session"""
        self.session = get_session()
        # Clean up any test data
        test_apps = self.session.query(ConnectedApplication).filter(
            ConnectedApplication.name.like('TEST_%')
        ).all()
        for app in test_apps:
            self.session.delete(app)
        self.session.commit()
    
    def tearDown(self):
        """Cleanup"""
        self.session.close()
    
    def test_create_connected_app(self):
        """Test creating a connected application"""
        app_data = {
            'name': 'TEST_Banking_App',
            'app_type': 'banking',
            'app_name': 'Test Bank',
            'website_url': 'https://www.testbank.com',
            'username': 'testuser@example.com',
            'account_number': 'TEST-123456',
            'account_holder': 'Test User',
            'category': 'banking',
            'icon_emoji': '🏦'
        }
        
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'TEST_Banking_App')
        self.assertEqual(app.app_type, 'banking')
        self.assertEqual(app.account_number, 'TEST-123456')
        self.assertTrue(app.is_active)
        logger.info(f"✅ Created application: {app.name}")
    
    def test_get_connected_app(self):
        """Test retrieving a connected application"""
        # Create app
        app_data = {
            'name': 'TEST_Banking_Get',
            'app_type': 'banking',
            'username': 'test@example.com',
            'account_number': 'ACC-789',
            'category': 'banking',
            'icon_emoji': '🏦'
        }
        created_app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Retrieve app
        retrieved_app = ConnectedApplicationManager.get_connected_app(self.session, created_app.id)
        
        self.assertIsNotNone(retrieved_app)
        self.assertEqual(retrieved_app.name, 'TEST_Banking_Get')
        self.assertEqual(retrieved_app.id, created_app.id)
        logger.info(f"✅ Retrieved application: {retrieved_app.name}")
    
    def test_get_app_by_name(self):
        """Test retrieving app by name"""
        app_data = {
            'name': 'TEST_Insurance_Name',
            'app_type': 'insurance',
            'username': 'test@example.com',
            'account_number': 'INS-456',
            'category': 'insurance',
            'icon_emoji': '📋'
        }
        ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        app = ConnectedApplicationManager.get_connected_app_by_name(self.session, 'TEST_Insurance_Name')
        
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'TEST_Insurance_Name')
        logger.info(f"✅ Retrieved by name: {app.name}")
    
    def test_get_all_connected_apps(self):
        """Test retrieving all applications"""
        # Create multiple apps
        for i in range(3):
            app_data = {
                'name': f'TEST_App_{i}',
                'app_type': 'banking',
                'username': f'user{i}@example.com',
                'account_number': f'ACC-{i}',
                'category': 'banking'
            }
            ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        apps = ConnectedApplicationManager.get_all_connected_apps(self.session, active_only=True)
        
        test_apps = [a for a in apps if a.name.startswith('TEST_')]
        self.assertGreaterEqual(len(test_apps), 3)
        logger.info(f"✅ Retrieved {len(test_apps)} test applications")
    
    def test_get_apps_by_category(self):
        """Test filtering applications by category"""
        # Create apps with different categories
        categories = ['banking', 'insurance', 'mortgage']
        for cat in categories:
            app_data = {
                'name': f'TEST_{cat.upper()}',
                'app_type': cat,
                'username': f'{cat}@example.com',
                'account_number': f'{cat.upper()}-123',
                'category': cat
            }
            ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Retrieve by category
        banking_apps = ConnectedApplicationManager.get_apps_by_category(self.session, 'banking')
        
        self.assertGreater(len(banking_apps), 0)
        for app in banking_apps:
            self.assertEqual(app.category, 'banking')
        logger.info(f"✅ Retrieved {len(banking_apps)} banking applications")
    
    def test_update_connected_app(self):
        """Test updating an application"""
        # Create app
        app_data = {
            'name': 'TEST_Update_App',
            'app_type': 'banking',
            'username': 'original@example.com',
            'account_number': 'UPDATE-123',
            'category': 'banking'
        }
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        app_id = app.id
        
        # Update app
        updated_app = ConnectedApplicationManager.update_connected_app(
            self.session,
            app_id,
            notes='Updated notes',
            account_holder='Updated Name'
        )
        
        self.assertIsNotNone(updated_app)
        self.assertEqual(updated_app.notes, 'Updated notes')
        self.assertEqual(updated_app.account_holder, 'Updated Name')
        logger.info(f"✅ Updated application: {updated_app.name}")
    
    def test_update_last_accessed(self):
        """Test updating last accessed timestamp"""
        app_data = {
            'name': 'TEST_LastAccessed',
            'app_type': 'banking',
            'username': 'test@example.com',
            'account_number': 'ACC-999'
        }
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Initially should be None
        self.assertIsNone(app.last_accessed)
        
        # Update last accessed
        ConnectedApplicationManager.update_last_accessed(self.session, app.id)
        
        # Verify update
        updated_app = ConnectedApplicationManager.get_connected_app(self.session, app.id)
        self.assertIsNotNone(updated_app.last_accessed)
        logger.info(f"✅ Updated last_accessed: {updated_app.last_accessed}")
    
    def test_search_connected_apps(self):
        """Test searching applications"""
        # Create test apps
        app_data = {
            'name': 'TEST_Search_Mortgage',
            'app_type': 'mortgage',
            'username': 'mortgage@example.com',
            'account_number': 'MTG-12345',
            'category': 'mortgage'
        }
        ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Search by name
        results = ConnectedApplicationManager.search_connected_apps(self.session, 'Search')
        
        self.assertGreater(len(results), 0)
        found = any(r.name == 'TEST_Search_Mortgage' for r in results)
        self.assertTrue(found)
        logger.info(f"✅ Search found {len(results)} results")
    
    def test_delete_connected_app(self):
        """Test deleting an application"""
        # Create app
        app_data = {
            'name': 'TEST_Delete_App',
            'app_type': 'banking',
            'username': 'delete@example.com',
            'account_number': 'DEL-123'
        }
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        app_id = app.id
        
        # Delete app
        result = ConnectedApplicationManager.delete_connected_app(self.session, app_id)
        
        self.assertTrue(result)
        
        # Verify deletion
        deleted_app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        self.assertIsNone(deleted_app)
        logger.info(f"✅ Deleted application with ID: {app_id}")


class TestConnectedApplicationFeatures(unittest.TestCase):
    """Test feature-specific functionality"""
    
    def setUp(self):
        """Setup"""
        self.session = get_session()
    
    def tearDown(self):
        """Cleanup"""
        self.session.close()
    
    def test_application_model_fields(self):
        """Test all ConnectedApplication model fields"""
        app_data = {
            'name': 'TEST_Full_Model',
            'app_type': 'banking',
            'app_name': 'Test Bank Corp',
            'website_url': 'https://www.testbank.com',
            'login_url': 'https://www.testbank.com/login',
            'username': 'testuser@example.com',
            'account_number': 'ACC-123456',
            'account_holder': 'John Test',
            'category': 'banking',
            'icon_emoji': '🏦',
            'notes': 'Test banking account'
        }
        
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Verify all fields
        self.assertEqual(app.name, app_data['name'])
        self.assertEqual(app.app_type, app_data['app_type'])
        self.assertEqual(app.app_name, app_data['app_name'])
        self.assertEqual(app.website_url, app_data['website_url'])
        self.assertEqual(app.login_url, app_data['login_url'])
        self.assertEqual(app.username, app_data['username'])
        self.assertEqual(app.account_number, app_data['account_number'])
        self.assertEqual(app.account_holder, app_data['account_holder'])
        self.assertEqual(app.category, app_data['category'])
        self.assertEqual(app.icon_emoji, app_data['icon_emoji'])
        self.assertEqual(app.notes, app_data['notes'])
        self.assertTrue(app.is_active)
        self.assertIsNotNone(app.created_at)
        self.assertIsNotNone(app.updated_at)
        
        logger.info(f"✅ All model fields verified for: {app.name}")
    
    def test_category_filtering(self):
        """Test category-based organization"""
        categories = ['mortgage', 'banking', 'insurance', 'utilities']
        
        for cat in categories:
            app_data = {
                'name': f'TEST_CAT_{cat}',
                'app_type': cat,
                'username': f'{cat}@test.com',
                'account_number': f'{cat.upper()}-001',
                'category': cat,
                'icon_emoji': '📱'
            }
            ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        
        # Test each category
        for cat in categories:
            apps = ConnectedApplicationManager.get_apps_by_category(self.session, cat)
            cat_apps = [a for a in apps if a.name.startswith('TEST_CAT_')]
            self.assertGreater(len(cat_apps), 0)
            logger.info(f"✅ Category '{cat}' has {len(cat_apps)} application(s)")
    
    def test_readonly_fields_protection(self):
        """Test that readonly fields cannot be accidentally modified"""
        app_data = {
            'name': 'TEST_Readonly',
            'app_type': 'banking',
            'username': 'test@example.com',
            'account_number': 'RO-123'
        }
        
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        created_at_original = app.created_at
        
        # Try to update (created_at should not change)
        ConnectedApplicationManager.update_connected_app(
            self.session,
            app.id,
            notes='Updated'
        )
        
        updated_app = ConnectedApplicationManager.get_connected_app(self.session, app.id)
        self.assertEqual(updated_app.created_at, created_at_original)
        logger.info(f"✅ Readonly fields protected")


class TestConnectedApplicationSamples(unittest.TestCase):
    """Test sample data and real-world scenarios"""
    
    def setUp(self):
        """Setup"""
        self.session = get_session()
    
    def tearDown(self):
        """Cleanup"""
        self.session.close()
    
    def test_mortgage_account_scenario(self):
        """Test real-world mortgage account scenario"""
        mortgage_app = {
            'name': 'TEST_Primary_Mortgage',
            'app_type': 'mortgage',
            'app_name': 'Better.com',
            'website_url': 'https://www.better.com',
            'login_url': 'https://app.better.com/login',
            'username': 'homeowner@example.com',
            'account_number': 'MG-987654321',
            'account_holder': 'Test Homeowner',
            'category': 'mortgage',
            'icon_emoji': '🏠',
            'notes': 'Primary residence mortgage, 30-year fixed at 3.5%'
        }
        
        app = ConnectedApplicationManager.create_connected_app(self.session, **mortgage_app)
        
        self.assertIsNotNone(app.id)
        self.assertEqual(app.app_name, 'Better.com')
        self.assertTrue(app.account_number.startswith('MG-'))
        logger.info(f"✅ Mortgage scenario: {app.name}")
    
    def test_banking_account_scenario(self):
        """Test real-world banking account scenario"""
        bank_app = {
            'name': 'TEST_Chase_Business',
            'app_type': 'banking',
            'app_name': 'Chase Bank',
            'website_url': 'https://www.chase.com',
            'login_url': 'https://secure06a.chase.com/id/client/login',
            'username': 'business@example.com',
            'email': 'business.email@example.com',
            'account_number': 'CH-987654321',
            'account_holder': 'Test Business LLC',
            'category': 'banking',
            'icon_emoji': '🏦',
            'notes': 'Business checking account with multiple signers'
        }
        
        app = ConnectedApplicationManager.create_connected_app(self.session, **bank_app)
        
        self.assertEqual(app.account_holder, 'Test Business LLC')
        self.assertEqual(app.email, 'business.email@example.com')
        logger.info(f"✅ Banking scenario: {app.name}")
    
    def test_multiple_accounts_same_service(self):
        """Test managing multiple accounts with same service"""
        accounts = [
            {'name': 'TEST_Chase_Personal', 'account_number': 'CH-111111'},
            {'name': 'TEST_Chase_Business', 'account_number': 'CH-222222'},
            {'name': 'TEST_Chase_Savings', 'account_number': 'CH-333333'}
        ]
        
        created_ids = []
        for account in accounts:
            app_data = {
                'app_type': 'banking',
                'app_name': 'Chase Bank',
                'username': f'{account["name"]}@example.com',
                'category': 'banking',
                'icon_emoji': '🏦',
                **account
            }
            app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
            created_ids.append(app.id)
        
        # Verify all were created
        self.assertEqual(len(created_ids), 3)
        
        # Retrieve and verify
        for app_id in created_ids:
            app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
            self.assertIsNotNone(app)
            self.assertEqual(app.app_name, 'Chase Bank')
        
        logger.info(f"✅ Created {len(created_ids)} Chase accounts")


class TestConnectedApplicationIntegration(unittest.TestCase):
    """Integration tests across components"""
    
    def setUp(self):
        """Setup"""
        self.session = get_session()
    
    def tearDown(self):
        """Cleanup"""
        self.session.close()
    
    def test_workflow_create_edit_delete(self):
        """Test complete workflow: create → edit → delete"""
        # Step 1: Create
        app_data = {
            'name': 'TEST_Workflow_App',
            'app_type': 'insurance',
            'username': 'workflow@example.com',
            'account_number': 'WF-123',
            'category': 'insurance'
        }
        app = ConnectedApplicationManager.create_connected_app(self.session, **app_data)
        app_id = app.id
        self.assertIsNotNone(app_id)
        logger.info(f"✅ Step 1 - Created: {app.name}")
        
        # Step 2: Edit
        ConnectedApplicationManager.update_connected_app(
            self.session,
            app_id,
            account_holder='Workflow Tester',
            notes='Test workflow'
        )
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        self.assertEqual(app.account_holder, 'Workflow Tester')
        logger.info(f"✅ Step 2 - Updated: {app.account_holder}")
        
        # Step 3: Delete
        result = ConnectedApplicationManager.delete_connected_app(self.session, app_id)
        self.assertTrue(result)
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        self.assertIsNone(app)
        logger.info(f"✅ Step 3 - Deleted app ID: {app_id}")
    
    def test_search_and_filter_workflow(self):
        """Test search and filter workflow"""
        # Create various apps
        apps_to_create = [
            {'name': 'TEST_Filter_Bank1', 'category': 'banking'},
            {'name': 'TEST_Filter_Bank2', 'category': 'banking'},
            {'name': 'TEST_Filter_Mortgage', 'category': 'mortgage'},
            {'name': 'TEST_Filter_Insurance', 'category': 'insurance'}
        ]
        
        for app_data in apps_to_create:
            full_data = {
                'app_type': app_data['category'],
                'username': f'{app_data["name"]}@test.com',
                'account_number': f'{app_data["name"]}-ACC',
                **app_data
            }
            ConnectedApplicationManager.create_connected_app(self.session, **full_data)
        
        # Test 1: Filter by category
        banking = ConnectedApplicationManager.get_apps_by_category(self.session, 'banking')
        banking_test = [a for a in banking if a.name.startswith('TEST_Filter_Bank')]
        self.assertEqual(len(banking_test), 2)
        logger.info(f"✅ Filter: Found {len(banking_test)} banking apps")
        
        # Test 2: Search by name
        results = ConnectedApplicationManager.search_connected_apps(self.session, 'Mortgage')
        self.assertGreater(len(results), 0)
        logger.info(f"✅ Search: Found {len(results)} matching 'Mortgage'")


# ============================================================================
# Test Execution Summary
# ============================================================================

def run_all_tests():
    """Run all test suites and generate report"""
    print("\n" + "="*70)
    print("CONNECTED APPLICATIONS - COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConnectedApplicationsDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectedApplicationFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectedApplicationSamples))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectedApplicationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Status: {'✅ ALL TESTS PASSED' if result.wasSuccessful() else '❌ SOME TESTS FAILED'}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
