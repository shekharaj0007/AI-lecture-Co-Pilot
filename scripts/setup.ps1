$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Lecture Copilot — local setup" -ForegroundColor Cyan

# Backend
Write-Host "`n==> Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "$Root\backend"
python -m pip install -r requirements.txt

# Frontend
Write-Host "`n==> Installing Node dependencies..." -ForegroundColor Yellow
Set-Location "$Root\frontend"
npm install

Write-Host "`n==> Setup complete!" -ForegroundColor Green
Write-Host "Run:  .\scripts\start.ps1" -ForegroundColor Cyan
