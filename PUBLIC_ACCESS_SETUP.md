# Making Your Server Publicly Accessible

## Current Situation

Your server is running on **private IP: 172.31.40.145**
- ✅ Accessible on local network
- ❌ NOT accessible from internet (private IP)

## Why It's Not Public

The IP `172.31.40.145` is a **private IP address** (AWS VPC range):
- Only accessible within your network/VPC
- Cannot be reached from the internet
- Need a **public IP** to make it accessible worldwide

---

## Solution: Get Public IP Address

### If You're on AWS EC2 (Security Group Already Configured ✅):

#### Step 1: Get Your Public IP

**Quick Method - Run Script:**
```cmd
# Windows Command Prompt
verify_aws_setup.bat

# Or PowerShell
.\get_aws_public_ip.ps1
```

**Manual Method:**
```powershell
# PowerShell
Invoke-RestMethod http://169.254.169.254/latest/meta-data/public-ipv4
```

**Or check in AWS Console:**
1. Go to EC2 Dashboard
2. Select your instance
3. Look for "Public IPv4 address" in the instance details

#### Step 2: Verify Security Group (You've Already Done This ✅)
1. Go to EC2 → Security Groups
2. Select your instance's security group
3. Verify inbound rule exists:
   - Type: HTTP
   - Port: 80
   - Source: 0.0.0.0/0 (or your specific IP)
4. If missing, add the rule and save

#### Step 3: Check/Allocate Public IP

**If your instance shows "Public IPv4 address: None":**

1. **Option A: Enable Auto-assign Public IP**
   - EC2 → Instances → Select instance
   - Actions → Networking → Modify instance IP address settings
   - Enable "Auto-assign public IPv4 address"
   - Save

2. **Option B: Allocate Elastic IP (Recommended for Production)**
   - EC2 → Elastic IPs → Allocate Elastic IP
   - Click "Allocate"
   - Select the Elastic IP → Actions → Associate Elastic IP address
   - Choose your instance
   - Associate
   - This gives you a permanent public IP that won't change

### If You're on a Regular Windows Server:

#### Step 1: Find Your Public IP
Visit: https://whatismyipaddress.com/
Or run:
```cmd
curl ifconfig.me
```

#### Step 2: Configure Router Port Forwarding
1. Access your router admin panel (usually 192.168.1.1)
2. Go to Port Forwarding / Virtual Server
3. Add rule:
   - External Port: 80
   - Internal IP: 172.31.40.145
   - Internal Port: 80
   - Protocol: TCP
4. Save and restart router

#### Step 3: Configure Windows Firewall
```cmd
# Allow port 80 inbound (run as Administrator)
netsh advfirewall firewall add rule name="Google Scraper HTTP" dir=in action=allow protocol=TCP localport=80
```

---

## Quick Check Commands

### Check Your Public IP:
```cmd
# Windows PowerShell
Invoke-RestMethod http://ifconfig.me/ip

# Or visit in browser
https://whatismyipaddress.com/
```

### Check If Port 80 is Open:
Visit: https://www.yougetsignal.com/tools/open-ports/
- Enter your public IP
- Port: 80
- Click "Check"

### Test Public Access:
```cmd
# From another computer/phone
# Replace YOUR_PUBLIC_IP with your actual public IP
curl http://YOUR_PUBLIC_IP
```

---

## Security Considerations

⚠️ **IMPORTANT**: Making your server public exposes it to the internet!

### Recommended Security Measures:

1. **Add Authentication** (if not already)
2. **Use HTTPS** (SSL certificate)
3. **Restrict Access** (if possible, limit to specific IPs)
4. **Keep Software Updated**
5. **Monitor Logs** for suspicious activity

---

## Alternative: Use a Domain Name

Instead of using IP address, you can use a domain:

1. **Buy a domain** (e.g., from Namecheap, GoDaddy)
2. **Point DNS** to your public IP:
   ```
   A Record: @ → YOUR_PUBLIC_IP
   ```
3. **Access via**: `http://yourdomain.com`

---

## Troubleshooting

### Can't Access from Internet

1. **Check Public IP**: Make sure you're using the public IP, not private
2. **Check Security Group/Firewall**: Port 80 must be open
3. **Check Router**: Port forwarding must be configured
4. **Check ISP**: Some ISPs block port 80 (try port 8080 instead)

### Port 80 Blocked by ISP

Use a different port:
```cmd
# Set environment variable
set FLASK_PORT=8080

# Run server
python app.py
```

Then access: `http://YOUR_PUBLIC_IP:8080`

---

## Summary

To make your server publicly accessible:

1. ✅ Get your **public IP address**
2. ✅ Configure **security group/firewall** (allow port 80)
3. ✅ Configure **router port forwarding** (if behind NAT)
4. ✅ Access via: `http://YOUR_PUBLIC_IP`

Your server is already configured correctly (`host='0.0.0.0'`), you just need to:
- Get the public IP
- Open port 80 in firewall/security group
- Access using the public IP instead of private IP

