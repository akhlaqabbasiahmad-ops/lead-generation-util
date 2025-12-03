# Google Business Scraper - PowerShell Start Script
# Run this script as Administrator to start the server on port 80

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Google Business Scraper - Server Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if port 80 is in use
$port80 = Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue
if ($port80) {
    Write-Host "[WARNING] Port 80 is already in use" -ForegroundColor Yellow
    Write-Host "You may need to stop IIS or another web server" -ForegroundColor Yellow
    Write-Host ""
    $port80 | Format-Table -AutoSize
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host "Starting server on port 80..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be accessible at:" -ForegroundColor Cyan
Write-Host "  - http://localhost" -ForegroundColor White
Write-Host "  - http://$($env:COMPUTERNAME)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Start the application
python app.py

