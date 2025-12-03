# Check Public IP Address (PowerShell)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Public IP Address Checker" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking your public IP address..." -ForegroundColor Yellow
Write-Host ""

# Try multiple methods
$publicIP = $null

try {
    $publicIP = (Invoke-RestMethod -Uri "http://ifconfig.me/ip" -TimeoutSec 5).Trim()
    Write-Host "[OK] Method 1: ifconfig.me" -ForegroundColor Green
} catch {
    try {
        $publicIP = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5).Trim()
        Write-Host "[OK] Method 2: ipify.org" -ForegroundColor Green
    } catch {
        try {
            $publicIP = (Invoke-RestMethod -Uri "http://icanhazip.com" -TimeoutSec 5).Trim()
            Write-Host "[OK] Method 3: icanhazip.com" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Could not retrieve public IP" -ForegroundColor Red
            Write-Host "Please check your internet connection" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "You can also visit: https://whatismyipaddress.com/" -ForegroundColor Cyan
            pause
            exit 1
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Your Public IP Address: $publicIP" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your server should be accessible at:" -ForegroundColor Yellow
Write-Host "  http://$publicIP" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Make sure:" -ForegroundColor Yellow
Write-Host "  1. Port 80 is open in Windows Firewall" -ForegroundColor White
Write-Host "  2. Security group allows port 80 (if AWS EC2)" -ForegroundColor White
Write-Host "  3. Router port forwarding is configured (if behind NAT)" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
pause

