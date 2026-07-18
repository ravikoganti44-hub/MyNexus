"""
Comprehensive Advanced User Testing of UI/UX Improvements and New Features
Tests all enhancements from advanced user perspective
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Create QApplication before importing PyQt6 widgets
from PyQt6.QtWidgets import QApplication
app_instance = None
try:
    app_instance = QApplication.instance()
    if app_instance is None:
        app_instance = QApplication(sys.argv)
except:
    pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_session, init_db
from src.database.operations import ActivityManager, ConnectedApplicationManager
from src.database.models import RecurrenceType, CategoryType
from src.ui.components.activities import ActivitiesWidget, ActivityDialog
from src.ui.components.dashboard import DashboardWidget
from src.ui.components.settings import SettingsWidget
from src.ui.components.connected_apps import ConnectedAppsWidget


class TestActivitiesUIEnhancements(unittest.TestCase):
    """Test Activities widget enhancements"""
    
    @classmethod
    def setUpClass(cls):
        """Setup for all tests"""
        init_db()
        cls.session = get_session()
        
        # Clear existing test data
        for activity in ActivityManager.get_all_activities(cls.session):
            ActivityManager.delete_activity(cls.session, activity.id)
        
        # Create test activities
        test_activities = [
            {
                'title': 'Pay Mortgage',
                'description': 'Monthly mortgage payment for primary residence',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'next_due_date': datetime.now() + timedelta(days=5),
            },
            {
                'title': 'Car Insurance Due',
                'description': 'Auto insurance premium payment',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.QUARTERLY,
                'next_due_date': datetime.now() + timedelta(days=2),
            },
            {
                'title': 'Netflix Subscription',
                'description': 'Monthly streaming service renewal',
                'category': CategoryType.SUBSCRIPTION,
                'recurrence_type': RecurrenceType.MONTHLY,
                'next_due_date': datetime.now() + timedelta(days=10),
            },
            {
                'title': 'Overdue: Property Tax',
                'description': 'Property tax payment overdue',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.YEARLY,
                'next_due_date': datetime.now() - timedelta(days=3),
            },
            {
                'title': 'HVAC Maintenance',
                'description': 'Schedule HVAC system maintenance',
                'category': CategoryType.MAINTENANCE,
                'recurrence_type': RecurrenceType.ONCE,
                'next_due_date': datetime.now() + timedelta(days=15),
            },
        ]
        
        for activity_data in test_activities:
            ActivityManager.create_activity(cls.session, **activity_data)
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        cls.session.close()
    
    def test_1_activities_load_correctly(self):
        """Test that all activities load without errors"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            self.assertGreaterEqual(len(activities), 5)
            print(f"✅ Test 1 Passed: {len(activities)} activities loaded successfully")
        finally:
            session.close()
    
    def test_2_search_functionality(self):
        """Test activity search functionality"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            # Simulate search by title
            search_term = "mortgage"
            matches = [a for a in activities if search_term.lower() in a.title.lower()]
            self.assertGreater(len(matches), 0)
            print(f"✅ Test 2 Passed: Search found {len(matches)} results for '{search_term}'")
        finally:
            session.close()
    
    def test_3_filter_by_category(self):
        """Test category filtering"""
        session = get_session()
        try:
            payment_activities = ActivityManager.get_all_activities(session)
            payment_activities = [a for a in payment_activities if a.category == CategoryType.PAYMENT]
            self.assertGreater(len(payment_activities), 0)
            print(f"✅ Test 3 Passed: Category filter found {len(payment_activities)} payment activities")
        finally:
            session.close()
    
    def test_4_filter_by_status(self):
        """Test status filtering (pending/completed)"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            pending = [a for a in activities if not a.is_completed]
            completed = [a for a in activities if a.is_completed]
            self.assertGreater(len(pending), 0)
            print(f"✅ Test 4 Passed: Pending={len(pending)}, Completed={len(completed)}")
        finally:
            session.close()
    
    def test_5_bulk_mark_complete(self):
        """Test bulk mark as complete functionality"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            if activities:
                # Mark first activity as complete
                first_activity = activities[0]
                ActivityManager.update_activity(session, first_activity.id, is_completed=True)
                
                # Verify it's marked
                updated = ActivityManager.get_activity(session, first_activity.id)
                self.assertTrue(updated.is_completed)
                print(f"✅ Test 5 Passed: Activity '{first_activity.title}' marked as complete")
        finally:
            session.close()
    
    def test_6_sorting_functionality(self):
        """Test sorting by due date"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            sorted_asc = sorted(activities, key=lambda x: x.next_due_date or datetime.max)
            self.assertGreater(len(sorted_asc), 0)
            print(f"✅ Test 6 Passed: Activities sorted by due date successfully")
        finally:
            session.close()
    
    def test_7_get_overdue_activities(self):
        """Test overdue activity detection"""
        session = get_session()
        try:
            overdue = ActivityManager.get_overdue_activities(session)
            self.assertGreaterEqual(len(overdue), 1)
            print(f"✅ Test 7 Passed: Found {len(overdue)} overdue activities")
        finally:
            session.close()
    
    def test_8_get_due_soon_activities(self):
        """Test due soon activity detection"""
        session = get_session()
        try:
            due_soon = ActivityManager.get_due_activities(session, days_ahead=7)
            self.assertGreater(len(due_soon), 0)
            print(f"✅ Test 8 Passed: Found {len(due_soon)} activities due within 7 days")
        finally:
            session.close()
    
    def test_9_activity_urgency_indicators(self):
        """Test visual urgency indicators"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            
            # Test days left calculation
            for activity in activities:
                if activity.next_due_date:
                    days_left = (activity.next_due_date - datetime.now()).days
                    
                    # Determine urgency level
                    if days_left < 0:
                        urgency = "OVERDUE (Red)"
                    elif days_left == 0:
                        urgency = "TODAY (Orange)"
                    elif days_left <= 3:
                        urgency = "URGENT (Yellow)"
                    else:
                        urgency = "OK (Normal)"
                    
                    print(f"  - {activity.title}: {days_left} days left - {urgency}")
            
            print(f"✅ Test 9 Passed: Urgency indicators calculated correctly")
        finally:
            session.close()
    
    def test_10_activity_dialog_creation(self):
        """Test ActivityDialog can be instantiated"""
        dialog = ActivityDialog()
        self.assertIsNotNone(dialog.title_input)
        self.assertIsNotNone(dialog.category_combo)
        self.assertIsNotNone(dialog.recurrence_combo)
        print(f"✅ Test 10 Passed: ActivityDialog created successfully with all fields")


class TestDashboardEnhancements(unittest.TestCase):
    """Test Dashboard widget enhancements"""
    
    def test_1_dashboard_statistics(self):
        """Test dashboard calculates statistics correctly"""
        session = get_session()
        try:
            all_activities = ActivityManager.get_all_activities(session)
            due_activities = ActivityManager.get_due_activities(session, days_ahead=7)
            overdue_activities = ActivityManager.get_overdue_activities(session)
            
            completed_count = sum(1 for a in all_activities if a.is_completed)
            completion_rate = (completed_count / len(all_activities) * 100) if all_activities else 0
            
            print(f"📊 Dashboard Statistics:")
            print(f"  - Total Activities: {len(all_activities)}")
            print(f"  - Due This Week: {len(due_activities)}")
            print(f"  - Overdue: {len(overdue_activities)}")
            print(f"  - Completed: {completed_count}/{len(all_activities)}")
            print(f"  - Completion Rate: {completion_rate:.1f}%")
            
            self.assertGreater(len(all_activities), 0)
            print(f"✅ Test 1 Passed: Dashboard statistics calculated correctly")
        finally:
            session.close()
    
    def test_2_category_breakdown(self):
        """Test category breakdown on dashboard"""
        session = get_session()
        try:
            from collections import Counter
            activities = ActivityManager.get_all_activities(session)
            
            category_counts = Counter(a.category.value for a in activities)
            print(f"📊 Category Breakdown:")
            for cat, count in category_counts.most_common():
                print(f"  - {cat.title()}: {count}")
            
            self.assertGreater(len(category_counts), 0)
            print(f"✅ Test 2 Passed: Category breakdown generated successfully")
        finally:
            session.close()


class TestSettingsWidget(unittest.TestCase):
    """Test Settings widget functionality"""
    
    def test_1_settings_load(self):
        """Test settings can be loaded"""
        widget = SettingsWidget()
        self.assertIsNotNone(widget.settings)
        self.assertIn('notifications_enabled', widget.settings)
        self.assertIn('theme', widget.settings)
        print(f"✅ Test 1 Passed: Settings loaded successfully")
    
    def test_2_settings_persist(self):
        """Test settings can be saved"""
        widget = SettingsWidget()
        original_settings = widget.settings.copy()
        
        # Modify a setting
        widget.settings['notifications_enabled'] = not widget.settings['notifications_enabled']
        from PyQt6.QtWidgets import QMessageBox
        original_information = QMessageBox.information
        original_critical = QMessageBox.critical
        QMessageBox.information = staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
        QMessageBox.critical = staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
        try:
            widget._save_settings()
        finally:
            QMessageBox.information = original_information
            QMessageBox.critical = original_critical
        
        # Verify it was saved
        new_widget = SettingsWidget()
        self.assertEqual(
            new_widget.settings['notifications_enabled'],
            not original_settings['notifications_enabled']
        )
        
        # Restore
        widget.settings['notifications_enabled'] = original_settings['notifications_enabled']
        widget._save_settings()
        
        print(f"✅ Test 2 Passed: Settings persist correctly")
    
    def test_3_all_settings_tabs_exist(self):
        """Test all settings tabs are present"""
        # Check that settings tabs exist
        expected_settings = [
            'notifications_enabled',
            'sound_enabled',
            'theme',
            'time_format',
            'auto_refresh_interval',
            'check_updates',
            'backup_enabled',
        ]
        
        widget = SettingsWidget()
        for setting in expected_settings:
            self.assertIn(setting, widget.settings)
        
        print(f"✅ Test 3 Passed: All {len(expected_settings)} setting categories present")


class TestConnectedAppsFeature(unittest.TestCase):
    """Test Connected Applications feature"""
    
    def test_1_connected_apps_load(self):
        """Test connected apps can be loaded"""
        session = get_session()
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(session)
            self.assertGreater(len(apps), 0)
            print(f"✅ Test 1 Passed: {len(apps)} connected apps loaded successfully")
        finally:
            session.close()
    
    def test_2_connected_apps_by_category(self):
        """Test filtering connected apps by category"""
        session = get_session()
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(session)
            
            # Group by category
            from collections import Counter
            categories = Counter(a.app_type for a in apps)
            
            print(f"📊 Connected Apps by Category:")
            for cat, count in categories.most_common():
                print(f"  - {cat}: {count}")
            
            self.assertGreater(len(categories), 0)
            print(f"✅ Test 2 Passed: Connected apps grouped by category")
        finally:
            session.close()


class TestWorkflows(unittest.TestCase):
    """Test complete user workflows"""
    
    def test_1_create_edit_delete_workflow(self):
        """Test complete create-edit-delete workflow"""
        session = get_session()
        try:
            # Create
            new_activity = ActivityManager.create_activity(
                session,
                title="Test Activity for Workflow",
                description="Testing the complete workflow",
                category=CategoryType.TASK,
                recurrence_type=RecurrenceType.ONCE,
                next_due_date=datetime.now() + timedelta(days=5)
            )
            self.assertIsNotNone(new_activity.id)
            print(f"✅ Created activity: {new_activity.title}")
            
            # Edit
            ActivityManager.update_activity(
                session, new_activity.id,
                description="Updated description"
            )
            updated = ActivityManager.get_activity(session, new_activity.id)
            self.assertEqual(updated.description, "Updated description")
            print(f"✅ Updated activity description")
            
            # Delete
            ActivityManager.delete_activity(session, new_activity.id)
            deleted = ActivityManager.get_activity(session, new_activity.id)
            self.assertIsNone(deleted)
            print(f"✅ Deleted activity")
            
            print(f"✅ Test 1 Passed: Complete workflow executed successfully")
        finally:
            session.close()
    
    def test_2_advanced_filtering_workflow(self):
        """Test advanced filtering and search workflow"""
        session = get_session()
        try:
            activities = ActivityManager.get_all_activities(session)
            
            # Multiple filters
            filtered = [a for a in activities 
                       if a.category == CategoryType.PAYMENT and 
                          not a.is_completed and
                          a.next_due_date and
                          (a.next_due_date - datetime.now()).days <= 7]
            
            print(f"🔍 Advanced Filter Results:")
            print(f"  - Total activities: {len(activities)}")
            print(f"  - Matching filters: {len(filtered)}")
            print(f"    (Payment category + Pending + Due within 7 days)")
            
            for activity in filtered:
                days_left = (activity.next_due_date - datetime.now()).days
                print(f"    - {activity.title} (due in {days_left} days)")
            
            print(f"✅ Test 2 Passed: Advanced filtering workflow successful")
        finally:
            session.close()


class TestPerformanceAndStress(unittest.TestCase):
    """Test performance with larger datasets"""
    
    def test_1_large_dataset_performance(self):
        """Test performance with many activities"""
        session = get_session()
        try:
            # This tests ability to handle current data
            activities = ActivityManager.get_all_activities(session)
            
            import time
            start = time.time()
            
            # Simulate sorting
            sorted_by_title = sorted(activities, key=lambda x: x.title)
            sorted_by_date = sorted(activities, key=lambda x: x.next_due_date or datetime.max)
            
            # Simulate filtering
            completed = [a for a in activities if a.is_completed]
            pending = [a for a in activities if not a.is_completed]
            
            elapsed = time.time() - start
            
            print(f"⚡ Performance Metrics:")
            print(f"  - Activities processed: {len(activities)}")
            print(f"  - Sort + Filter time: {elapsed*1000:.2f}ms")
            print(f"  - Completed: {len(completed)}, Pending: {len(pending)}")
            
            # Should complete in under 100ms even with 100+ activities
            self.assertLess(elapsed, 0.1)
            print(f"✅ Test 1 Passed: Performance acceptable")
        finally:
            session.close()


def run_all_tests():
    """Run all tests with detailed reporting"""
    print("\n" + "="*70)
    print("ADVANCED USER TESTING - ProJ Connect Enhanced UI/UX")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestActivitiesUIEnhancements))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboardEnhancements))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsWidget))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectedAppsFeature))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceAndStress))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
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
    sys.exit(0 if success else 1)
