$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting Deye Inverter Monitor " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[!] Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    }
}

if (-not (Test-Path "venv")) {
    Write-Host "[*] Creating venv..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "[*] Activating venv..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "[*] Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Server running at http://localhost:8000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
