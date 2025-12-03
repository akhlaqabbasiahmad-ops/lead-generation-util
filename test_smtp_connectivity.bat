@echo off
REM Test SMTP Connectivity on EC2
REM Tests if SMTP ports are reachable

echo ==========================================
echo SMTP Connectivity Test
echo ==========================================
echo.

echo Testing SMTP connectivity...
echo.

echo Testing email-smtp.us-east-1.amazonaws.com
echo ----------------------------------------
powershell -Command "Test-NetConnection -ComputerName email-smtp.us-east-1.amazonaws.com -Port 587 -InformationLevel Quiet"
if %errorLevel% equ 0 (
    echo   Port 587: REACHABLE
) else (
    echo   Port 587: BLOCKED or TIMEOUT
)

powershell -Command "Test-NetConnection -ComputerName email-smtp.us-east-1.amazonaws.com -Port 465 -InformationLevel Quiet"
if %errorLevel% equ 0 (
    echo   Port 465: REACHABLE
) else (
    echo   Port 465: BLOCKED or TIMEOUT
)

powershell -Command "Test-NetConnection -ComputerName email-smtp.us-east-1.amazonaws.com -Port 25 -InformationLevel Quiet"
if %errorLevel% equ 0 (
    echo   Port 25: REACHABLE
) else (
    echo   Port 25: BLOCKED or TIMEOUT
)

echo.
echo ==========================================
echo Diagnosis:
echo.
echo If all ports show BLOCKED or TIMEOUT:
echo   1. AWS Security Group is blocking outbound SMTP
echo   2. Windows Firewall is blocking outbound connections
echo.
echo Solution:
echo   1. Run fix_ec2_smtp.bat as Administrator
echo   2. Configure AWS Security Group (see FIX_EC2_SMTP.md)
echo ==========================================
echo.
pause

