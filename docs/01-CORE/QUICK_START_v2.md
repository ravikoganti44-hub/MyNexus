# ProJ Connect v2.0 - Quick Reference Guide

## ⚡ New Features at a Glance

### 🔍 Search & Filter (Activities)
**Access:** Activities Page - Top Bar

| Feature | How to Use | Example |
|---------|-----------|---------|
| **Search** | Type in search box | Type "mortgage" → finds all mortgage-related activities |
| **Category Filter** | Select from dropdown | Select "Payment" → shows only payment activities |
| **Status Filter** | Select from dropdown | Select "Overdue" → shows only overdue activities |
| **Sort** | Select from sort dropdown | "Due Date (Soon)" → prioritizes urgent items |
| **Clear Filters** | Click "Clear Filters" | Resets all filters to show all activities |

### ✓ Bulk Operations (Activities)
**Access:** Activities Page - Bulk Actions Bar

| Action | Steps | Notes |
|--------|-------|-------|
| **Select All** | Check "Select All" box | Selects all visible filtered activities |
| **Mark Complete** | Select items → Click "Mark Complete" | ✓ Green success message |
| **Delete Selected** | Select items → Click "Delete" | 🗑️ Requires confirmation |
| **Deselect** | Uncheck individual checkboxes | Can mix selected/unselected |

**Example Workflow:**
```
1. Filter by Category: "Subscription"
2. Click "Select All"
3. Click "✓ Mark Complete" (if paid)
OR
4. Click "🗑️ Delete Selected" (if no longer needed)
```

### 📥📤 Import & Export
**Access:** Activities Page - Export/Import Buttons

**Export to CSV:**
1. Click "📥 Export"
2. Select "📄 Export as CSV"
3. Choose save location
4. Open in Excel or spreadsheet app

**Export to JSON:**
1. Click "📥 Export"
2. Select "📋 Export as JSON"
3. Choose save location
4. Use for backup or data transfer

**Import from File:**
1. Click "📤 Import"
2. Select CSV or JSON file
3. Confirm import
4. Activities added to database

### ⚙️ Settings & Preferences
**Access:** Sidebar - ⚙️ Settings Button

#### 🔔 Notifications
- Enable/Disable notifications
- Toggle notification sound
- Set notification duration (1-60 seconds)
- Choose notification position (top-right, bottom-left, etc.)
- Configure activity reminders

#### 🎨 Display
- Theme selection (Dark, Light, Auto)
- Time format (24h or 12h)
- Calendar view options
- Font size adjustment

#### ⚙️ Behavior
- Auto-refresh interval
- Startup behavior
- Update checking
- Default page at startup

#### 💾 Data & Backup
- Enable automatic backups
- Set backup interval
- Manual backup now
- Restore from backup
- Export all data
- Clear completed activities

---

## 📊 Dashboard Improvements

**New Statistics:**
- 📈 **Completion Rate**: Percentage of completed activities
- 📊 **Category Breakdown**: Top 3 categories by activity count
- 📋 **Activity Metrics**: Total, Due This Week, Overdue, Completed Today

**Quick Access:**
- Click activity cards to see details
- Connected Apps quick launcher (top 5 apps)
- One-click browser launch for app URLs

---

## 🎨 Visual Indicators

### Urgency Colors
```
🔴 RED        = -1 or more days (Overdue)
🟠 ORANGE     = 0 days (Due today)
🟡 YELLOW     = 1-3 days (Urgent)
⚪ NORMAL     = 4+ days (OK)
```

### Status Icons
```
✓  = Completed (Green)
⏳ = Pending (Gray)
```

### Category Icons
```
💳 Payment
📺 Subscription
🔧 Maintenance
🏥 Health
📅 Meeting
✓  Task
other = Other
```

---

## 💡 Pro Tips for Advanced Users

### Tip 1: Advanced Filtering Workflow
```
Goal: Find overdue payment activities
1. Status Filter → "Overdue"
2. Category Filter → "Payment"
3. Sort by → "Due Date (Soon)"
Result: Most urgent overdue payments first
```

