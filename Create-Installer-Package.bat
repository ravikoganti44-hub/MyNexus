@echo off
REM Create MyNexus Installer Package
REM This script bundles everything needed for distribution

setlocal enabledelayedexpansion

set "PACKAGE_DIR=.\MyNexus-Installer-1.0.0"
set "VERSION=1.0.0"

echo.
echo ========================================
echo   Creating MyNexus Installer Package
echo ========================================
echo.

REM Create package directory structure
echo Creating package directory structure...
if exist "%PACKAGE_DIR%" (
    echo Removing old package...
    rmdir /s /q "%PACKAGE_DIR%" 2>nul
)

mkdir "%PACKAGE_DIR%\dist"
mkdir "%PACKAGE_DIR%\assets"
mkdir "%PACKAGE_DIR%\config"
mkdir "%PACKAGE_DIR%\docs"

echo.
echo Copying files...

REM Copy main executable
if exist "dist\MyNexus.exe" (
    copy /Y "dist\MyNexus.exe" "%PACKAGE_DIR%\dist\" >nul
    echo   OK MyNexus.exe
) else (
    echo   ERROR: MyNexus.exe not found!
    exit /b 1
)

REM Copy assets
if exist "assets" (
    xcopy /E /I /Q "assets" "%PACKAGE_DIR%\assets" >nul
    echo   OK Assets
)

REM Copy config
if exist "config" (
    xcopy /E /I /Q "config" "%PACKAGE_DIR%\config" >nul
    echo   OK Config
)

REM Copy installers
copy /Y "Install-MyNexus.ps1" "%PACKAGE_DIR%\" >nul
copy /Y "Install-MyNexus.bat" "%PACKAGE_DIR%\" >nul
echo   OK Installers (PowerShell + Batch)

REM Copy documentation
if exist "README.txt" copy /Y "README.txt" "%PACKAGE_DIR%\" >nul
if exist "LICENSE.txt" copy /Y "LICENSE.txt" "%PACKAGE_DIR%\" >nul
if exist "INSTALLATION.md" copy /Y "INSTALLATION.md" "%PACKAGE_DIR%\" >nul
if exist "QUICK_START.md" copy /Y "QUICK_START.md" "%PACKAGE_DIR%\" >nul
if exist "dist\README-INSTALLER.txt" copy /Y "dist\README-INSTALLER.txt" "%PACKAGE_DIR%\" >nul
echo   OK Documentation

REM Create a simple startup guide
echo.  > "%PACKAGE_DIR%\START-HERE.txt"
echo MyNexus Installer Guide >> "%PACKAGE_DIR%\START-HERE.txt"
echo. >> "%PACKAGE_DIR%\START-HERE.txt"
echo How to Install >> "%PACKAGE_DIR%\START-HERE.txt"
echo =============== >> "%PACKAGE_DIR%\START-HERE.txt"
echo. >> "%PACKAGE_DIR%\START-HERE.txt"
echo Option A (Recommended) >> "%PACKAGE_DIR%\START-HERE.txt"
echo 1. Right-click Install-MyNexus.ps1 >> "%PACKAGE_DIR%\START-HERE.txt"
echo 2. Select "Run with PowerShell" >> "%PACKAGE_DIR%\START-HERE.txt"
echo 3. Click Yes when prompted for admin >> "%PACKAGE_DIR%\START-HERE.txt"
echo. >> "%PACKAGE_DIR%\START-HERE.txt"
echo Option B (Alternative) >> "%PACKAGE_DIR%\START-HERE.txt"
echo 1. Right-click Install-MyNexus.bat >> "%PACKAGE_DIR%\START-HERE.txt"
echo 2. Select "Run as administrator" >> "%PACKAGE_DIR%\START-HERE.txt"
echo. >> "%PACKAGE_DIR%\START-HERE.txt"
echo Data Location >> "%PACKAGE_DIR%\START-HERE.txt"
echo =============== >> "%PACKAGE_DIR%\START-HERE.txt"
echo Your financial data will be stored at >> "%PACKAGE_DIR%\START-HERE.txt"
echo C:\Users\[YourUsername]\AppData\Roaming\MyNexus\data\ >> "%PACKAGE_DIR%\START-HERE.txt"
echo. >> "%PACKAGE_DIR%\START-HERE.txt"
echo For more information, see INSTALLATION.md >> "%PACKAGE_DIR%\START-HERE.txt"
echo   OK START-HERE.txt

REM Create version info file
echo MyNexus Version: 1.0.0 > "%PACKAGE_DIR%\VERSION.txt"
echo. >> "%PACKAGE_DIR%\VERSION.txt"
echo For installation see START-HERE.txt >> "%PACKAGE_DIR%\VERSION.txt"
echo. >> "%PACKAGE_DIR%\VERSION.txt"
echo System Requirements >> "%PACKAGE_DIR%\VERSION.txt"
echo OS: Windows 10 or later, 64-bit >> "%PACKAGE_DIR%\VERSION.txt"
echo RAM: 1 GB minimum >> "%PACKAGE_DIR%\VERSION.txt"
echo Disk Space: 100 MB >> "%PACKAGE_DIR%\VERSION.txt"
echo   OK VERSION.txt

echo.
echo ========================================
echo   Package Contents
echo ========================================
echo.
echo The package contains:
echo   - MyNexus.exe (main application)
echo   - Install-MyNexus.ps1 (PowerShell installer)
echo   - Install-MyNexus.bat (Batch installer)
echo   - Installation and user documentation
echo   - Pre-loaded financial templates
echo   - Supporting assets and configuration
echo.

REM Count files
for /f %%A in ('dir /s /b "%PACKAGE_DIR%" 2^>nul ^| find /c /v ""') do (
    echo Total files in package: %%A
)

echo.
echo ========================================
echo   Compression (Optional)
echo ========================================
echo.
echo To create a distributable ZIP file:
echo   Windows 11+: Right-click folder then Compress to ZIP
echo   Or use 7-Zip, WinRAR, or other compression tool
echo.

echo ========================================
echo   Package Location
echo ========================================
echo.
echo Package ready at: %PACKAGE_DIR%
echo.
echo Next steps:
echo   1. Test installation on your system
echo   2. (Optional) Compress to ZIP for distribution
echo   3. Share with users
echo.

echo ========================================
echo   Creation Complete!
echo ========================================
echo.

pause
