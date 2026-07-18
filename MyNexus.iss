; MyNexus Installer Script
; Uses InnoSetup to create a professional Windows installer
; This installer will:
; - Install MyNexus.exe to Program Files
; - Create Start Menu shortcuts
; - Create Desktop shortcut
; - Set up data folder in AppData
; - Seed sample data on fresh install (skips if prior data exists)
; - Handle uninstallation properly

[Setup]
AppName=MyNexus
AppVersion=1.0.1
AppPublisher=ProJ Connect
AppPublisherURL=https://mynexus.app
AppSupportURL=https://mynexus.app/support
AppUpdatesURL=https://mynexus.app/updates
DefaultDirName={autopf}\MyNexus
DefaultGroupName=MyNexus
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoAfterFile=README.txt
OutputDir=dist\installer
OutputBaseFilename=MyNexus-Setup-1.0.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\icons\my_nexus_setup.ico
UninstallDisplayIcon={app}\MyNexus.exe

; Preserve existing installation directory on upgrade
DirExistsWarning=no
; Allow upgrading over existing install without removing files first
UsePreviousAppDir=yes

; Request admin privileges for installation
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "dist\MyNexus.exe"; DestDir: "{app}"; Flags: ignoreversion
; Assets
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Config
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
; Seed script (runs after install to populate sample data for new users)
Source: "seed_sample_data.py"; DestDir: "{app}"; Flags: ignoreversion
; Documentation
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\MyNexus"; Filename: "{app}\MyNexus.exe"; WorkingDir: "{app}"; IconFilename: "{app}\MyNexus.exe"; Comment: "Personal Finance & Activity Manager"
Name: "{group}\{cm:UninstallProgram,MyNexus}"; Filename: "{uninstallexe}"
; Desktop shortcut (created by default)
Name: "{autodesktop}\MyNexus"; Filename: "{app}\MyNexus.exe"; WorkingDir: "{app}"; IconFilename: "{app}\MyNexus.exe"; Tasks: desktopicon; Comment: "Personal Finance & Activity Manager"
; Quick Launch shortcut (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\MyNexus"; Filename: "{app}\MyNexus.exe"; WorkingDir: "{app}"; IconFilename: "{app}\MyNexus.exe"; Tasks: quicklaunchicon

[Run]
; Seed sample data ONLY on fresh install (seeder skips if DB already has data)
Filename: "{app}\MyNexus.exe"; Parameters: "--seed-once"; Description: "Loading sample data..."; Flags: runhidden waituntilterminated; Check: IsNewInstall
; Run the app after installation (optional)
Filename: "{app}\MyNexus.exe"; Description: "{cm:LaunchProgram,MyNexus}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

[Code]
{ ─────────────────────────────────────────────────────────────────────────── }
{ Helpers                                                                      }
{ ─────────────────────────────────────────────────────────────────────────── }

{ Returns True when this is a brand-new installation (no prior version found). }
function IsNewInstall: Boolean;
begin
  Result := not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus_is1');
  { Also check the 64-bit registry hive on 64-bit Windows }
  if Result then
    Result := not RegKeyExists(HKLM64, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MyNexus_is1');
end;

{ ─────────────────────────────────────────────────────────────────────────── }
{ Wizard events                                                                }
{ ─────────────────────────────────────────────────────────────────────────── }

procedure InitializeWizard;
begin
  { Ensure user data directory exists in every case }
  CreateDir(ExpandConstant('{userappdata}\MyNexus'));
  CreateDir(ExpandConstant('{userappdata}\MyNexus\data'));
end;

procedure CurPageChanged(CurPageID: Integer);
var
  DataNote: String;
begin
  if CurPageID = wpFinished then
  begin
    if IsNewInstall then
      DataNote := 'Sample data has been pre-loaded to help you explore each feature.'
    else
      DataNote := 'Your existing data has been preserved. Nothing was overwritten.';

    WizardForm.InfoAfterMemo.Lines.Clear;
    WizardForm.InfoAfterMemo.Lines.Add('Installation Complete!');
    WizardForm.InfoAfterMemo.Lines.Add('');
    WizardForm.InfoAfterMemo.Lines.Add(DataNote);
    WizardForm.InfoAfterMemo.Lines.Add('');
    WizardForm.InfoAfterMemo.Lines.Add('Your personal data is stored at:');
    WizardForm.InfoAfterMemo.Lines.Add(ExpandConstant('{userappdata}\MyNexus\data\'));
    WizardForm.InfoAfterMemo.Lines.Add('');
    WizardForm.InfoAfterMemo.Lines.Add('This means your data:');
    WizardForm.InfoAfterMemo.Lines.Add('  * Persists between app updates');
    WizardForm.InfoAfterMemo.Lines.Add('  * Is never touched by the installer');
    WizardForm.InfoAfterMemo.Lines.Add('  * Can be backed up from the location above');
    WizardForm.InfoAfterMemo.Lines.Add('');
    WizardForm.InfoAfterMemo.Lines.Add('Click Finish to launch MyNexus!');
  end;
end;
