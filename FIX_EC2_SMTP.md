# Fix SMTP Connection Timeout on EC2

## Problem
SMTP connection works on local machine but times out on EC2 server.

## Solution: Configure AWS Security Group

EC2 Security Groups block outbound SMTP connections by default. You need to allow outbound SMTP ports.

### Step 1: Open AWS Console

1. Go to **EC2 Dashboard**
2. Click **Security Groups** (left sidebar)
3. Select your instance's security group

### Step 2: Add Outbound Rules

1. Click **Outbound rules** tab
2. Click **Edit outbound rules**
3. Click **Add rule**

**For Gmail/Outlook (TLS - Port 587):**
- Type: Custom TCP
- Port: 587
- Destination: 0.0.0.0/0
- Description: SMTP TLS (Gmail, Outlook)

**For Gmail (SSL - Port 465):**
- Type: Custom TCP
- Port: 465
- Destination: 0.0.0.0/0
- Description: SMTP SSL (Gmail)

**For Yahoo/Other (Port 25):**
- Type: Custom TCP
- Port: 25
- Destination: 0.0.0.0/0
- Description: SMTP Plain

4. Click **Save rules**

### Step 3: Verify Rules

Your outbound rules should include:
- Port 587 (TLS) - for Gmail, Outlook
- Port 465 (SSL) - for Gmail SSL
- Port 25 (Plain) - for other providers

### Alternative: Allow All Outbound (Less Secure)

If you want to allow all outbound traffic:
- Type: All traffic
- Protocol: All
- Port: All
- Destination: 0.0.0.0/0

⚠️ **Note:** This is less secure but will allow all SMTP connections.

## Common SMTP Ports

| Provider | Port | Type |
|----------|------|------|
| Gmail | 587 | TLS (Recommended) |
| Gmail | 465 | SSL |
| Outlook/Office 365 | 587 | TLS |
| Yahoo | 587 | TLS |
| Yahoo | 465 | SSL |
| Custom SMTP | 25, 587, 465 | Varies |

## Quick Fix Commands

### Check Current Outbound Rules (via AWS CLI)

```bash
aws ec2 describe-security-groups --group-ids YOUR_SECURITY_GROUP_ID --query 'SecurityGroups[0].IpPermissionsEgress'
```

### Add Outbound Rule (via AWS CLI)

```bash
# For port 587 (TLS)
aws ec2 authorize-security-group-egress \
    --group-id YOUR_SECURITY_GROUP_ID \
    --protocol tcp \
    --port 587 \
    --cidr 0.0.0.0/0 \
    --description "SMTP TLS"
```

## Test After Configuration

1. Wait 1-2 minutes for changes to take effect
2. Go to Email Marketing tab
3. Configure SMTP settings
4. Click "Test Connection"
5. Should work now!

## Troubleshooting

### Still Timing Out?

1. **Check Security Group** - Verify outbound rules are saved
2. **Check Network ACLs** - VPC Network ACLs might also block
3. **Try Different Port** - Some providers block port 25, try 587
4. **Check Instance Firewall** - Windows Firewall might block outbound

### Check Windows Firewall (on EC2 instance)

```cmd
# Allow outbound SMTP
netsh advfirewall firewall add rule name="SMTP Outbound 587" dir=out action=allow protocol=TCP localport=587
netsh advfirewall firewall add rule name="SMTP Outbound 465" dir=out action=allow protocol=TCP localport=465
```

## Network ACLs (If Still Not Working)

1. Go to **VPC Dashboard**
2. Click **Network ACLs**
3. Select your subnet's Network ACL
4. Click **Outbound rules** tab
5. Add rules for ports 587, 465, 25 (same as Security Group)

