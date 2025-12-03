# Quick Fix: SMTP Connection Blocked on EC2

## Problem
Port 587 (and other SMTP ports) are not reachable from your EC2 instance.

## Root Cause
AWS Security Group is blocking **outbound** SMTP connections by default.

## Solution: Fix AWS Security Group (REQUIRED)

### Step 1: Open AWS Console
1. Go to **AWS Console** → **EC2 Dashboard**
2. Click **Security Groups** (left sidebar)

### Step 2: Find Your Security Group
1. Look for the security group attached to your EC2 instance
2. You can find it by:
   - Going to **Instances** → Select your instance → **Security** tab
   - Or check the **Security groups** column in the instances list

### Step 3: Edit Outbound Rules
1. Click on your security group
2. Click **Outbound rules** tab
3. Click **Edit outbound rules** button

### Step 4: Add SMTP Rules

**IMPORTANT:** You need to add rules for ALL SMTP ports:

#### Rule 1: Port 587 (TLS)
- Click **Add rule**
- Type: **Custom TCP**
- Port range: **587**
- Destination: **0.0.0.0/0**
- Description: **SMTP TLS (AWS SES, Gmail, Outlook)**
- Click **Save rules**

#### Rule 2: Port 465 (SSL)
- Click **Add rule**
- Type: **Custom TCP**
- Port range: **465**
- Destination: **0.0.0.0/0**
- Description: **SMTP SSL (Gmail)**
- Click **Save rules**

#### Rule 3: Port 25 (Plain)
- Click **Add rule**
- Type: **Custom TCP**
- Port range: **25**
- Destination: **0.0.0.0/0**
- Description: **SMTP Plain**
- Click **Save rules**

### Step 5: Verify Rules
After saving, you should see:
- ✅ Port 587 - Custom TCP - 0.0.0.0/0
- ✅ Port 465 - Custom TCP - 0.0.0.0/0
- ✅ Port 25 - Custom TCP - 0.0.0.0/0

### Step 6: Test Again
1. Wait 30-60 seconds for changes to take effect
2. Go back to your application
3. Click "Test Connection" again
4. Should work now! ✅

## Alternative: Allow All Outbound (Quick but Less Secure)

If you want to allow all outbound traffic:

1. In **Outbound rules**, click **Add rule**
2. Type: **All traffic**
3. Protocol: **All**
4. Port range: **All**
5. Destination: **0.0.0.0/0**
6. Description: **Allow all outbound**
7. Click **Save rules**

⚠️ **Note:** This is less secure but will definitely work.

## Also Fix Windows Firewall (On EC2 Instance)

Run this on your EC2 instance (as Administrator):

```cmd
fix_ec2_smtp.bat
```

Or manually:
```cmd
netsh advfirewall firewall add rule name="SMTP Outbound 587" dir=out action=allow protocol=TCP localport=587
netsh advfirewall firewall add rule name="SMTP Outbound 465" dir=out action=allow protocol=TCP localport=465
netsh advfirewall firewall add rule name="SMTP Outbound 25" dir=out action=allow protocol=TCP localport=25
```

## Test Connectivity

Run this script to test if ports are reachable:

```cmd
test_smtp_connectivity.bat
```

## Common Mistakes

❌ **Only adding inbound rules** - SMTP needs **OUTBOUND** rules
❌ **Wrong port** - Make sure you're using 587, 465, or 25
❌ **Wrong destination** - Must be `0.0.0.0/0` (all IPs)
❌ **Not waiting** - Changes take 30-60 seconds to apply

## Still Not Working?

1. **Check Network ACLs** (VPC level)
   - Go to VPC Dashboard → Network ACLs
   - Check outbound rules for your subnet

2. **Try Different Port**
   - Some providers support multiple ports
   - Try 465 (SSL) or 25 (Plain)

3. **Check Instance Firewall**
   - Run `fix_ec2_smtp.bat` as Administrator
   - Verify rules with: `netsh advfirewall firewall show rule name="SMTP Outbound 587"`

4. **Use AWS SES**
   - AWS SES works better on EC2
   - Follow `AWS_SES_SETUP.md` guide

## Summary

**The fix is simple:**
1. AWS Console → EC2 → Security Groups
2. Your Security Group → Outbound Rules → Edit
3. Add rules for ports 587, 465, 25
4. Destination: 0.0.0.0/0
5. Save
6. Wait 1 minute
7. Test again!

That's it! 🎉

