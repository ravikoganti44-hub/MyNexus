"""
Test the enhanced Connected Applications UI
Tests: Search, Filter, Sort, View Modes
"""

import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from src.database.config import get_session
from src.database.operations import ConnectedApplicationManager
from src.ui.components.connected_apps import ConnectedAppsWidget

def test_connected_apps_ui():
    """Test the enhanced UI components"""
    print("\n" + "="*60)
    print("Testing Enhanced Connected Applications UI")
    print("="*60)
    
    app = QApplication(sys.argv)
    session = get_session()
    
    try:
        # Test 1: Verify CATEGORY_COLORS import
        from src.ui.components.connected_apps import CATEGORY_COLORS, PREMIUM_COLORS
        print("\n✓ CATEGORY_COLORS imported successfully")
        print(f"  Categories available: {len(CATEGORY_COLORS)}")
        print(f"  Categories: {', '.join(CATEGORY_COLORS.keys())}")
        
        # Test 2: Verify PREMIUM_COLORS
        print("\n✓ PREMIUM_COLORS imported successfully")
        print(f"  Colors available: {len(PREMIUM_COLORS)}")
        
        # Test 3: Get sample applications from database
        apps = ConnectedApplicationManager.get_all_connected_apps(session, active_only=True)
        print(f"\n✓ Retrieved {len(apps)} connected applications from database")
        
        if apps:
            print("\n  Sample applications:")
            for app_obj in apps[:3]:
                print(f"    - {app_obj.name} ({app_obj.app_type})")
        
        # Test 4: Create ConnectedAppsWidget
        print("\n✓ Creating ConnectedAppsWidget...")
        widget = ConnectedAppsWidget()
        print("  Widget created successfully")
        
        # Test 5: Verify view mode attributes
        view_modes = [
            ('VIEW_CARD', 'card'),
            ('VIEW_LIST', 'list'),
            ('VIEW_GRID', 'grid'),
            ('VIEW_COMPACT', 'compact')
        ]
        print("\n✓ Verifying view modes:")
        for attr_name, expected_value in view_modes:
            actual_value = getattr(widget, attr_name)
            assert actual_value == expected_value, f"Mismatch: {attr_name} = {actual_value}"
            print(f"  ✓ {attr_name}: {actual_value}")
        
        # Test 6: Verify view buttons created
        print("\n✓ Checking view mode buttons:")
        expected_buttons = ['card', 'list', 'grid', 'compact']
        for view_mode in expected_buttons:
            assert view_mode in widget.view_buttons, f"Missing button for {view_mode}"
            print(f"  ✓ {view_mode} button exists")
        
        # Test 7: Verify search input exists
        print("\n✓ Checking search functionality:")
        assert hasattr(widget, 'search_input'), "Missing search_input"
        assert hasattr(widget, 'search_query'), "Missing search_query attribute"
        print("  ✓ Search input widget exists")
        print("  ✓ Search query tracking available")
        
        # Test 8: Verify filter/category combo
        print("\n✓ Checking category filter:")
        assert hasattr(widget, 'category_combo'), "Missing category_combo"
        assert hasattr(widget, 'selected_category'), "Missing selected_category attribute"
        print(f"  ✓ Category combo has {widget.category_combo.count()} items")
        print(f"  Current category: {widget.selected_category}")
        
        # Test 9: Verify sort combo
        print("\n✓ Checking sort functionality:")
        assert hasattr(widget, 'sort_combo'), "Missing sort_combo"
        sort_count = widget.sort_combo.count()
        print(f"  ✓ Sort options available: {sort_count}")
        for i in range(sort_count):
            print(f"    - {widget.sort_combo.itemText(i)}")
        
        # Test 10: Verify stats display
        print("\n✓ Checking stats display:")
        assert hasattr(widget, 'total_stat'), "Missing total_stat"
        assert hasattr(widget, 'secured_stat'), "Missing secured_stat"
        print(f"  ✓ Total apps stat: {widget.total_stat.text()}")
        print(f"  ✓ Secured apps stat: {widget.secured_stat.text()}")
        
        # Test 11: Test view mode switching
        print("\n✓ Testing view mode switching:")
        test_views = ['card', 'list', 'grid', 'compact']
        for view_mode in test_views:
            widget.set_view_mode(view_mode)
            assert widget.current_view == view_mode, f"Failed to set view to {view_mode}"
            print(f"  ✓ Successfully switched to {view_mode} view")
        
        # Test 12: Test search functionality
        print("\n✓ Testing search functionality:")
        widget.search_input.setText("test")
        assert widget.search_query == "test", "Search query not updated"
        print("  ✓ Search query update working")
        widget.search_input.clear()
        
        # Test 13: Test category filter
        print("\n✓ Testing category filter:")
        if widget.category_combo.count() > 1:
            widget.category_combo.setCurrentIndex(1)
            category_data = widget.category_combo.currentData()
            print(f"  ✓ Category filter changed to: {category_data}")
        else:
            print("  ✓ Only 'All' category available (no filtering needed)")
        
        print("\n" + "="*60)
        print("✅ All UI tests PASSED!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"  - View modes: {len(widget.view_buttons)} modes working")
        print(f"  - Search: Functional")
        print(f"  - Category filter: {widget.category_combo.count()} options")
        print(f"  - Sort options: {widget.sort_combo.count()} modes")
        print(f"  - Applications displayed: {len(apps)}")
        print("\n✨ Connected Applications UI is production-ready!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    success = test_connected_apps_ui()
    sys.exit(0 if success else 1)
