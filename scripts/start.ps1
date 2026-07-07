$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

# Refresh PATH so ffmpeg (winget) is visible
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "==> Starting backend (port 8010)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
`$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
cd '$Root\backend'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
"@

Start-Sleep -Seconds 2

Write-Host "==> Starting frontend (port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\frontend'; npm run dev"

Write-Host ""
Write-Host "Open http://localhost:3000" -ForegroundColor Green
Write-Host "API health: http://localhost:8010/health" -ForegroundColor Green
