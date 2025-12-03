# Fix SMTP Outbound Rules on EC2 Windows Instance
# Run this on the EC2 instance to configure Windows Firewall

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EC2 SMTP Outbound Configuration" -ForegroundColor Cyan
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

Write-Host "[1/3] Configuring Windows Firewall for SMTP outbound..." -ForegroundColor Yellow

# Remove existing rules
netsh advfirewall firewall delete rule name="SMTP Outbound 587" >$null 2>&1
netsh advfirewall firewall delete rule name="SMTP Outbound 465" >$null 2>&1
netsh advfirewall firewall delete rule name="SMTP Outbound 25" >$null 2>&1

# Add outbound rules for SMTP
Write-Host "  Adding rule for port 587 (TLS)..." -ForegroundColor Gray
netsh advfirewall firewall add rule name="SMTP Outbound 587" dir=out action=allow protocol=TCP localport=587

Write-Host "  Adding rule for port 465 (SSL)..." -ForegroundColor Gray
netsh advfirewall firewall add rule name="SMTP Outbound 465" dir=out action=allow protocol=TCP localport=465

Write-Host "  Adding rule for port 25 (Plain)..." -ForegroundColor Gray
netsh advfirewall firewall add rule name="SMTP Outbound 25" dir=out action=allow protocol=TCP localport=25

Write-Host "[OK] Windows Firewall configured" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Verifying rules..." -ForegroundColor Yellow
netsh advfirewall firewall show rule name="SMTP Outbound 587"
netsh advfirewall firewall show rule name="SMTP Outbound 465"
Write-Host ""

Write-Host "[3/3] Important: AWS Security Group Configuration" -ForegroundColor Yellow
Write-Host ""
Write-Host "You MUST also configure AWS Security Group:" -ForegroundColor Cyan
Write-Host "  1. Go to EC2 Dashboard -> Security Groups" -ForegroundColor White
Write-Host "  2. Select your instance's security group" -ForegroundColor White
Write-Host "  3. Click 'Outbound rules' tab" -ForegroundColor White
Write-Host "  4. Click 'Edit outbound rules'" -ForegroundColor White
Write-Host "  5. Add rules:" -ForegroundColor White
Write-Host "     - Type: Custom TCP, Port: 587, Destination: 0.0.0.0/0" -ForegroundColor White
Write-Host "     - Type: Custom TCP, Port: 465, Destination: 0.0.0.0/0" -ForegroundColor White
Write-Host "     - Type: Custom TCP, Port: 25, Destination: 0.0.0.0/0" -ForegroundColor White
Write-Host "  6. Save rules" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
pause

