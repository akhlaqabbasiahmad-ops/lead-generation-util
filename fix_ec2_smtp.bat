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

echo [3/3] CRITICAL: AWS Security Group Configuration
echo.
echo ==========================================
echo YOU MUST CONFIGURE AWS SECURITY GROUP!
echo ==========================================
echo.
echo This is the MAIN issue - Windows Firewall alone won't fix it.
echo.
echo Steps:
echo   1. Go to AWS Console -^> EC2 Dashboard
echo   2. Click "Security Groups" (left sidebar)
echo   3. Find your instance's security group
echo      (Check Instances -^> Your Instance -^> Security tab)
echo   4. Click on the security group
echo   5. Click "Outbound rules" tab
echo   6. Click "Edit outbound rules"
echo   7. Click "Add rule" THREE times:
echo.
echo      Rule 1:
echo        Type: Custom TCP
echo        Port: 587
echo        Destination: 0.0.0.0/0
echo        Description: SMTP TLS
echo.
echo      Rule 2:
echo        Type: Custom TCP
echo        Port: 465
echo        Destination: 0.0.0.0/0
echo        Description: SMTP SSL
echo.
echo      Rule 3:
echo        Type: Custom TCP
echo        Port: 25
echo        Destination: 0.0.0.0/0
echo        Description: SMTP Plain
echo.
echo   8. Click "Save rules"
echo   9. Wait 30-60 seconds
echo  10. Test connection in your app
echo.
echo ==========================================
echo See QUICK_FIX_SMTP.md for detailed guide
echo ==========================================
echo.
pause

