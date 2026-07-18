# MyNexus Installation Guide

**Version 1.1.0 — April 2026**

---

## What's New in This Release

### Net Worth — Advanced Wealth Dashboard
- **7 KPI cards**: Total Assets, Total Liabilities, Net Worth, Month-over-Month change,
  Year-over-Year change, Debt-to-Asset ratio, FIRE Progress %
- **Insight chips**: auto-calculated MoM %, YoY %, best/worst month, snapshot count, FIRE ETA
- **Net Worth Trend sparkline** chart (built-in, no external dependencies)
- **4-tab layout**: Breakdown | Analytics | History | FIRE & Goals
  - *Breakdown*: itemised assets & liabilities with percentage share bars, sorted by value
  - *Analytics*: asset allocation donut chart + top-8 horizontal bar chart
  - *History*: full snapshot table (newest first) with Edit/Delete per row
  - *FIRE & Goals*: FIRE number calculator (25× rule), animated progress bar, projected ETA,
    and a custom wealth-goal calculator with month/year projection
- **Smart "New Snapshot" dialog**: automatically pre-fills with the most recent snapshot's
  values so you only need to update what has changed — no re-entering everything from scratch
- **Category autocomplete**: 30+ suggested asset and liability categories with fuzzy matching
- **Live net-worth preview**: Assets − Liabilities = Net Worth updates in real time as you type

### Budget Tracker
- Budget periods with configurable start/end dates
- Per-category spending limits with progress tracking
- Budget vs actual summary

### Calendar View
- Monthly activity calendar with event overlay
- Detail panel for selected date (max 260 px, 12 pt font)

### Sidebar & Navigation
- All 9 navigation items in a single compact list (4 px spacing)
- Settings integrated directly into the navigation pane
- NAVIGATION section label aligned with button icon column

---

## Quick Install

### Option 1: PowerShell Installer (Recommended)

1. Download the **MyNexus installer package**
2. Extract to a temporary folder
3. **Right-click** `Install-MyNexus.ps1`
4. Select **"Run with PowerShell"**
5. Click **"Yes"** when prompted for admin privileges
6. Follow the on-screen prompts

Advantages:
- Automatic Start Menu & Desktop shortcuts
- Proper Windows registry integration
- Uninstall through Control Panel

### Option 2: Batch Installer

1. Extract the installer package
2. **Right-click** `Install-MyNexus.bat`
3. Select **"Run as administrator"**
4. Follow the on-screen prompts

Advantages:
- Works on all Windows versions
- No PowerShell knowledge required

### Option 3: Run from Source (Python)

**Requirements:** Python 3.11 or later

```bash
# 1. Clone or download the source
cd MyNexus

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python app.py
```

**Dependencies (`requirements.txt`):**
```
PyQt6==6.9.0
PyQt6-sip==13.8.0
APScheduler==3.10.4
SQLAlchemy==2.0.48
Pillow==11.0.0
requests==2.31.0
python-dateutil==2.8.2
pytz==2023.3
wintoast==0.2
plyer==2.1.0
pydantic==2.10.0
cryptography==41.0.7
```

> All charts and graphs are rendered using pure PyQt6 — no matplotlib or additional
> charting libraries are required.

---

## Data Storage

### Location: `%APPDATA%\MyNexus\data\`

**On Windows, this expands to:**
```
C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\
```

### What's stored:
| File | Contents |
|---|---|
| `projconnect.db` | All financial data — activities, connected apps, documents, budgets, net worth snapshots |

### Data is preserved:
- Between app restarts
- During Windows updates
- When reinstalling the app (upgrade installs keep existing data)

### Data is removed only if:
- You manually delete the AppData folder
- You select "Remove all data" during uninstallation

### Backup Your Data

**To backup:**
1. Open File Explorer
2. Press `Ctrl+L` and paste: `%APPDATA%\MyNexus\data`
3. Copy the `data` folder to a backup location (USB, cloud storage, etc.)

**To restore:**
1. Reinstall MyNexus
2. Close the application
3. Paste your backed-up `data` folder to `%APPDATA%\MyNexus\`
4. Overwrite when prompted
5. Launch MyNexus — all your history will be intact

---

## Uninstallation

### Using Control Panel (Recommended)
1. Open **Settings** → **Apps** → **Apps & features**
2. Search for **MyNexus**
3. Click **Uninstall**
4. Choose whether to keep or remove your data

### Manual Uninstallation
1. Delete folder: `C:\Program Files\MyNexus`
2. Delete shortcut: `%USERPROFILE%\Desktop\MyNexus.lnk`
3. Delete Start Menu folder: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\MyNexus`
4. Your data at `%APPDATA%\MyNexus\data\` will be preserved unless you delete it manually

---

## System Requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| RAM | 512 MB | 1 GB |
| Disk Space | 150 MB | 300 MB |
| Python (source only) | 3.11 | 3.13 |
| Admin Rights | Required for install only | — |

---

## Troubleshooting

### "Administrator rights required"
Right-click the installer and select **"Run as administrator"**.

### App won't launch after install
1. Verify `C:\Program Files\MyNexus\MyNexus.exe` exists
2. Check Windows Defender / antivirus isn't blocking it
3. Try running from source with `python app.py` to see error output

### Net Worth section shows $0
This was a known bug in v1.0.0 (SQLAlchemy session expiry). It is fixed in v1.1.0.
If upgrading, no data migration is needed — existing snapshots will display correctly.

### Database errors on first launch
The app creates its database automatically on first run. If you see errors, ensure the
`%APPDATA%\MyNexus\data\` folder is writable by your Windows user account.

### "File not found" during installation
- Extract the installer package completely
- Ensure all files are in the same directory
- Try again

### App won't start after installation
1. Close all instances of MyNexus
2. Delete the data folder: `%APPDATA%\MyNexus\data`
3. Restart MyNexus (it will recreate the database)

### "Cannot find MyNexus.exe"
- Run the installer from the directory containing the dist folder
- Or manually copy `dist\MyNexus.exe` to `C:\Program Files\MyNexus\`

### Data not persisting
1. Verify data location: `%APPDATA%\MyNexus\data\`
2. Check file permissions on that folder
3. Ensure enough free disk space (at least 100 MB)

---

## Portable Mode (Advanced)

To use MyNexus without installation:

1. Copy `dist\MyNexus.exe` to any folder
2. Create a subfolder named `data` in the same location
3. Run `MyNexus.exe` directly

**Note:** Portable mode stores data relative to the EXE location, not in AppData.

---

## Support & Documentation

- **Documentation:** See `QUICK_START.md`
- **Issues:** Check the logs in the app's Settings tab
- **Website:** https://mynexus.app

---

**Version:** 1.0.0  
**Last Updated:** March 2026