### Tip 2: Bulk Cleanup
```
Goal: Clean up completed activities
1. Status Filter → "Completed"
2. Select All
3. Export to CSV (backup)
4. Delete Selected
Result: Cleaner activity list, data preserved in file
```

### Tip 3: Data Backup Strategy
```
Goal: Regular backups
1. Settings → Data & Backup Tab
2. Enable "Automatic backups"
3. Set "Backup interval" → 7 days
4. Optional: Click "💾 Backup Now" for immediate backup
Result: Automatic weekly backups of all data
```

### Tip 4: Custom Sorting
```
Goal: See oldest activities first
1. Sort dropdown → "Created (Old)"
Result: See original activities at top, newest at bottom
```

### Tip 5: Search Optimization
```
Goal: Find specific account
Search: "Chase" → Finds activities, descriptions with "Chase"
Search: "2025" → Finds activities due in 2025
Search: "urgent" → Finds any notes containing "urgent"
```

---

## 🚀 Common Tasks

### Create New Activity
1. Click "➕ Add Activity"
2. Fill in required fields:
   - Title
   - Category
   - Recurrence type
   - Due date
3. Click "Save"

### Edit Activity
1. Find activity in table
2. Click "✏️ Edit" button
3. Modify fields
4. Click "Save"

### Delete Activity
1. Find activity in table
2. Click "🗑️ Delete" button
3. Confirm deletion

### Mark Activity Complete
1. Find activity in table
2. Check the checkbox (first column)
3. Click "✓ Mark Complete"
OR
1. Click "Edit" on activity
2. Check "Completed" checkbox
3. Click "Save"

### Export Activities
1. Click "📥 Export"
2. Choose CSV or JSON
3. Select save location
4. File saved successfully

### Import Activities
1. Click "📤 Import"
2. Select CSV or JSON file
3. Activities imported automatically

---

## ⌨️ Keyboard Shortcuts (Coming Soon)

| Shortcut | Action | Status |
|----------|--------|--------|
| Ctrl+N | New Activity | Coming v2.1 |
| Ctrl+F | Open Search | Coming v2.1 |
| Ctrl+E | Export | Coming v2.1 |
| Ctrl+S | Save Settings | Coming v2.1 |

---

## 🐛 Troubleshooting

### Issue: Search Results Empty
**Solution:**
1. Check spelling of search term
2. Make sure activity actually exists
3. Try broader search term
4. Click "Clear Filters" to reset

### Issue: Export File Not Saving
**Solution:**
1. Check disk space available
2. Verify write permissions to folder
3. Try different file location
4. Check file size (should be < 1MB)

### Issue: Import Shows Error
**Solution:**
1. Verify file format (CSV or JSON)
2. Check file isn't corrupted
3. Ensure all required columns present (for CSV)
4. Try re-exporting from another instance

### Issue: Settings Not Saving
**Solution:**
1. Click "💾 Save Settings" explicitly
2. Check disk space
3. Verify write permissions
4. Restart application

### Issue: Application Runs Slowly
**Solution:**
1. Settings → Behavior → Increase auto-refresh interval
2. Clear completed activities (Settings → Data)
3. Restart application
4. Check system resources

---

## 📞 Getting Help

**Common Questions:**

Q: How do I backup my activities?
A: Settings → Data & Backup → Enable automatic backups OR click "💾 Backup Now"

Q: Can I restore deleted activities?
A: Yes, from backup file. Import the CSV/JSON backup file.

Q: How do I move activities to another computer?
A: Export to CSV/JSON → Move file → Import on new computer

Q: How do I search across multiple criteria?
A: Use combination of Search box + Category filter + Status filter

Q: What happens if I clear completed activities?
A: They are permanently deleted. Export first to create backup!

---

## 🎉 New in v2.0

✅ Advanced search and filtering
✅ Bulk operations (select, complete, delete)
✅ Import/export (CSV & JSON)
✅ Settings panel with preferences
✅ Enhanced dashboard statistics
✅ Visual urgency indicators
✅ Better UI/UX throughout

---

**Version:** 2.0 - Enhanced  
**Last Updated:** March 28, 2026  
**Status:** ✅ Production Ready

For detailed information, see: IMPROVEMENTS_v2.md
