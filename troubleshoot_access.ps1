# Troubleshoot Public Access Issues
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Troubleshooting Public Access" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Server Status
Write-Host "[1/5] Checking if server is running..." -ForegroundColor Yellow
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Server is running and accessible locally" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "[ERROR] Server is NOT running or not accessible locally" -ForegroundColor Red
    Write-Host "   Make sure Flask app is running: python app.py" -ForegroundColor Yellow
}

Write-Host ""

# Check 2: Port 80 Listening
Write-Host "[2/5] Checking if port 80 is listening..." -ForegroundColor Yellow
$port80 = Get-NetTCPConnection -LocalPort 80 -State Listen -ErrorAction SilentlyContinue
if ($port80) {
    Write-Host "[OK] Port 80 is listening" -ForegroundColor Green
    $port80 | Format-Table -AutoSize
} else {
    Write-Host "[ERROR] Port 80 is NOT listening" -ForegroundColor Red
    Write-Host "   Make sure Flask app is running on port 80" -ForegroundColor Yellow
}

Write-Host ""

# Check 3: Windows Firewall
Write-Host "[3/5] Checking Windows Firewall rules..." -ForegroundColor Yellow
$firewallRules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*80*" -or $_.DisplayName -like "*HTTP*" -or $_.DisplayName -like "*Google*" } | Select-Object DisplayName, Enabled, Direction, Action
if ($firewallRules) {
    Write-Host "[INFO] Found firewall rules:" -ForegroundColor Yellow
    $firewallRules | Format-Table -AutoSize
    
    $allowRule = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Google*" -or ($_.LocalPort -eq 80 -and $_.Direction -eq "Inbound" -and $_.Action -eq "Allow") }
    if ($allowRule) {
        Write-Host "[OK] Firewall rule exists for port 80" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] No specific allow rule found for port 80" -ForegroundColor Yellow
        Write-Host "   Run fix_firewall.bat as Administrator" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] No firewall rules found for port 80" -ForegroundColor Yellow
    Write-Host "   Run fix_firewall.bat as Administrator" -ForegroundColor Yellow
}

Write-Host ""

# Check 4: Public IP
Write-Host "[4/5] Getting public IP address..." -ForegroundColor Yellow
try {
    $publicIP = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/meta-data/public-ipv4" -TimeoutSec 3).Trim()
    Write-Host "[OK] Public IP: $publicIP" -ForegroundColor Green
} catch {
    try {
        $publicIP = (Invoke-RestMethod -Uri "http://ifconfig.me/ip" -TimeoutSec 5).Trim()
        Write-Host "[OK] Public IP: $publicIP" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not retrieve public IP" -ForegroundColor Yellow
        $publicIP = "16.16.249.160"  # From your screenshot
        Write-Host "[INFO] Using IP from screenshot: $publicIP" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check 5: Network Interface
Write-Host "[5/5] Checking network interfaces..." -ForegroundColor Yellow
$interfaces = Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" -and $_.IPAddress -notlike "127.*" } | Select-Object IPAddress, InterfaceAlias
if ($interfaces) {
    Write-Host "[INFO] Network interfaces:" -ForegroundColor Yellow
    $interfaces | Format-Table -AutoSize
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Diagnosis Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $serverRunning) {
    Write-Host "[CRITICAL] Server is not running!" -ForegroundColor Red
    Write-Host "   Solution: Start Flask app with: python app.py" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run fix_firewall.bat as Administrator" -ForegroundColor White
Write-Host "2. Verify AWS Security Group allows port 80 from 0.0.0.0/0" -ForegroundColor White
Write-Host "3. Check AWS VPC Network ACLs (should allow port 80)" -ForegroundColor White
Write-Host "4. Test access: http://$publicIP" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
pause

