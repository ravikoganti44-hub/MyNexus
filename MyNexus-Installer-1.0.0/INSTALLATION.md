# MyNexus Installation Guide

## Quick Install

### Option 1: PowerShell Installer (Recommended) ⭐

1. Download the **MyNexus installer package** (contains dist/MyNexus.exe and installation scripts)
2. Extract to a temporary folder
3. **Right-click** `Install-MyNexus.ps1`
4. Select **"Run with PowerShell"**
5. Click **"Yes"** when prompted for admin privileges
6. Follow the on-screen prompts

**Advantages:**
- ✅ Most reliable and modern
- ✅ Automatic Start Menu & Desktop shortcuts
- ✅ Proper Windows registry integration
- ✅ Uninstall through Control Panel

### Option 2: Batch Installer

1. Extract the installer package
2. **Right-click** `Install-MyNexus.bat`
3. Select **"Run as administrator"**
4. Follow the on-screen prompts

**Advantages:**
- ✅ Works on all Windows versions
- ✅ No PowerShell knowledge required

### Option 3: Manual Installation

1. Create folder: `C:\Program Files\MyNexus`
2. Copy `dist\MyNexus.exe` to this folder
3. Create a shortcut to `MyNexus.exe` on your Desktop
4. (Optional) Pin to Start Menu

---

## Data Storage

### Location: `%APPDATA%\MyNexus\data\`

**On Windows, this expands to:**
```
C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\
```

### What's stored:
- `projconnect.db` - Your financial data (bills, payments, connected apps)
- All your activity history
- Application preferences

### Important Notes:

✅ **Data is preserved:**
- Between app restarts
- During Windows updates
- When reinstalling the app
- When moving MyNexus to a different folder

❌ **Data is removed only if:**
- You manually delete the AppData folder
- You select "Remove all data" during uninstallation

### Backup Your Data

**To backup your data:**

1. Open File Explorer
2. Press `Ctrl+L` and paste: `%APPDATA%\MyNexus\data`
3. Copy the entire `data` folder to a backup location (USB drive, cloud storage, etc.)

**To restore from backup:**

1. Reinstall MyNexus
2. Close the application completely
3. Paste your backed-up `data` folder back to `C:\Users\[YourUsername]\AppData\Roaming\MyNexus\`
4. Overwrite when prompted
5. Launch MyNexus

---

## Uninstallation

### Using Control Panel (Recommended)

1. Open **Settings** → **Apps** → **Apps & features**
2. Search for **MyNexus**
3. Click **Uninstall**
4. Choose whether to keep or remove your data

### Using Uninstall Script

1. Open Start Menu
2. Right-click **MyNexus** → **Uninstall**

### Manual Uninstallation

1. Delete folder: `C:\Program Files\MyNexus`
2. Delete shortcut: `C:\Users\[YourUsername]\Desktop\MyNexus.lnk`
3. Delete Start Menu folder: `C:\Users\[YourUsername]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\MyNexus`
4. Your data at `%APPDATA%\MyNexus\data\` will be preserved

---

## System Requirements

- **OS:** Windows 10 or later (64-bit)
- **RAM:** 512 MB minimum (1 GB recommended)
- **Disk Space:** 100 MB for installation
- **Admin Rights:** Required for installation only

---

## Troubleshooting

### "Administrator rights required"
- Right-click the installer
- Select "Run as administrator"

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
