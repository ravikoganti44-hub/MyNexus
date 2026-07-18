# ProJ Connect UI - Quick Reference Guide

## 🎯 Component Quick Start

### Import & Use Stat Cards
```python
from src.ui.components.stat_card import StatCard

# Create stat card
card = StatCard("Total Activities", "42", "📊", "#58a6ff")

# Update value
card.set_value("50")

# Change color
card.set_color("#3fb950")

# Add to layout
layout.addWidget(card)
```

### Import & Use Premium Buttons
```python
from src.ui.components.premium_button import PremiumButton

# Primary button with icon
btn_save = PremiumButton("Save", 
                         style=PremiumButton.Style.PRIMARY,
                         icon_name="save")

# Secondary button
btn_cancel = PremiumButton("Cancel",
                          style=PremiumButton.Style.SECONDARY)

# Danger button
btn_delete = PremiumButton("Delete",
                          style=PremiumButton.Style.DANGER,
                          icon_name="delete")

# Success button
btn_confirm = PremiumButton("Confirm",
                           style=PremiumButton.Style.SUCCESS,
                           icon_name="check")

# Flat button
btn_more = PremiumButton("More",
                        style=PremiumButton.Style.FLAT)
```

### Using Icons
```python
from src.ui.styles.icon_manager import IconManager, ICON_PRIMARY

# Method 1: Direct usage
icon = IconManager.get_icon("dashboard", size=24, color="#58a6ff")
button.setIcon(icon)

# Method 2: Pre-configured colors
from src.ui.styles.icon_manager import (
    ICON_PRIMARY, ICON_SUCCESS, ICON_ERROR, 
    ICON_WARNING, ICON_SECONDARY, ICON_GRAY
)

primary_icon = ICON_PRIMARY("dashboard")   # #58a6ff
success_icon = ICON_SUCCESS("check")       # #3fb950
error_icon = ICON_ERROR("error")           # #f85149
warning_icon = ICON_WARNING("warning")     # #d29922
```

## 🎨 Available Icons
```
dashboard      activities      integrations    connected_apps  settings
refresh        add             delete          edit            calendar
warning        check           error           search          close
menu           download        upload          save            mail
```

## 🌈 Color Reference
```python
# Access theme colors
from src.ui.styles.theme import DARK_THEME

DARK_THEME["bg_primary"]      # #0d1117 - Main background
DARK_THEME["bg_secondary"]    # #161b22 - Elevated surface
DARK_THEME["bg_tertiary"]     # #21262d - Lighter surface
DARK_THEME["accent_primary"]  # #58a6ff - Primary blue
DARK_THEME["success"]         # #3fb950 - Green
DARK_THEME["error"]           # #f85149 - Red
DARK_THEME["warning"]         # #d29922 - Amber
DARK_THEME["text_primary"]    # #ffffff - White text
DARK_THEME["text_secondary"]  # #8b949e - Gray text
DARK_THEME["border_color"]    # #30363d - Subtle border
```

## 🏗️ Layout Patterns

### Stat Cards Row
```python
stats_layout = QHBoxLayout()
stats_layout.addWidget(StatCard("Total", "42", "📊", "#58a6ff"))
stats_layout.addWidget(StatCard("Due", "5", "📅", "#d29922"))
stats_layout.addWidget(StatCard("Overdue", "2", "⚠️", "#f85149"))
stats_layout.addWidget(StatCard("Done", "38", "✓", "#3fb950"))
main_layout.addLayout(stats_layout)
```

### Header with Action Buttons
```python
header_layout = QHBoxLayout()
title = QLabel("Page Title")
title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
title.setObjectName("titleLabel")

btn_add = PremiumButton("Add", icon_name="add")
btn_refresh = PremiumButton("Refresh", icon_name="refresh")

header_layout.addWidget(title)
header_layout.addStretch()
header_layout.addWidget(btn_add)
header_layout.addWidget(btn_refresh)
```

### Card Container
```python
card = QFrame()
card.setObjectName("card")  # Auto-styled as premium card
layout = QVBoxLayout()
layout.setContentsMargins(16, 16, 16, 16)
# ... add content
card.setLayout(layout)
```

## 📋 Common Patterns

### Create Table with Premium Styling
```python
table = QTableWidget()
table.setColumnCount(3)
table.setHorizontalHeaderLabels(["Name", "Status", "Date"])
table.setAlternatingRowColors(True)
# Table automatically styled by theme
```

### Form Container
```python
form_frame = QFrame()
form_frame.setObjectName("card")
form_layout = QFormLayout()
form_layout.setContentsMargins(16, 16, 16, 16)
form_layout.setSpacing(12)

form_layout.addRow("Name:", QLineEdit())
form_layout.addRow("Email:", QLineEdit())

form_frame.setLayout(form_layout)
```

## 🎯 Design Principles

1. **Use Components**: Always use `PremiumButton` and `StatCard` for consistency
2. **Icon It**: Replace emoji with SVG icons using IconManager
3. **Follow Colors**: Use colors from `DARK_THEME` dictionary
4. **Spacing**: Use 8px, 12px, 16px, 20px, 24px intervals
5. **Cards**: Wrap content in `QFrame` with `objectName="card"`
6. **Buttons**: Use `PremiumButton` with appropriate style

## 🔍 File Locations

| Component | File |
|-----------|------|
| Theme | `src/ui/styles/theme.py` |
| Icons | `assets/icons/` |
| Icon Manager | `src/ui/styles/icon_manager.py` |
| Stat Card | `src/ui/components/stat_card.py` |
| Premium Button | `src/ui/components/premium_button.py` |

## 📚 Documentation Files

- `UI_PREMIUM_DESIGN.md` - Comprehensive design guide
- `UI_UPGRADE_SUMMARY.md` - Complete upgrade summary
- This file - Quick reference

## 💡 Pro Tips

1. **Icon Sizing**: Use 20-24px for most buttons
2. **Color Consistency**: Use theme colors, not hardcoded hex values
3. **Reusable Components**: Create component classes for complex UI
4. **QSS Classes**: Use `objectName` for QSS class-like styling
5. **Spacing**: Use layouts with proper margins and spacing

---

**Ready to build premium UIs!** 🚀
