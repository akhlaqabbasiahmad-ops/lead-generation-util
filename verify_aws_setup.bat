@echo off
REM Verify AWS EC2 Setup for Public Access
echo ==========================================
echo AWS EC2 Public Access Verification
echo ==========================================
echo.

echo [1/4] Checking Public IP Address...
echo.

REM Try to get public IP from AWS metadata (if on EC2)
echo Trying AWS metadata service...
curl -s http://169.254.169.254/latest/meta-data/public-ipv4 >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] AWS metadata service accessible
    echo.
    echo Your Public IP (from EC2 metadata):
    curl -s http://169.254.169.254/latest/meta-data/public-ipv4
    echo.
    echo.
    set AWS_PUBLIC_IP=1
) else (
    echo [INFO] Not on EC2 or metadata service not accessible
    echo Getting public IP from external service...
    echo.
    curl -s http://ifconfig.me/ip
    if %errorLevel% neq 0 (
        curl -s https://api.ipify.org
    )
    echo.
    echo.
    set AWS_PUBLIC_IP=0
)

echo [2/4] Checking Private IP Address...
ipconfig | findstr /i "IPv4"
echo.

echo [3/4] Checking if server is running on port 80...
netstat -ano | findstr ":80 " | findstr "LISTENING"
if %errorLevel% equ 0 (
    echo [OK] Server is listening on port 80
) else (
    echo [WARNING] Server may not be running on port 80
)
echo.

echo [4/4] Testing local access...
curl -s http://localhost >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Server is accessible locally
) else (
    echo [ERROR] Server is NOT accessible locally
    echo Make sure the Flask app is running
)
echo.

echo ==========================================
echo Summary
echo ==========================================
echo.
echo If you have a public IP above, access your server at:
echo   http://[PUBLIC_IP_SHOWN_ABOVE]
echo.
echo If you see "Not on EC2" or no public IP:
echo   1. Check AWS Console - EC2 Dashboard
echo   2. Select your instance
echo   3. Look for "Public IPv4 address"
echo   4. If it shows "None", you need to:
echo      - Allocate an Elastic IP
echo      - Associate it with your instance
echo.
echo Security Group Check:
echo   - Port 80 should be open (you confirmed this)
echo   - Source should be 0.0.0.0/0 (or your IP)
echo.
echo ==========================================
echo.
pause

