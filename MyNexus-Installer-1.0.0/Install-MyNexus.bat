@echo off
REM MyNexus Installation Script
REM This script installs MyNexus and sets up the data folder

title MyNexus Installer
color 0A

echo.
echo ========================================
echo   MyNexus Financial Manager Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: This installer requires administrator privileges.
    echo Please right-click the installer and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

setlocal enabledelayedexpansion

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Set installation paths
set "INSTALL_DIR=%ProgramFiles%\MyNexus"
set "DATA_DIR=%APPDATA%\MyNexus\data"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\MyNexus"
set "DESKTOP=%USERPROFILE%\Desktop"

echo Installation Paths:
echo   Program Folder: !INSTALL_DIR!
echo   Data Folder:    !DATA_DIR!
echo.

REM Check if MyNexus.exe exists
if not exist "!SCRIPT_DIR!\dist\MyNexus.exe" (
    echo ERROR: MyNexus.exe not found in dist folder!
    echo Please ensure MyNexus.exe is in the dist subfolder.
    echo Looked in: !SCRIPT_DIR!\dist\
    echo.
    pause
    exit /b 1
)

REM Create directories
echo Creating directories...
mkdir "!INSTALL_DIR!" 2>nul
mkdir "!DATA_DIR!" 2>nul
mkdir "!START_MENU!" 2>nul

REM Copy MyNexus executable
echo Copying MyNexus.exe...
copy /Y "!SCRIPT_DIR!\dist\MyNexus.exe" "!INSTALL_DIR!\MyNexus.exe" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy MyNexus.exe
    pause
    exit /b 1
)

REM Copy assets and config if they exist
if exist "!SCRIPT_DIR!\assets" (
    echo Copying assets...
    xcopy /E /I /Y "!SCRIPT_DIR!\assets" "!INSTALL_DIR!\assets" >nul
)

if exist "!SCRIPT_DIR!\config" (
    echo Copying config...
    xcopy /E /I /Y "!SCRIPT_DIR!\config" "!INSTALL_DIR!\config" >nul
)

REM Copy documentation
if exist "!SCRIPT_DIR!\README.txt" copy /Y "!SCRIPT_DIR!\README.txt" "!INSTALL_DIR!\" >nul
if exist "!SCRIPT_DIR!\LICENSE.txt" copy /Y "!SCRIPT_DIR!\LICENSE.txt" "!INSTALL_DIR!\" >nul
if exist "!SCRIPT_DIR!\QUICK_START.md" copy /Y "!SCRIPT_DIR!\QUICK_START.md" "!INSTALL_DIR!\" >nul

REM Create shortcuts using VBScript
echo Creating shortcuts...

REM Desktop shortcut
set "VBS_DESKTOP=%TEMP%\create_desktop_shortcut.vbs"
>"%VBS_DESKTOP%" (
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "!DESKTOP!\MyNexus.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "!INSTALL_DIR!\MyNexus.exe"
    echo oLink.WorkingDirectory = "!INSTALL_DIR!"
    echo oLink.Description = "MyNexus - Financial Activity & Bill Reminder Manager"
    echo oLink.Save
)
cscript /nologo "%VBS_DESKTOP%"
del "%VBS_DESKTOP%"

REM Start Menu shortcut
set "VBS_START=%TEMP%\create_startmenu_shortcut.vbs"
>"%VBS_START%" (
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "!START_MENU!\MyNexus.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "!INSTALL_DIR!\MyNexus.exe"
    echo oLink.WorkingDirectory = "!INSTALL_DIR!"
    echo oLink.Description = "MyNexus - Financial Activity & Bill Reminder Manager"
    echo oLink.Save
)
cscript /nologo "%VBS_START%"
del "%VBS_START%"

REM Add to Windows Registry for uninstall
echo Registering application...
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "DisplayName" /d "MyNexus" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "DisplayVersion" /d "1.0.0" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "Publisher" /d "ProJ Connect" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "DisplayIcon" /d "!INSTALL_DIR!\MyNexus.exe" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "InstallLocation" /d "!INSTALL_DIR!" /f >nul
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" ^
    /v "UninstallString" /d "!INSTALL_DIR!\Uninstall.bat" /f >nul

REM Create uninstaller
echo Creating uninstaller...
set "UNINSTALL_BAT=!INSTALL_DIR!\Uninstall.bat"
>"%UNINSTALL_BAT%" (
    echo @echo off
    echo title MyNexus Uninstaller
    echo echo.
    echo echo ========================================
    echo echo   MyNexus - Uninstalling...
    echo echo ========================================
    echo echo.
    echo.
    echo taskkill /f /im MyNexus.exe 2^>nul
    echo.
    echo echo Removing shortcuts...
    echo del "!DESKTOP!\MyNexus.lnk" 2^>nul
    echo del "!START_MENU!\MyNexus.lnk" 2^>nul
    echo rmdir "!START_MENU!" 2^>nul
    echo.
    echo echo Removing program files...
    echo rmdir /s /q "!INSTALL_DIR!" 2^>nul
    echo.
    echo echo Removing registry entries...
    echo reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus" /f 2^>nul
    echo.
    echo echo Data folder at !DATA_DIR! has been preserved for re-installation.
    echo echo.
    echo echo Uninstallation complete!
    echo pause
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo MyNexus has been installed successfully!
echo.
echo Program Location: !INSTALL_DIR!
echo Data Location:    !DATA_DIR!
echo.
echo Your shortcuts have been created on:
echo   - Desktop
echo   - Start Menu
echo.
echo Launch MyNexus from the Start Menu or Desktop shortcut.
echo.
echo ========================================
echo.

REM Option to launch MyNexus
set /p LAUNCH="Would you like to launch MyNexus now? (Y/N): "
if /i "!LAUNCH!"=="Y" (
    start "" "!INSTALL_DIR!\MyNexus.exe"
)

pause
endlocal
