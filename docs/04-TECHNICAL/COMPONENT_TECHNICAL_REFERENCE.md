# View Components - Technical Reference

## Component Hierarchy

```
ConnectedAppsWidget (Main container)
├── ViewSelector UI (🎴 📋 ⊞ ⚡ buttons)
├── ScrollArea
│   └── cards_container (QWidget with QGridLayout)
│       └── Content based on view mode:
│           ├── Card View: ApplicationCardWidget (2 cols)
│           ├── List View: ListApplicationItemWidget (1 col)
│           ├── Grid View: CompactApplicationCardWidget (3 cols)
│           └── Compact: CompactApplicationCardWidget (4 cols)
└── Action Buttons (Add, Refresh)
```

## Component Details

### 1. ApplicationCardWidget
**Used In:** Card View (DEFAULT)

**Characteristics:**
- Full-height card with detailed information
- Minimum height: 280px
- Colored category indicator bar at top
- Large emoji icon (36px)
- Complete information display

**Display Elements:**
1. Top colored bar (4px height, category color)
2. Header section:
   - Icon (36px emoji)
   - App name (bold, 13pt)
   - Provider (cyan, 11pt)
   - Status indicator (✓ Active)
3. Content divider
4. Details grid:
   - Account holder
   - Username (masked)
   - Account number (masked)
   - Type (color-coded)
   - Last accessed
5. Notes section (if available)
6. Action buttons (36×36px)

**Properties:**
```python
- setMinimumHeight(280)
- Border: 2px solid, rounded 14px
- Hover: Cyan border + lighter background
- Spacing: 12px between elements
- Padding: 16px content area
```

---

### 2. CompactApplicationCardWidget
**Used In:** Grid View (3 columns) & Compact View (4 columns)

**Characteristics:**
- Compact horizontal card
- Height: 80-100px
- Left-aligned colored bar
- Minimal information
- Quick action buttons

**Display Elements:**
1. Left colored bar (4px width, category color)
2. Icon (24px emoji)
3. App name (bold, 11pt)
4. Provider name (gray, 9px)
5. Action buttons (28×28px, 4 buttons)

**Properties:**
```python
- setMinimumHeight(80)
- setMaximumHeight(100)
- Border: 1px solid, rounded 8px
- Hover: Cyan border + darker background
- Horizontal layout (HBox)
- Total padding: 10px
```

**Button Layout:**
- Left side: Icon + Name/Provider info
- Right side: 4 action buttons in row

---

### 3. ListApplicationItemWidget
**Used In:** List View (1 column)

**Characteristics:**
- Full-width list item
- Height: 60px
- Information displayed in columns
- Proper alignment for scanning

**Display Elements:**
1. Icon (24×24px, left)
2. Info grid (center):
   - Row 0: Name (left) | Provider (right)
   - Row 1: Type (left) | Last Accessed (right)
3. Action buttons (32×32px, right)

**Properties:**
```python
- setMinimumHeight(60)
- Border: 1px solid, rounded 6px
- Hover: Cyan border + background change
- Grid layout with proper column stretching
- Padding: 12px horizontal, 10px vertical
```

**Column Width:**
- Icon: 40px fixed
- Info: Flex (stretches to available space)
- Actions: Fixed width for buttons

---

## Button Styling

### Card View Buttons (36×36px)
```css
/* Copy */
background-color: #1e90ff
color: #ffffff
border: none
border-radius: 6px

/* Open */
background-color: #10d981
color: #ffffff
border: none
border-radius: 6px

/* Edit */
background-color: #00d4ff
color: #000000
border: none
border-radius: 6px

/* Delete */
background-color: #f87171
color: #ffffff
border: none
border-radius: 6px
```

### List & Grid View Buttons (28-32px)
- Same colors as above
- Smaller fixed sizes
- Compact spacing

### Hover States
```
Copy:   #3b82f6 (lighter blue)
Open:   #34d399 (lighter green)
Edit:   #00ffff (bright cyan)
Delete: #fb7185 (lighter red)
```

---

## Layout Calculations

### Card View
```
Available width: W pixels
Cards per row: 2 (fixed)
Card width: (W - spacing) / 2
Spacing: 20px
Padding: 0px (cards_container)
```

### List View
```
Container width: W pixels
Item width: W (full width)
Item height: 60px
Spacing: 8px between items
```

### Grid View
```
Available width: W pixels
Cards per row: 3 (fixed)
Card width: (W - 2×spacing) / 3
Spacing: 20px
Minimum card width: 150px
```

