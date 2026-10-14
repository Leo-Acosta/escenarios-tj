#ifndef AppGuid
  #define AppGuid "B1724A8D-8B55-4B8E-A8C9-7EF8DCC9B290"
#endif
#ifndef OutputName
  #define OutputName "EscenariosTJ-0.1.0-Setup"
#endif

[Setup]
AppId={{{#AppGuid}}
AppName=Escenarios TJ
AppVersion=0.1.0
AppPublisher=Escenarios TJ
DefaultDirName={localappdata}\Programs\EscenariosTJ
DefaultGroupName=Escenarios TJ
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename={#OutputName}
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
CloseApplications=no
RestartApplications=no
UninstallDisplayIcon={app}\EscenariosTJ.exe
SetupLogging=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked

[Files]
Source: "..\release\EscenariosTJ\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Escenarios TJ"; Filename: "{app}\EscenariosTJ.exe"
Name: "{group}\Guía de uso"; Filename: "{app}\LEEME-WINDOWS.md"
Name: "{userdesktop}\Escenarios TJ"; Filename: "{app}\EscenariosTJ.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EscenariosTJ.exe"; Description: "Abrir Escenarios TJ"; Flags: nowait postinstall skipifsilent unchecked

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  Stream: TFileStream;
  AppPath, DataPath: String;
begin
  Result := '';
  AppPath := Lowercase(AddBackslash(ExpandConstant('{app}')));
  if Length(AppPath) > 80 then begin
    Result := 'Elegí una carpeta de instalación más corta (máximo 80 caracteres). Esto evita errores de rutas largas de Windows con el entorno científico.';
    Exit;
  end;
  DataPath := Lowercase(AddBackslash(ExpandConstant('{localappdata}\EscenariosTJ')));
  if Pos(DataPath, AppPath) = 1 then begin
    Result := 'Elegí una carpeta de programa distinta de la carpeta de datos de Escenarios TJ.';
    Exit;
  end;
  if FileExists(ExpandConstant('{app}\EscenariosTJ.exe')) then begin
    try
      Stream := TFileStream.Create(ExpandConstant('{app}\EscenariosTJ.exe'), fmOpenReadWrite or fmShareExclusive);
      Stream.Free;
    except
      Result := 'Cerrá Escenarios TJ antes de instalar o actualizar. No se cerrará automáticamente.'
    end;
  end;
end;
