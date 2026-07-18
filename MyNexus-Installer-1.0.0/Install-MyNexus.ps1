param(
    [switch]$Silent = $false
)

# MyNexus Installation Script (PowerShell version - More reliable)
# This script installs MyNexus and sets up data folders

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Host "`n" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MyNexus Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This installer requires administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host "`n"
    Read-Host "Press Enter to exit"
    exit 1
}

# Define installation paths
$InstallDir = "$env:ProgramFiles\MyNexus"
$DataDir = "$env:APPDATA\MyNexus\data"
$StartMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MyNexus"
$DesktopPath = "$env:USERPROFILE\Desktop"
$SourceDir = $PSScriptRoot

Write-Host "Installation Paths:" -ForegroundColor Yellow
Write-Host "  Program Folder: $InstallDir"
Write-Host "  Data Folder:    $DataDir"
Write-Host "`n"

# Verify MyNexus.exe exists
$ExePath = Join-Path $SourceDir "dist\MyNexus.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "ERROR: MyNexus.exe not found at $ExePath" -ForegroundColor Red
    Write-Host "Please ensure the dist folder contains MyNexus.exe" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create directories
Write-Host "Creating installation directories..." -ForegroundColor Yellow
@($InstallDir, $DataDir, $StartMenuDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "  ✓ Created: $_" -ForegroundColor Green
    }
}

# Copy files
try {
    Write-Host "`nCopying files..." -ForegroundColor Yellow
    Copy-Item -Path $ExePath -Destination (Join-Path $InstallDir "MyNexus.exe") -Force
    Write-Host "  ✓ Copied MyNexus.exe" -ForegroundColor Green
    
    # Copy assets
    $assetsSource = Join-Path $SourceDir "assets"
    if (Test-Path $assetsSource) {
        Copy-Item -Path $assetsSource -Destination (Join-Path $InstallDir "assets") -Recurse -Force
        Write-Host "  ✓ Copied assets" -ForegroundColor Green
    }
    
    # Copy config
    $configSource = Join-Path $SourceDir "config"
    if (Test-Path $configSource) {
        Copy-Item -Path $configSource -Destination (Join-Path $InstallDir "config") -Recurse -Force
        Write-Host "  ✓ Copied config" -ForegroundColor Green
    }
    
    # Copy documentation
    @("README.txt", "LICENSE.txt", "QUICK_START.md") | ForEach-Object {
        $file = Join-Path $SourceDir $_
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $InstallDir -Force
            Write-Host "  ✓ Copied $_" -ForegroundColor Green
        }
    }
    
} catch {
    Write-Host "ERROR: Failed to copy files: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create shortcuts
Write-Host "`nCreating shortcuts..." -ForegroundColor Yellow
try {
    $WshShell = New-Object -ComObject WScript.Shell
    
    # Desktop shortcut
    $DesktopShortcut = Join-Path $DesktopPath "MyNexus.lnk"
    $Link = $WshShell.CreateShortCut($DesktopShortcut)
    $Link.TargetPath = Join-Path $InstallDir "MyNexus.exe"
    $Link.WorkingDirectory = $InstallDir
    $Link.Description = "MyNexus - Financial Activity & Bill Manager"
    $Link.Save()
    Write-Host "  ✓ Created Desktop shortcut" -ForegroundColor Green
    
    # Start Menu shortcut
    $StartMenuShortcut = Join-Path $StartMenuDir "MyNexus.lnk"
    $Link = $WshShell.CreateShortCut($StartMenuShortcut)
    $Link.TargetPath = Join-Path $InstallDir "MyNexus.exe"
    $Link.WorkingDirectory = $InstallDir
    $Link.Description = "MyNexus - Financial Activity & Bill Manager"
    $Link.Save()
    Write-Host "  ✓ Created Start Menu shortcut" -ForegroundColor Green
    
    # Uninstall shortcut
    $UninstallScript = Join-Path $InstallDir "Uninstall.ps1"
    @'
# Uninstall MyNexus
$Title = "MyNexus Uninstaller"
$CheckBox = $null
$Message = "Uninstall MyNexus?`n`nYour data at %APPDATA%\MyNexus\data will be preserved for re-installation."
$InstallDir = "$env:ProgramFiles\MyNexus"

if ([System.Windows.Forms.MessageBox]::Show($Message, $Title, [System.Windows.Forms.MessageBoxButtons]::YesNo) -eq "Yes") {
    Stop-Process -Name "MyNexus" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MyNexus" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$env:USERPROFILE\Desktop\MyNexus.lnk" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" -Force -ErrorAction SilentlyContinue
    [System.Windows.Forms.MessageBox]::Show("MyNexus has been uninstalled.", $Title)
}
'@ | Out-File -FilePath $UninstallScript -Encoding UTF8
    Write-Host "  ✓ Created Uninstall script" -ForegroundColor Green
    
} catch {
    Write-Host "WARNING: Failed to create some shortcuts: $_" -ForegroundColor Yellow
}

# Register in Windows Registry
Write-Host "`nRegistering application in Windows..." -ForegroundColor Yellow
try {
    $RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus"
    New-Item -Path $RegPath -Force | Out-Null
    
    New-ItemProperty -Path $RegPath -Name "DisplayName" -Value "MyNexus" -Force | Out-Null
    New-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "1.0.0" -Force | Out-Null
    New-ItemProperty -Path $RegPath -Name "Publisher" -Value "ProJ Connect" -Force | Out-Null
    New-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value (Join-Path $InstallDir "MyNexus.exe") -Force | Out-Null
    New-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir -Force | Out-Null
    
    Write-Host "  ✓ Registered in Control Panel" -ForegroundColor Green
    
} catch {
    Write-Host "WARNING: Failed to register in Control Panel: $_" -ForegroundColor Yellow
}

# Installation complete
Write-Host "`n" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "MyNexus has been installed successfully!" -ForegroundColor Green
Write-Host "`nInstallation Details:" -ForegroundColor Yellow
Write-Host "  Program Location: $InstallDir"
Write-Host "  Data Location:    $DataDir"
Write-Host "`nYour shortcuts have been created at:" -ForegroundColor Yellow
Write-Host "  - Desktop"
Write-Host "  - Start Menu"
Write-Host "`nYou can now launch MyNexus from:" -ForegroundColor Yellow
Write-Host "  - Start Menu → MyNexus"
Write-Host "  - Desktop shortcut"
Write-Host "`n"

# Option to launch
if (-not $Silent) {
    $response = Read-Host "Would you like to launch MyNexus now? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process -FilePath (Join-Path $InstallDir "MyNexus.exe") -WorkingDirectory $InstallDir
        Write-Host "`n✓ MyNexus is launching..." -ForegroundColor Green
    }
}

Write-Host "`n"
Read-Host "Press Enter to exit"