### Compact View
```
Available width: W pixels
Cards per row: 4 (fixed)
Card width: (W - 3×spacing) / 4
Spacing: 20px
Minimum card width: 120px
```

---

## State Management

### View Mode Persistence
```python
self.current_view = self.VIEW_CARD  # Default

def set_view_mode(view_mode):
    self.current_view = view_mode
    # Update button styles
    # Call refresh_apps()
    # Re-render with new layout
```

### Button State Tracking
```python
self.view_buttons = {
    "card": button_widget,
    "list": button_widget,
    "grid": button_widget,
    "compact": button_widget,
}
```

### Rendering Methods
```python
def refresh_apps():
    # Clear layout
    # Load applications
    # Call render based on current_view:
    #   - render_card_view()
    #   - render_list_view()
    #   - render_grid_view()
    #   - render_compact_view()
```

---

## Color Reference

### Component Colors
| Element | Color | Hex |
|---------|-------|-----|
| Card Background | Dark Blue | #1a1a2e |
| Card Hover | Lighter Blue | #252541 |
| Text Primary | White | #ffffff |
| Text Secondary | Gray | #b0b0c0 |
| Accent | Cyan | #00d4ff |
| Border Normal | Dark Gray | #2a2a3e |
| Border Focus | Cyan | #00d4ff |

### Category Top Bar Colors
| Type | Color | Hex |
|------|-------|-----|
| Mortgage | Red | #ff6b6b |
| Banking | Teal | #4ecdc4 |
| Credit Card | Gold | #ffd93d |
| Investment | Green | #6bcf7f |
| Utilities | Light Green | #a8e6cf |
| Insurance | Plum | #dda0dd |
| Medical | Light Red | #ff9999 |
| Subscription | Purple | #b19cd9 |
| Other | Gray | #95a5a6 |

### Action Button Colors
| Action | Color | Hex |
|--------|-------|-----|
| Copy | Blue | #1e90ff |
| Open | Green | #10d981 |
| Edit | Cyan | #00d4ff |
| Delete | Red | #f87171 |

---

## Responsive Breakpoints

### Desktop (> 1200px)
- Card: 2 columns
- Grid: 3 columns
- Compact: 4 columns
- Large spacing and padding

### Tablet (768px - 1200px)
- Card: 2 columns
- Grid: 2-3 columns
- Compact: 3-4 columns
- Medium spacing

### Mobile (< 768px)
- Card: 1 column
- Grid: 2 columns
- Compact: 2-3 columns
- Minimal spacing

---

## Performance Considerations

### Rendering Optimization
- Views cleared and re-built on mode change
- Grid layout with proper column definitions per view
- Scroll area with widget resizing enabled
- Lazy loading for large datasets

### Memory Management
- Old widgets deleted on clear
- QLayoutItem properly removed
- No dangling references after widget deletion

### UI Responsiveness
- Instant view switching (no animation delays)
- Smooth scrolling with optimized layout
- Button clicks processed immediately
- No blocking operations during rendering

---

## Data Flow

```
User Interaction (click view button)
    ↓
set_view_mode(new_mode)
    ↓
Update button styles (update view_buttons dict)
    ↓
refresh_apps()
    ↓
Clear card_layout
    ↓
Get applications from database
    ↓
Render based on current_view:
    - For each app, create appropriate widget type
    - Add to grid layout with proper row/col positions
    - Add stretch at bottom
    ↓
Display updated content
    ↓
User can interact with actions
```

---

## Testing Guidelines

### Unit Tests
- [ ] Each view renders correctly
- [ ] Button click handlers work
- [ ] View switching updates styles
- [ ] Grid layout positions items correctly
- [ ] Scrolling works smoothly
- [ ] Empty state displays properly

### Integration Tests
- [ ] All actions work in all views
- [ ] Adding/editing/deleting works across views
- [ ] View switching preserves data
- [ ] Copy/Open/Edit/Delete function in each view

### UI Tests
- [ ] Colors display correctly
- [ ] Buttons have proper hover effects
- [ ] Text renders clearly
- [ ] No overlapping elements
- [ ] Proper spacing throughout
- [ ] Icons display correctly
- [ ] Responsive layout on different sizes

---

**Version**: 1.0  
**File**: src/ui/components/connected_apps.py  
**Components**: 4 (ApplicationCardWidget, CompactApplicationCardWidget, ListApplicationItemWidget, ConnectedAppsWidget)  
**Status**: ✅ Complete
