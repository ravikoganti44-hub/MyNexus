"""
Quick test to verify ConnectedApplicationDialog form field mapping is correct
"""
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

from src.ui.components.connected_apps import ConnectedApplicationDialog

# Create dialog
dialog = ConnectedApplicationDialog()

# Simulate form input
dialog.name_edit.setText("Test Chase Account")
dialog.category_combo.setCurrentText("Banking")
dialog.app_name_edit.setText("Chase Bank")
dialog.website_edit.setText("https://www.chase.com")
dialog.login_url_edit.setText("https://www.chase.com/login")
dialog.username_edit.setText("myusername")
dialog.account_num_edit.setText("12345678")
dialog.holder_edit.setText("John Doe")
dialog.notes_edit.setPlainText("Primary checking account")
dialog.emoji_edit.setText("🏦")

# Get form data
form_data = dialog.get_form_data()

print("\n" + "="*70)
print("FORM DATA MAPPING TEST")
print("="*70)

expected_fields = ['name', 'app_type', 'category', 'app_name', 'website_url', 'login_url', 
                   'username', 'email', 'account_number', 'account_holder', 'notes', 'icon_emoji']

print(f"\n✅ Expected fields: {len(expected_fields)}")
print(f"✅ Returned fields: {len(form_data)}")

all_fields_present = True
for field in expected_fields:
    if field in form_data:
        print(f"  ✅ {field:20} = {str(form_data[field])[:40]}")
    else:
        print(f"  ❌ MISSING: {field}")
        all_fields_present = False

print("\n" + "-"*70)
print("CRITICAL FIELDS FOR DATABASE:")
print("-"*70)

critical_fields = ['app_type', 'username']
for field in critical_fields:
    if field in form_data and form_data[field]:
        print(f"  ✅ {field:20} = {form_data[field]} (NOT NULL ✓)")
    else:
        print(f"  ❌ {field:20} = MISSING OR EMPTY (NULL ✗)")

print("\n" + "="*70)
if all_fields_present:
    print("✅ FORM DATA MAPPING TEST PASSED")
else:
    print("❌ FORM DATA MAPPING TEST FAILED")
print("="*70 + "\n")

sys.exit(0 if all_fields_present else 1)
