# Get AWS EC2 Public IP Address
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AWS EC2 Public IP Checker" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Checking AWS EC2 Metadata Service..." -ForegroundColor Yellow
try {
    $publicIP = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/meta-data/public-ipv4" -TimeoutSec 3 -ErrorAction Stop).Trim()
    Write-Host "[OK] Found Public IP from EC2 metadata" -ForegroundColor Green
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Your Public IP Address: $publicIP" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access your server at:" -ForegroundColor Yellow
    Write-Host "  http://$publicIP" -ForegroundColor White
    Write-Host ""
    
    # Also get private IP for reference
    try {
        $privateIP = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/meta-data/local-ipv4" -TimeoutSec 3).Trim()
        Write-Host "Private IP: $privateIP" -ForegroundColor Gray
        Write-Host ""
    } catch {
        Write-Host "Could not retrieve private IP" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[INFO] Not on EC2 or metadata service not accessible" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[2/3] Getting public IP from external service..." -ForegroundColor Yellow
    try {
        $publicIP = (Invoke-RestMethod -Uri "http://ifconfig.me/ip" -TimeoutSec 5).Trim()
        Write-Host "[OK] Found Public IP" -ForegroundColor Green
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host "Your Public IP Address: $publicIP" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Access your server at:" -ForegroundColor Yellow
        Write-Host "  http://$publicIP" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "[ERROR] Could not retrieve public IP" -ForegroundColor Red
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "  1. Internet connection" -ForegroundColor White
        Write-Host "  2. AWS Console - EC2 Dashboard" -ForegroundColor White
        Write-Host "  3. Select your instance and check 'Public IPv4 address'" -ForegroundColor White
        pause
        exit 1
    }
}

Write-Host "[3/3] Checking server status..." -ForegroundColor Yellow
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Server is running and accessible locally" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "[WARNING] Server may not be running or not accessible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Access your server at: http://$publicIP" -ForegroundColor White
Write-Host ""
Write-Host "2. If you cannot access:" -ForegroundColor Yellow
Write-Host "   - Verify security group allows port 80 from 0.0.0.0/0" -ForegroundColor White
Write-Host "   - Check if instance has a public IP assigned" -ForegroundColor White
Write-Host "   - Verify the Flask app is running" -ForegroundColor White
Write-Host ""
Write-Host "3. If no public IP shown:" -ForegroundColor Yellow
Write-Host "   - Go to AWS Console - EC2" -ForegroundColor White
Write-Host "   - Select your instance" -ForegroundColor White
Write-Host "   - Allocate Elastic IP if needed" -ForegroundColor White
Write-Host "   - Associate Elastic IP with instance" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
pause

