$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath 'frontend/dist/index.html')) { throw 'Compilá primero frontend: npm run build.' }
python -m PyInstaller --noconfirm --clean --onedir --name EscenariosTJ --distpath release --workpath tmp/packaging --specpath tmp/packaging --paths "$projectRoot" --collect-all reportlab --add-data "$projectRoot/escenarios/r;escenarios/r" --add-data "$projectRoot/frontend/dist;frontend/dist" --add-data "$projectRoot/web;web" "$projectRoot/packaging/windows_entry.py"
if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller.' }
Copy-Item -LiteralPath 'docs/FASE-9-WINDOWS.md' -Destination 'release/EscenariosTJ/LEEME-WINDOWS.md'
python packaging/release_manifest.py release/EscenariosTJ
if ($LASTEXITCODE -ne 0) { throw 'Falló la verificación del paquete.' }
