#ifndef AppVersion
  #define AppVersion "0.1.12"
#endif
#ifndef BuildDir
  #define BuildDir "..\build\installer"
#endif
#ifndef InstallPrivileges
  #define InstallPrivileges "admin"
#endif
#ifndef SetupOutputDir
  #define SetupOutputDir "..\dist"
#endif
#ifndef SetupOutputName
  #define SetupOutputName "iDevice-Modded-Setup-" + AppVersion + "-x64"
#endif

#define AppName "iDevice Modded"
#define AppPublisher "iDevice Modded contributors"
#define ProjectRoot ".."

[Setup]
AppId={{A4EC4CF8-9DCE-40BA-97B1-9303E5D2C801}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com/kevinW0W/iDevice-Modded
AppSupportURL=https://github.com/kevinW0W/iDevice-Modded/issues
AppUpdatesURL=https://github.com/kevinW0W/iDevice-Modded/releases
DefaultDirName={autopf}\iDesktop
DefaultGroupName=iDevice Modded
DisableProgramGroupPage=yes
PrivilegesRequired={#InstallPrivileges}
ArchitecturesAllowed=x64compatible and not arm64
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
WizardImageFile={#BuildDir}\wizard.bmp
WizardSmallImageFile={#ProjectRoot}\assets\idesktop.png
SetupIconFile={#ProjectRoot}\assets\idesktop.ico
UninstallDisplayIcon={app}\assets\idesktop.ico
UninstallDisplayName=iDevice Modded
Uninstallable=yes
OutputDir={#SetupOutputDir}
OutputBaseFilename={#SetupOutputName}
Compression=lzma2/ultra64
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoVersion={#AppVersion}.0
VersionInfoProductName=iDevice Modded
VersionInfoProductVersion={#AppVersion}.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=iDevice Modded Windows installer

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#BuildDir}\python-installer.exe"; DestName: "python-installer.exe"; Flags: dontcopy noencryption
Source: "{#BuildDir}\wheelhouse.zip"; DestName: "wheelhouse.zip"; Flags: dontcopy noencryption
Source: "{#BuildDir}\installing-image.png"; DestName: "installing-image.png"; Flags: dontcopy
Source: "bootstrap.py"; DestName: "bootstrap.py"; Flags: dontcopy noencryption
Source: "{#ProjectRoot}\idesktop\*.py"; DestDir: "{app}\idesktop"; Flags: ignoreversion
Source: "{#ProjectRoot}\assets\idesktop.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "{#ProjectRoot}\assets\idesktop.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "{#ProjectRoot}\assets\idesktop-install-preview.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "{#ProjectRoot}\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\..\iDesktop.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\extras\*"; DestDir: "{app}\extras"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "stop-processes.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion

[InstallDelete]
Type: files; Name: "{app}\iDesktop.vbs"

[Icons]
Name: "{autoprograms}\iDevice Modded"; Filename: "{code:GetPythonwExe}"; Parameters: "-m idesktop.splash"; WorkingDir: "{app}"; IconFilename: "{app}\assets\idesktop.ico"; Comment: "Mirror and control your iPhone"; Check: CreateStartMenuShortcuts
Name: "{autoprograms}\Uninstall iDevice Modded"; Filename: "{uninstallexe}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\idesktop.ico"; Check: CreateStartMenuShortcuts
Name: "{autodesktop}\iDevice Modded"; Filename: "{code:GetPythonwExe}"; Parameters: "-m idesktop.splash"; WorkingDir: "{app}"; IconFilename: "{app}\assets\idesktop.ico"; Comment: "Mirror and control your iPhone"; Check: CreateDesktopShortcut

[UninstallRun]
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""{app}\installer\stop-processes.ps1"" -InstallRoot ""{app}"""; Flags: runhidden waituntilterminated; RunOnceId: "StopiDesktopProcesses"
FileName: "{app}\runtime\uninstall.exe"; Parameters: "/quiet"; Flags: runhidden waituntilterminated; Check: FileExists(ExpandConstant('{app}\runtime\uninstall.exe')); RunOnceId: "UninstallBundledPython"

[Code]
var
  OptionsPage: TWizardPage;
  OptionsCard: TPanel;
  StartMenuShortcutCheck: TNewCheckBox;
  DesktopShortcutCheck: TNewCheckBox;
  InstallPythonCheck: TNewCheckBox;
  AppleDevicesCheck: TNewCheckBox;
  InstallingArtwork: TBitmapImage;
  ExistingPythonExe: String;

function SendMessage(hWnd: HWND; Msg: Cardinal; wParam: Integer;
  lParam: Integer): Integer;
external 'SendMessageW@user32.dll stdcall';

function SetWindowTheme(hWnd: HWND; const SubAppName, SubIdList: String): Integer;
external 'SetWindowTheme@uxtheme.dll stdcall';

function FindCompatiblePython(const Filename, LauncherArgs: String): String;
var
  CheckFile: String;
  Parameters: String;
  ResultCode: Integer;
  DetectedExe: AnsiString;
begin
  Result := '';
  if not FileExists(Filename) then
    exit;

  CheckFile := ExpandConstant('{tmp}\idesktop-python-check.txt');
  DeleteFile(CheckFile);
  Parameters := LauncherArgs +
    '-c "import sys;sys.version_info[:2] == (3,13) and sys.maxsize > 2**32 and open(sys.argv[1],chr(119)).write(sys.executable)" "' +
    CheckFile + '"';
  if Exec(Filename, Parameters, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and
    (ResultCode = 0) and LoadStringFromFile(CheckFile, DetectedExe) then
    Result := Trim(DetectedExe);
  DeleteFile(CheckFile);
end;

function DetectCompatiblePython: String;
var
  InstallPath: String;
  Candidate: String;
  Launcher: String;
begin
  Result := '';

  if RegQueryStringValue(HKLM64, 'Software\Python\PythonCore\3.13\InstallPath',
    '', InstallPath) or
    RegQueryStringValue(HKCU64, 'Software\Python\PythonCore\3.13\InstallPath',
    '', InstallPath) then
  begin
    Candidate := FindCompatiblePython(AddBackslash(InstallPath) + 'python.exe', '');
    if Candidate <> '' then
    begin
      Result := Candidate;
      exit;
    end;
  end;

  Candidate := FileSearch('python.exe', GetEnv('PATH'));
  Result := FindCompatiblePython(Candidate, '');
  if Result <> '' then
    exit;

  Launcher := FileSearch('py.exe', GetEnv('PATH'));
  Result := FindCompatiblePython(Launcher, '-3.13-64 ');
end;

function GetPythonwExe(Param: String): String;
begin
  if InstallPythonCheck.Checked then
    Result := ExpandConstant('{app}\runtime\pythonw.exe')
  else
    Result := ExpandConstant('{app}\runtime\Scripts\pythonw.exe');
end;

procedure SetInstallerProgressColors;
begin
  SetWindowTheme(WizardForm.ProgressGauge.Handle, '', '');
  SendMessage(WizardForm.ProgressGauge.Handle, $0409, 0, $00E64680);
  SendMessage(WizardForm.ProgressGauge.Handle, $0401, 0, $003B2327);
  WizardForm.ProgressGauge.Refresh;
end;

function NewPageLabel(Parent: TWinControl; const Caption: String; Top: Integer;
  FontSize: Integer; Bold: Boolean; Color: TColor): TNewStaticText;
begin
  Result := TNewStaticText.Create(Parent);
  Result.Parent := Parent;
  Result.Left := ScaleX(0);
  Result.Top := ScaleY(Top);
  Result.Width := Parent.ClientWidth - ScaleX(8);
  Result.AutoSize := True;
  Result.WordWrap := True;
  Result.Caption := Caption;
  Result.Font.Name := 'Segoe UI';
  Result.Font.Size := FontSize;
  Result.Font.Color := Color;
  if Bold then
    Result.Font.Style := [fsBold];
end;

procedure InitializeWizard;
begin
  ExistingPythonExe := DetectCompatiblePython;

  ExtractTemporaryFile('installing-image.png');
  InstallingArtwork := TBitmapImage.Create(WizardForm);
  InstallingArtwork.PngImage.LoadFromFile(ExpandConstant('{tmp}\installing-image.png'));
  InstallingArtwork.Parent := WizardForm.ProgressGauge.Parent;
  InstallingArtwork.Left := (InstallingArtwork.Parent.ClientWidth - ScaleX(377)) div 2;
  InstallingArtwork.Top := ScaleY(78);
  InstallingArtwork.Width := ScaleX(377);
  InstallingArtwork.Height := ScaleY(230);
  InstallingArtwork.Stretch := True;
  InstallingArtwork.Visible := False;

  WizardForm.Font.Name := 'Segoe UI';
  WizardForm.Font.Color := $00FFF2F5;
  WizardForm.StyleElements := [];
  WizardForm.Color := $00271312;
  WizardForm.MainPanel.StyleElements := [];
  WizardForm.MainPanel.Font.Name := 'Segoe UI';
  WizardForm.MainPanel.Font.Color := $00FFF2F5;
  WizardForm.MainPanel.Color := $003B1E23;
  WizardForm.InnerPage.StyleElements := [];
  WizardForm.InnerPage.Color := $00271312;
  WizardForm.DirEdit.Color := $003C3458;
  WizardForm.DirEdit.Font.Name := 'Segoe UI';
  WizardForm.DirEdit.Font.Color := $00FFF2F5;
  WizardForm.PageNameLabel.Font.Name := 'Segoe UI';
  WizardForm.PageNameLabel.Font.Color := $00FFF2F5;
  WizardForm.PageDescriptionLabel.Font.Name := 'Segoe UI';
  WizardForm.PageDescriptionLabel.Font.Color := $00E8C2C8;
  WizardForm.DiskSpaceLabel.Font.Name := 'Segoe UI';
  WizardForm.DiskSpaceLabel.Font.Color := $00F0D2D8;
  WizardForm.ReadyMemo.StyleElements := [];
  WizardForm.ReadyMemo.Color := $003C3458;
  WizardForm.ReadyMemo.Font.Name := 'Segoe UI';
  WizardForm.ReadyMemo.Font.Color := $00FFF2F5;
  WizardForm.WelcomeLabel1.Caption := 'Your iPhone, on your desktop.';
  WizardForm.WelcomeLabel1.Font.Name := 'Segoe UI';
  WizardForm.WelcomeLabel1.Font.Size := 19;
  WizardForm.WelcomeLabel1.Font.Color := $00FFF2F5;
  WizardForm.WelcomeLabel1.Font.Style := [fsBold];
  WizardForm.WelcomeLabel2.Caption :=
    'Install iDevice Modded with its own Python runtime and required packages. No separate Python setup or internet connection is needed for the app dependencies.';
  WizardForm.WelcomeLabel2.Font.Name := 'Segoe UI';
  WizardForm.WelcomeLabel2.Font.Color := $00F0D2D8;
  WizardForm.BackButton.Font.Name := 'Segoe UI';
  WizardForm.NextButton.Font.Name := 'Segoe UI';
  WizardForm.CancelButton.Font.Name := 'Segoe UI';

  OptionsPage := CreateCustomPage(wpSelectDir, 'Personalize your setup',
    'Choose shortcuts and iPhone USB support.');
  OptionsPage.Surface.StyleElements := [];
  OptionsPage.Surface.Color := $00271312;

  NewPageLabel(OptionsPage.Surface, 'A complete, self-contained install', 8, 17,
    True, $00FFF2F5);
  NewPageLabel(OptionsPage.Surface,
    'Setup reuses compatible 64-bit Python 3.13 when it is already installed. Otherwise, it can install Python privately. iDevice Modded packages are installed offline in its own app environment.',
    48, 10, False, $00F0D2D8);

  OptionsCard := TPanel.Create(OptionsPage.Surface);
  OptionsCard.Parent := OptionsPage.Surface;
  OptionsCard.Left := ScaleX(0);
  OptionsCard.Top := ScaleY(135);
  OptionsCard.Width := OptionsPage.Surface.ClientWidth - ScaleX(8);
  OptionsCard.Height := ScaleY(148);
  OptionsCard.BevelOuter := bvNone;
  OptionsCard.StyleElements := [];
  OptionsCard.Color := $00EFEAF9;

  StartMenuShortcutCheck := TNewCheckBox.Create(OptionsPage.Surface);
  StartMenuShortcutCheck.Parent := OptionsCard;
  StartMenuShortcutCheck.Left := ScaleX(8);
  StartMenuShortcutCheck.Top := ScaleY(6);
  StartMenuShortcutCheck.Width := OptionsCard.ClientWidth - ScaleX(16);
  StartMenuShortcutCheck.Caption := 'Add iDevice Modded to the Start Menu';
  StartMenuShortcutCheck.Checked := True;
  StartMenuShortcutCheck.StyleElements := [];
  StartMenuShortcutCheck.Font.Name := 'Segoe UI';
  StartMenuShortcutCheck.Font.Color := $00271312;

  DesktopShortcutCheck := TNewCheckBox.Create(OptionsPage.Surface);
  DesktopShortcutCheck.Parent := OptionsCard;
  DesktopShortcutCheck.Left := ScaleX(8);
  DesktopShortcutCheck.Top := ScaleY(32);
  DesktopShortcutCheck.Width := OptionsCard.ClientWidth - ScaleX(16);
  DesktopShortcutCheck.Caption := 'Create a desktop shortcut';
  DesktopShortcutCheck.Checked := True;
  DesktopShortcutCheck.StyleElements := [];
  DesktopShortcutCheck.Font.Name := 'Segoe UI';
  DesktopShortcutCheck.Font.Color := $00271312;

  InstallPythonCheck := TNewCheckBox.Create(OptionsCard);
  InstallPythonCheck.Parent := OptionsCard;
  InstallPythonCheck.Left := ScaleX(8);
  InstallPythonCheck.Top := ScaleY(58);
  InstallPythonCheck.Width := OptionsCard.ClientWidth - ScaleX(16);
  if ExistingPythonExe <> '' then
  begin
    InstallPythonCheck.Caption := 'Install bundled Python 3.13 anyway';
    InstallPythonCheck.Checked := False;
  end
  else
  begin
    InstallPythonCheck.Caption := 'Install Python 3.13 (required)';
    InstallPythonCheck.Checked := True;
  end;
  InstallPythonCheck.StyleElements := [];
  InstallPythonCheck.Font.Name := 'Segoe UI';
  InstallPythonCheck.Font.Color := $00271312;

  AppleDevicesCheck := TNewCheckBox.Create(OptionsCard);
  AppleDevicesCheck.Parent := OptionsCard;
  AppleDevicesCheck.Left := ScaleX(8);
  AppleDevicesCheck.Top := ScaleY(84);
  AppleDevicesCheck.Width := OptionsCard.ClientWidth - ScaleX(16);
  AppleDevicesCheck.Caption := 'Install Apple Devices from Microsoft Store (recommended)';
  AppleDevicesCheck.Checked := True;
  AppleDevicesCheck.StyleElements := [];
  AppleDevicesCheck.Font.Name := 'Segoe UI';
  AppleDevicesCheck.Font.Color := $00271312;

  if ExistingPythonExe <> '' then
    NewPageLabel(OptionsCard, 'Compatible Python 3.13 detected; setup will reuse it.',
      115, 8, False, $003B3458)
  else
    NewPageLabel(OptionsCard, 'No compatible Python detected; setup will install it.',
      115, 8, False, $003B3458);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  InstallingArtwork.Visible := CurPageID = wpInstalling;
  if CurPageID = wpInstalling then
    SetInstallerProgressColors;
  if CurPageID = wpWelcome then
  begin
    WizardForm.WelcomeLabel1.Font.Color := $00FFF2F5;
    WizardForm.WelcomeLabel2.Font.Color := $00F0D2D8;
  end;
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedHeadingLabel.StyleElements := [];
    WizardForm.FinishedHeadingLabel.Font.Name := 'Segoe UI';
    WizardForm.FinishedHeadingLabel.Font.Color := $00271312;
    WizardForm.FinishedLabel.StyleElements := [];
    WizardForm.FinishedLabel.Font.Name := 'Segoe UI';
    WizardForm.FinishedLabel.Font.Color := $00271312;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = OptionsPage.ID) and not InstallPythonCheck.Checked and
    (ExistingPythonExe = '') then
  begin
    MsgBox('A compatible 64-bit Python 3.13 installation was not found. Select "Install Python 3.13" to continue.',
      mbError, MB_OK);
    Result := False;
  end;
end;

function InstallAppleDevices: Boolean;
var
  ResultCode: Integer;
  PowerShell: String;
  Parameters: String;
begin
  Result := True;
  if WizardSilent or not AppleDevicesCheck.Checked then
    exit;

  PowerShell := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  Parameters := '-NoProfile -NonInteractive -Command "' +
    '$ErrorActionPreference=''SilentlyContinue''; ' +
    'if ((Get-AppxPackage -Name AppleInc.AppleDevices) -or ' +
    '(Get-AppxPackage -Name AppleInc.iTunes) -or ' +
    '(Get-Service -Name ''Apple Mobile Device Service'')) { exit 0 }; ' +
    'if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { exit 127 }; ' +
    'winget install --id 9NP83LWLPZ9K --source msstore --exact --silent ' +
    '--accept-package-agreements --accept-source-agreements; exit $LASTEXITCODE"';
  try
    WizardForm.StatusLabel.Caption := 'Installing Apple Devices support...';
    if not ExecAsOriginalUser(PowerShell, Parameters, '', SW_HIDE,
      ewWaitUntilTerminated, ResultCode) then
      ResultCode := -1;
    if ResultCode <> 0 then
    begin
      MsgBox('iDevice Modded installed successfully, but Apple Devices could not be installed automatically.' +
        Chr(13) + Chr(10) + Chr(13) + Chr(10) +
        'Install it from the Microsoft Store to connect an iPhone over USB:' +
        Chr(13) + Chr(10) + 'https://apps.microsoft.com/detail/9NP83LWLPZ9K',
        mbInformation, MB_OK);
    end;
  except
    MsgBox('iDevice Modded installed successfully, but Apple Devices could not be installed automatically.' +
      Chr(13) + Chr(10) + Chr(13) + Chr(10) + GetExceptionMessage +
      Chr(13) + Chr(10) + Chr(13) + Chr(10) +
      'Install it from the Microsoft Store: https://apps.microsoft.com/detail/9NP83LWLPZ9K',
      mbInformation, MB_OK);
  end;
end;

function CreateDesktopShortcut: Boolean;
begin
  Result := DesktopShortcutCheck.Checked;
end;

function CreateStartMenuShortcuts: Boolean;
begin
  Result := StartMenuShortcutCheck.Checked;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  ScriptPath: String;
begin
  Result := '';
  ScriptPath := ExpandConstant('{app}\installer\stop-processes.ps1');
  if not FileExists(ScriptPath) then
    exit;

  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'),
    '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' +
      ScriptPath + '" -InstallRoot "' + ExpandConstant('{app}') + '"',
    ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) or
    (ResultCode <> 0) then
    Result := 'Could not stop the existing iDesktop processes. Close iDesktop and retry setup.';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  PythonSetup: String;
  PythonArgs: String;
  Bootstrap: String;
  BootstrapArgs: String;
  InstallLog: String;
  PythonLog: String;
  RuntimePython: String;
begin
  if CurStep = ssInstall then
  begin
    InstallingArtwork.Visible := True;
    InstallingArtwork.BringToFront;
    SetInstallerProgressColors;
    exit;
  end;

  if CurStep <> ssPostInstall then
    exit;

  ExtractTemporaryFile('wheelhouse.zip');
  ExtractTemporaryFile('bootstrap.py');
  InstallLog := ExpandConstant('{userappdata}\iDesktop\logs\installer-dependencies.log');
  PythonLog := ExpandConstant('{userappdata}\iDesktop\logs\python-install.log');
  ForceDirectories(ExtractFileDir(PythonLog));
  ResultCode := -1;
  RuntimePython := ExpandConstant('{app}\runtime\python.exe');
  if InstallPythonCheck.Checked then
  begin
    ExtractTemporaryFile('python-installer.exe');
    PythonSetup := ExpandConstant('{tmp}\python-installer.exe');
    PythonArgs := '/quiet InstallAllUsers=1 Include_pip=1 Include_tcltk=1 ' +
      'Include_launcher=0 Include_test=0 Shortcuts=0 PrependPath=0 AppendPath=0 ' +
      'TargetDir="' + ExpandConstant('{app}\runtime') + '" /log "' + PythonLog + '"';
    WizardForm.StatusLabel.Caption := 'Installing the private Python runtime...';
    if not Exec(PythonSetup, PythonArgs, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) or
       (ResultCode <> 0) then
      RaiseException('Python setup failed (exit code ' + IntToStr(ResultCode) +
        '). See ' + PythonLog + ' for details.');
  end
  else
  begin
    WizardForm.StatusLabel.Caption := 'Preparing an iDevice Modded Python environment...';
    if not Exec(ExistingPythonExe, '-m venv "' + ExpandConstant('{app}\runtime') + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode) or (ResultCode <> 0) then
      RaiseException('Could not create iDevice Modded''s private environment using the detected Python interpreter.');
    RuntimePython := ExpandConstant('{app}\runtime\Scripts\python.exe');
  end;

  Bootstrap := ExpandConstant('{tmp}\bootstrap.py');
  BootstrapArgs := '"' + Bootstrap + '" --wheelhouse "' +
    ExpandConstant('{tmp}\wheelhouse.zip') + '" --requirements "' +
    ExpandConstant('{app}\requirements.txt') + '" --log "' + InstallLog + '"';
  WizardForm.StatusLabel.Caption := 'Installing bundled iDevice Modded packages...';
  if not Exec(RuntimePython, BootstrapArgs,
    ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) or
     (ResultCode <> 0) then
    RaiseException('Installing iDevice Modded packages failed (exit code ' +
      IntToStr(ResultCode) + '). See ' + InstallLog + ' for details.');

  InstallAppleDevices;
  DeleteFile(ExpandConstant('{autoprograms}\iDesktop.lnk'));
  DeleteFile(ExpandConstant('{autoprograms}\Uninstall iDesktop.lnk'));
  DeleteFile(ExpandConstant('{autodesktop}\iDesktop.lnk'));
end;
