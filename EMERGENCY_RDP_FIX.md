# Emergency RDP Access Fix

## If You Can't Access via RDP

### Option 1: Use AWS Systems Manager Session Manager (No RDP Needed)

1. **AWS Console → EC2 → Instances**
2. **Select your instance**
3. **Click "Connect"**
4. **Choose "Session Manager" tab**
5. **Click "Connect"**
6. This opens a browser-based terminal (no RDP needed)

### Option 2: Fix via AWS Console (If You Have Access)

1. **AWS Console → EC2 → Instances**
2. **Select your instance**
3. **Actions → Security → Modify instance attributes**
4. **Check "Enable" for RDP**

### Option 3: Fix Security Group (Most Likely Issue)

1. **AWS Console → EC2 → Security Groups**
2. **Select your instance's security group**
3. **Inbound Rules → Edit**
4. **Add Rule:**
   - Type: RDP
   - Port: 3389
   - Source: Your IP address (or 0.0.0.0/0 for testing)
5. **Save**

### Option 4: Run Script via AWS Systems Manager

If you can access via Systems Manager:

1. Connect via Session Manager (Option 1)
2. Download the fix script:
   ```cmd
   # In the browser terminal
   curl -o fix_rdp_access.bat https://your-script-url
   ```
3. Run it:
   ```cmd
   fix_rdp_access.bat
   ```

---

## What Likely Happened

The firewall rule you added might have:
- Overridden existing rules
- Changed firewall profile settings
- Blocked RDP accidentally

**The fix script will:**
- Re-enable RDP in Windows
- Add RDP firewall rule (port 3389)
- Keep HTTP rule (port 80)
- Ensure both work together

---

## Quick Commands (If You Have Terminal Access)

### Via AWS Systems Manager Session Manager:

```cmd
# Enable RDP
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f

# Add RDP firewall rule
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=3389

# Verify
netsh advfirewall firewall show rule name="Remote Desktop"
```

---

## After Fixing

1. **Wait 30-60 seconds** for changes to take effect
2. **Try RDP again**
3. **Verify both RDP and HTTP work:**
   - RDP: Connect via Remote Desktop
   - HTTP: Access http://16.16.249.160

---

## Prevention

The `restore_all_access.bat` script ensures both RDP and HTTP work together without conflicts.

