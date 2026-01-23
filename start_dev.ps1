# PowerShell helper to start the dev server
param(
  [string]$Port = "8001"
)
$ErrorActionPreference = "Stop"

Write-Host "Activating venv..."
. "$PSScriptRoot\env\Scripts\Activate.ps1"

Write-Host "Applying migrations..."
python manage.py migrate

Write-Host "Ensuring admin user (admin / 123)..."
python manage.py ensureadmin

Write-Host "Starting server on 127.0.0.1:$Port ... (keep this window open)"
python manage.py runserver "127.0.0.1:$Port"
