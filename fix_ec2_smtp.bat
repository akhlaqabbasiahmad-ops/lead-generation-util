@echo off
REM Fix SMTP Outbound Rules on EC2 Windows Instance
REM Run as Administrator

echo ==========================================
echo EC2 SMTP Outbound Configuration
echo ==========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/3] Configuring Windows Firewall for SMTP outbound...
echo.

REM Remove existing rules
netsh advfirewall firewall delete rule name="SMTP Outbound 587" >nul 2>&1
netsh advfirewall firewall delete rule name="SMTP Outbound 465" >nul 2>&1
netsh advfirewall firewall delete rule name="SMTP Outbound 25" >nul 2>&1

REM Add outbound rules for SMTP
echo   Adding rule for port 587 (TLS)...
netsh advfirewall firewall add rule name="SMTP Outbound 587" dir=out action=allow protocol=TCP localport=587

echo   Adding rule for port 465 (SSL)...
netsh advfirewall firewall add rule name="SMTP Outbound 465" dir=out action=allow protocol=TCP localport=465

echo   Adding rule for port 25 (Plain)...
netsh advfirewall firewall add rule name="SMTP Outbound 25" dir=out action=allow protocol=TCP localport=25

echo [OK] Windows Firewall configured
echo.

echo [2/3] Verifying rules...
netsh advfirewall firewall show rule name="SMTP Outbound 587"
netsh advfirewall firewall show rule name="SMTP Outbound 465"
echo.

echo [3/3] IMPORTANT: AWS Security Group Configuration
echo.
echo You MUST also configure AWS Security Group:
echo   1. Go to EC2 Dashboard -^> Security Groups
echo   2. Select your instance's security group
echo   3. Click "Outbound rules" tab
echo   4. Click "Edit outbound rules"
echo   5. Add rules:
echo      - Type: Custom TCP, Port: 587, Destination: 0.0.0.0/0
echo      - Type: Custom TCP, Port: 465, Destination: 0.0.0.0/0
echo      - Type: Custom TCP, Port: 25, Destination: 0.0.0.0/0
echo   6. Save rules
echo.
echo ==========================================
echo.
pause

