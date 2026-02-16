$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Error "PyInstaller not found. Install it in your venv: pip install pyinstaller"
}

$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $iscc) {
    Write-Error "Inno Setup (ISCC) not found in PATH. Install Inno Setup and add ISCC to PATH."
}

# Build the app (one-folder) with required data files
$pyiArgs = @(
    "--noconsole",
    "--name", "KFCInventoryApp",
    "--add-data", "app/assets;app/assets",
    "app/main.py"
)

$iconPath = "app/assets/app.ico"
if (Test-Path $iconPath) {
    $pyiArgs = @("--icon", $iconPath) + $pyiArgs
}

pyinstaller @pyiArgs

# Build the installer
iscc installer\KFCInventoryApp.iss
