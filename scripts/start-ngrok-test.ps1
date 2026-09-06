# Local Flitt webhook testing via ngrok
# Prerequisites:
#   1. Install ngrok: https://ngrok.com/download
#   2. Sign up (free), then: ngrok config add-authtoken YOUR_TOKEN
#   3. Django running: python manage.py runserver

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot ".env"

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "ngrok not found. Install from https://ngrok.com/download" -ForegroundColor Red
    Write-Host "Then run: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
}

Write-Host "Starting ngrok tunnel to http://127.0.0.1:8000 ..."
$ngrok = Start-Process -FilePath "ngrok" -ArgumentList "http","8000" -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 3

try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels"
    $publicUrl = ($tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1).public_url
    if (-not $publicUrl) {
        throw "Could not read ngrok HTTPS URL. Open http://127.0.0.1:4040"
    }

    Write-Host ""
    Write-Host "Public URL: $publicUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "Add or update in .env:" -ForegroundColor Yellow
    Write-Host "SITE_URL=$publicUrl"
    Write-Host ""
    Write-Host "Then RESTART Django (runserver) and start a NEW checkout from pricing."
    Write-Host "Webhook URL will be: $publicUrl/payments/callback/"
    Write-Host ""
    Write-Host "Press Ctrl+C here when done testing (ngrok keeps running in background, PID $($ngrok.Id))."
    while ($true) { Start-Sleep -Seconds 60 }
}
catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
