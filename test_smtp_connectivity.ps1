# Test SMTP Connectivity on EC2
# This script tests if SMTP ports are reachable

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SMTP Connectivity Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Test ports
$ports = @(587, 465, 25)
$servers = @(
    "email-smtp.us-east-1.amazonaws.com",
    "smtp.gmail.com",
    "smtp.office365.com"
)

Write-Host "Testing SMTP connectivity..." -ForegroundColor Yellow
Write-Host ""

foreach ($server in $servers) {
    Write-Host "Testing $server" -ForegroundColor Cyan
    Write-Host ("-" * 50) -ForegroundColor Gray
    
    foreach ($port in $ports) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connect = $tcpClient.BeginConnect($server, $port, $null, $null)
            $wait = $connect.AsyncWaitHandle.WaitOne(5000, $false)
            
            if ($wait) {
                $tcpClient.EndConnect($connect)
                Write-Host "  Port $port : " -NoNewline
                Write-Host "✓ REACHABLE" -ForegroundColor Green
                $tcpClient.Close()
            } else {
                Write-Host "  Port $port : " -NoNewline
                Write-Host "✗ TIMEOUT" -ForegroundColor Red
                $tcpClient.Close()
            }
        } catch {
            Write-Host "  Port $port : " -NoNewline
            Write-Host "✗ BLOCKED" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Diagnosis:" -ForegroundColor Yellow
Write-Host ""
Write-Host "If all ports show TIMEOUT or BLOCKED:" -ForegroundColor White
Write-Host "  1. AWS Security Group is blocking outbound SMTP" -ForegroundColor Yellow
Write-Host "  2. Windows Firewall is blocking outbound connections" -ForegroundColor Yellow
Write-Host ""
Write-Host "Solution:" -ForegroundColor White
Write-Host "  1. Run fix_ec2_smtp.bat as Administrator" -ForegroundColor Green
Write-Host "  2. Configure AWS Security Group (see FIX_EC2_SMTP.md)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
pause

