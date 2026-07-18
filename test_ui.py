#!/usr/bin/env python3
"""
ProJ Connect - UI Integration Test
Tests that the application can initialize PyQt6 components without errors
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_creation():
    """Test UI component creation"""
    print("\n" + "="*60)
    print("UI COMPONENT CREATION TEST")
    print("="*60)
    
    try:
        print("\n✓ Initializing PyQt6 application...")
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("  ✓ QApplication created")
        
        print("\n✓ Testing theme stylesheet...")
        from src.ui.styles.theme import get_stylesheet
        theme = get_stylesheet()
        print(f"  ✓ Stylesheet generated ({len(theme)} characters)")
        
        print("\n✓ Creating sidebar component...")
        from src.ui.components.sidebar import SidebarWidget
        sidebar = SidebarWidget()
        print("  ✓ Sidebar widget created")
        
        print("\n✓ Creating dashboard component...")
        from src.ui.components.dashboard import DashboardWidget
        dashboard = DashboardWidget()
        print("  ✓ Dashboard widget created")
        
        print("\n✓ Creating activities component...")
        from src.ui.components.activities import ActivitiesWidget
        activities = ActivitiesWidget()
        print("  ✓ Activities widget created")
        
        print("\n✓ Creating integrations component...")
        from src.ui.components.integrations import IntegrationsWidget
        integrations = IntegrationsWidget()
        print("  ✓ Integrations widget created")
        
        print("\n✓ All UI components created successfully!")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ UI Component Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_application_startup():
    """Test application can start without crashing"""
    print("="*60)
    print("APPLICATION STARTUP TEST")
    print("="*60)
    
    try:
        print("\n✓ Loading main application class...")
        from src.main import MainWindow
        print("  ✓ MainWindow class loaded")
        
        print("\n✓ Creating PyQt6 application...")
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("  ✓ QApplication created")
        
        print("\n✓ Creating main window...")
        window = MainWindow()
        print("  ✓ MainWindow created successfully")
        
        print("\n✓ Testing window properties...")
        print(f"  ✓ Window title: {window.windowTitle()}")
        print(f"  ✓ Window size: {window.width()}x{window.height()}")
        
        print("\n✓ Testing reminder engine integration...")
        if hasattr(window, 'reminder_engine'):
            print(f"  ✓ Reminder engine attached")
            print(f"  ✓ Engine running: {window.reminder_engine.running}")
        
        print("\n✓ Testing stacked pages...")
        print(f"  ✓ Current page: {window.pages.currentIndex()}")
        print(f"  ✓ Page count: {window.pages.count()}")
        
        print("\n✓ Stopping reminder engine...")
        window.reminder_engine.stop()
        print("  ✓ Reminder engine stopped")
        
        print("\n✓ Application startup test PASSED!")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Application Startup Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*8 + "ProJ Connect - UI & STARTUP TEST SUITE" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    success = True
    
    # Run tests
    if not test_ui_creation():
        success = False
    
    if not test_application_startup():
        success = False
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    if success:
        print("\n✓ ALL TESTS PASSED!")
        print("\nVerified Components:")
        print("  ✓ PyQt6 application framework")
        print("  ✓ Dark theme stylesheet")
        print("  ✓ Sidebar navigation")
        print("  ✓ Dashboard widget")
        print("  ✓ Activities management")
        print("  ✓ Integrations panel")
        print("  ✓ Main window creation")
        print("  ✓ Reminder engine integration")
        print("\n✓ Application ready for GUI launch!")
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
    
    print("="*60 + "\n")
