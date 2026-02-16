#define MyAppName "KFC Inventory App"
#define MyAppExeName "KFCInventoryApp.exe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "KFC Inventory"
#define MyAppId "{{E11E3F71-EDEF-4CFE-B28F-1D3AECEFFA9F}}"

#ifexist "app/assets/app.ico"
#define MyAppIcon "app/assets/app.ico"
#endif

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\KFCInventoryApp
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=KFCInventoryAppSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
#ifdef MyAppIcon
SetupIconFile={#MyAppIcon}
#endif

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; Flags: unchecked

[Files]
Source: "dist\KFCInventoryApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
