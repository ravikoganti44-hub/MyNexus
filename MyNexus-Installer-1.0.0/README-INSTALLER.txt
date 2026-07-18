# MyNexus Installer Package

Welcome to MyNexus - Your Personal Financial Activity & Bill Reminder Manager!

## What's in This Package

```
MyNexus-Installer/
├── dist/
│   └── MyNexus.exe              (Main application)
├── Install-MyNexus.ps1          (PowerShell installer - Recommended)
├── Install-MyNexus.bat          (Batch installer - Alternative)
├── README.txt                    (Quick start guide)
├── LICENSE.txt                   (License information)
├── INSTALLATION.md               (Detailed installation guide)
└── [Other supporting files]
```

## Quick Start (Choose One Method)

### ⭐ Method 1: PowerShell (Easiest & Most Reliable)

1. **Right-click** `Install-MyNexus.ps1`
2. Select **"Run with PowerShell"**
3. Click **"Yes"** when it asks for administrator permission
4. Wait for installation to complete
5. Choose to launch MyNexus immediately or later

### Method 2: Batch File

1. **Right-click** `Install-MyNexus.bat`  
2. Select **"Run as administrator"**
3. Follow the prompts in the command window
4. Choose to launch immediately or later

### Method 3: Manual Installation

1. Create folder: `C:\Program Files\MyNexus`
2. Copy `MyNexus.exe` to that folder
3. Create a Desktop shortcut to the EXE
4. (Optional) Copy to Start Menu

---

## ✨ What Gets Installed

### Application Files
- Location: `C:\Program Files\MyNexus\`
- Files: MyNexus.exe + supporting files
- Size: ~45 MB

### Data Storage
- Location: `C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\`
- Contains: Your financial activities, bills, connected apps, preferences
- **Persists:** Between app runs, system updates, reinstalls

### Shortcuts
- **Desktop:** Quick access shortcut
- **Start Menu:** Organize with your other programs
- **Optional:** Control Panel uninstall

---

## 📊 Features Included

After installation, you'll have access to:

✅ **Activities Management**
- Create and track bills, payments, maintenance
- Set recurring reminders (daily, weekly, monthly, yearly)
- 27 pre-loaded financial activity templates

✅ **Connected Applications**  
- Store and manage logins for financial apps
- 24 pre-loaded app templates:
  - Banks (Chase, BoA, Wells Fargo)
  - Credit Cards (Sapphire, AmEx, Discover)
  - Mortgage providers
  - Insurance companies
  - Utility companies
  - Tax & government sites
  - Investment platforms

✅ **Reminders & Notifications**
- Never miss a bill payment
- Custom reminder times
- Desktop notifications

✅ **Reports & Analytics**
- Track payment history
- Activity statistics
- Budget insights

---

## 🔒 Data Security & Privacy

- **Local Storage:** All data stored locally on your PC, not in the cloud
- **Encrypted Passwords:** Credentials are securely stored (encrypted in future versions)
- **No Cloud Sync:** Your financial data never leaves your computer
- **Portable:** Move MyNexus to a different folder - your data moves with it
- **Backup-Friendly:** Easy to backup and restore

---

## 💾 Important: Your Data Location

Your data is stored at:
```
C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\
```

**To access this folder:**
1. Press `Windows key + R`
2. Type: `%APPDATA%\MyNexus\data`
3. Press Enter

**Backup your data:**
```
Copy the entire data folder to your backup location
```

---

## ⚙️ System Requirements

- **Windows 10** or newer (64-bit)
- **1 GB RAM** minimum (2 GB recommended)
- **50 MB free disk space** for installation
- **Administrator privileges** for installation only

---

## 🆘 Troubleshooting

### "PowerShell" not found?
- Try the **Batch** installer instead (Install-MyNexus.bat)

### "Administrator rights required"?
- Right-click the installer
- Select "Run as administrator"

### Installation fails?
1. Ensure this entire folder is extracted completely
2. All scripts must be in the same directory as `dist/MyNexus.exe`
3. Close any antivirus temporarily during installation
4. Try the batch installer instead

### App won't launch?
1. Check that `dist\MyNexus.exe` exists
2. Verify you have write permissions to `C:\Program Files\`
3. Try manual installation method

### Data not saving?
- Verify: `C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\` exists
- Check Windows file permissions on that folder
- Ensure at least 100 MB free disk space

---

## 📋 Installation Steps (Visual Guide)

### PowerShell Method:
```
1. Extract installer package
2. Right-click Install-MyNexus.ps1
3. Select "Run with PowerShell"
4. Click "Yes" for admin prompt
5. Wait for completion
6. Launch MyNexus
```

### Batch Method:
```
1. Extract installer package
2. Right-click Install-MyNexus.bat
3. Select "Run as administrator"
4. Type Y and press Enter at prompts
5. Wait for completion
6. Close terminal when done
```

---

## 🔄 Upgrading to Newer Versions

1. Download the new installer package
2. Run the installer - it will update to the latest version
3. Your data will be preserved automatically

---

## 🗑️ Uninstalling MyNexus

### Clean Removal (Keep Data):
1. Open **Settings** → **Apps** → **Apps & features**
2. Search for **MyNexus**
3. Click **Uninstall**
4. Choose **"Keep my data"**

### Complete Removal:
1. Go to Settings → Apps → Apps & features
2. Search for **MyNexus**
3. Click **Uninstall**
4. Choose **"Remove all data"**

Your data at `%APPDATA%\MyNexus\` will be deleted.

---

## 📞 Support

- **Documentation:** See `INSTALLATION.md` for detailed guide
- **Quick Start:** See `README.txt` 
- **License:** See `LICENSE.txt`

---

## 🎯 Next Steps After Installation

1. **Launch MyNexus** from Start Menu or Desktop
2. **Explore your financial templates** - we've pre-loaded:
   - 27 financial activities
   - 24 connected app templates
3. **Customize** your activities and app connections
4. **Set reminders** for upcoming bills and payments
5. **Backup your data** regularly (see Data Security section)

---

**Happy organizing! 🎉**

Version: 1.0.0  
For the latest updates, visit: https://mynexus.app
