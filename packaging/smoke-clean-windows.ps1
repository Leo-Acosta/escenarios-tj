param([Parameter(Mandatory=$true)][string]$Setup, [Parameter(Mandatory=$true)][string]$TestRoot)
$ErrorActionPreference = 'Stop'
$setupPath = (Resolve-Path -LiteralPath $Setup).Path
if (-not $setupPath.EndsWith('-QA-Setup.exe')) { throw 'Usar sólo el instalador QA.' }
$rootPath = [IO.Path]::GetFullPath($TestRoot)
if (Test-Path -LiteralPath $rootPath) { throw 'La carpeta de prueba debe ser nueva.' }
New-Item -ItemType Directory -Path $rootPath | Out-Null
$appPath = Join-Path $rootPath 'programa'
$dataPath = Join-Path $rootPath 'datos-sinteticos'
$installArgs = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/NOICONS','/NOCLOSEAPPLICATIONS',('/DIR="'+$appPath+'"'))
function Install-TestPackage {
    $installation = Start-Process -FilePath $setupPath -ArgumentList $installArgs -WindowStyle Hidden -PassThru -Wait
    if ($installation.ExitCode -ne 0) { throw 'Falló la instalación QA.' }
}
function Verify-TestPackage {
    $manifest = Get-Content -LiteralPath (Join-Path $appPath 'release-manifest.json') -Raw | ConvertFrom-Json
    foreach ($file in $manifest.files.PSObject.Properties) {
        $hash = (Get-FileHash -LiteralPath (Join-Path $appPath $file.Name) -Algorithm SHA256).Hash
        if ($hash.ToLowerInvariant() -ne $file.Value) { throw ('Archivo distinto: ' + $file.Name) }
    }
}
Install-TestPackage
Verify-TestPackage
$listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
$listener.Start()
$testPort = $listener.LocalEndpoint.Port
$listener.Stop()
$baseUrl = 'http://127.0.0.1:'+$testPort
$originalSearchPath = $env:PATH
$env:PATH = ''
$appProcess = $null
try {
    $appProcess = Start-Process -FilePath (Join-Path $appPath 'EscenariosTJ.exe') -ArgumentList @('--no-browser',('--port='+$testPort),('--data-dir="'+$dataPath+'"')) -WindowStyle Hidden -PassThru
    $deadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        try { $status = Invoke-WebRequest -Uri ($baseUrl+'/api/continuity/status') -TimeoutSec 1; break }
        catch { if ($appProcess.HasExited -or [DateTime]::UtcNow -gt $deadline) { throw 'No inició el ejecutable instalado.' }; Start-Sleep -Milliseconds 100 }
    } while ($true)
    if ((Invoke-WebRequest -Uri ($baseUrl+'/app/')).StatusCode -ne 200) { throw 'No respondió React.' }
    $snapshot = Invoke-RestMethod -Uri ($baseUrl+'/api/snapshots') -Method Post -ContentType 'application/json' -Headers @{Origin=$baseUrl} -Body '{"cooperation":0.6,"cost":3}'
    if (-not $snapshot.id) { throw 'No guardó la prueba sintética.' }
    Invoke-WebRequest -Uri ($baseUrl+'/api/report.pdf?q=0.6&cost=3') -OutFile (Join-Path $rootPath 'sintetico.pdf') | Out-Null
    $prefix = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes((Join-Path $rootPath 'sintetico.pdf')),0,4)
    if ($prefix -ne '%PDF') { throw 'No se exportó PDF.' }
} finally {
    if ($null -ne $appProcess -and -not $appProcess.HasExited) { Stop-Process -Id $appProcess.Id; $appProcess.WaitForExit() }
    $env:PATH = $originalSearchPath
}
$databasePath = Join-Path $dataPath 'escenarios.sqlite3'
$dataHash = (Get-FileHash -LiteralPath $databasePath).Hash
Install-TestPackage
Verify-TestPackage
if ((Get-FileHash -LiteralPath $databasePath).Hash -ne $dataHash) { throw 'La reinstalación cambió los datos.' }
$uninstallPath = Join-Path $appPath 'unins000.exe'
if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($uninstallPath)) -ne $appPath) { throw 'Destino de desinstalación inesperado.' }
$uninstall = Start-Process -FilePath $uninstallPath -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -WindowStyle Hidden -PassThru -Wait
if ($uninstall.ExitCode -ne 0 -or (Test-Path -LiteralPath (Join-Path $appPath 'EscenariosTJ.exe'))) { throw 'Falló la desinstalación.' }
if ((Get-FileHash -LiteralPath $databasePath).Hash -ne $dataHash) { throw 'La desinstalación cambió los datos.' }
@{synthetic=$true;runtimePathEmpty=$true;pdfExported=$true;dataPreserved=$true;installerVerified=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $rootPath 'clean-verification.json')
Write-Output 'Instalador verificado en Windows sin herramientas de construcción en PATH.'
