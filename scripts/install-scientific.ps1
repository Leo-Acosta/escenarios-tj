param([string]$Python='python')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$rExecutable=Join-Path $projectRoot '.tools/R/bin/x64/Rscript.exe'
if(-not (Test-Path -LiteralPath $rExecutable)) {
    $installerDirectory=Join-Path $projectRoot '.tools/R-install'
    New-Item -ItemType Directory -Force -Path $installerDirectory | Out-Null
    $installerPath=Join-Path $installerDirectory 'R-4.6.1-win.exe'
    & curl.exe -L --fail --silent --show-error 'https://cran.r-project.org/bin/windows/base/R-4.6.1-win.exe' -o $installerPath
    if($LASTEXITCODE -ne 0){throw 'Falló la descarga oficial de R.'}
    if((Get-FileHash -LiteralPath $installerPath -Algorithm MD5).Hash -ne '7907F3A20EC8EC88CD0DA279024B8E27'){throw 'Huella del instalador incorrecta.'}
    $rTarget=Join-Path $projectRoot '.tools/R'
    $installArguments=@('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/NOICONS',('/DIR="'+$rTarget+'"'))
    $process=Start-Process -FilePath $installerPath -ArgumentList $installArguments -WindowStyle Hidden -Wait -PassThru
    if($process.ExitCode -ne 0){throw 'Falló la instalación de R.'}
}
& $rExecutable --vanilla (Join-Path $PSScriptRoot 'install-r-packages.R') (Join-Path $projectRoot '.tools/R-library')
if($LASTEXITCODE -ne 0){throw 'Falló la verificación de paquetes R.'}
$environmentDirectory=Join-Path $projectRoot '.tools/keras-python'
if(-not (Test-Path -LiteralPath (Join-Path $environmentDirectory 'Scripts/python.exe'))) {
    & $Python -m venv $environmentDirectory
    if($LASTEXITCODE -ne 0){throw 'Se requiere Python 3.11–3.13 para el entorno Keras.'}
}
$kerasPython=Join-Path $environmentDirectory 'Scripts/python.exe'
& $kerasPython -m pip install keras==3.12.0 numpy pandas scipy h5py
if($LASTEXITCODE -ne 0){throw 'Falló la instalación de Keras.'}
& $kerasPython -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
if($LASTEXITCODE -ne 0){throw 'Falló la instalación del backend CPU.'}
Write-Output 'Entorno científico instalado en .tools; reiniciá la aplicación para usarlo.'
