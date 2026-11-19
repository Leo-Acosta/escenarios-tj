param([string]$Python = 'python', [switch]$IncludeScientific, [switch]$SkipArchive)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath 'frontend/dist/index.html')) { throw 'Compilá primero frontend: npm run build.' }
& $Python -m PyInstaller --noconfirm --clean --onedir --name EscenariosTJ --distpath release --workpath tmp/packaging --specpath tmp/packaging --paths "$projectRoot" --collect-all reportlab --add-data "$projectRoot/escenarios/scientific_runtime.py;escenarios" --add-data "$projectRoot/escenarios/r;escenarios/r" --add-data "$projectRoot/frontend/dist;frontend/dist" --add-data "$projectRoot/web;web" "$projectRoot/packaging/windows_entry.py"
if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller.' }
Copy-Item -LiteralPath 'docs/FASE-9-WINDOWS.md' -Destination 'release/EscenariosTJ/LEEME-WINDOWS.md'
Copy-Item -LiteralPath 'docs/FASE-12-ESTUDIO-VISUAL.md' -Destination 'release/EscenariosTJ/GUIA-ESTUDIO-VISUAL.md'
if ($IncludeScientific) {
    & $Python packaging/bundle-scientific.py release/EscenariosTJ
    if ($LASTEXITCODE -ne 0) { throw 'Falló el empaquetado científico.' }
    Copy-Item -LiteralPath 'docs/CIERRE-CIENTIFICO-WINDOWS.md' -Destination 'release/EscenariosTJ/GUIA-CIENTIFICA.md'
}
if ($SkipArchive) {
    & $Python packaging/release_manifest.py release/EscenariosTJ --manifest-only
} else {
    & $Python packaging/release_manifest.py release/EscenariosTJ
}
if ($LASTEXITCODE -ne 0) { throw 'Falló la verificación del paquete.' }
