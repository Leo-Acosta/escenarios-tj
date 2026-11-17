param([string]$Compiler = '', [string]$Python = 'python',
    [ValidatePattern('^[A-Za-z0-9._-]+$')][string]$OutputName = 'EscenariosTJ-0.1.0-Setup')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not $Compiler) {
    $candidates = @((Join-Path $projectRoot 'tmp/installer-tools/compiler/ISCC.exe'), 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    $Compiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Compiler) { throw 'Se requiere Inno Setup 6.7.3 o compatible.' }
& $Python packaging/release_manifest.py release/EscenariosTJ --manifest-only
if ($LASTEXITCODE -ne 0) { throw 'Paquete inválido.' }
& $Compiler ("/DOutputName=" + $OutputName) packaging/windows-installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Falló el instalador.' }
$setupFile = Join-Path $projectRoot ('release/' + $OutputName + '.exe')
$setupHash = (Get-FileHash -LiteralPath $setupFile -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -LiteralPath ($setupFile + '.sha256') -Value ($setupHash + '  ' + $OutputName + '.exe') -Encoding ascii
