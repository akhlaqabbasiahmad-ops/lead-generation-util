# Client App Setup - License Server Integration

## Overview

The client app **CANNOT generate licenses**. It can only:
- Validate licenses from your server
- Activate licenses on the user's machine
- Check payment status with your server

## Configuration

### Set Server URL

In `google_scraper_gui.py`, update the server URL:

```python
# Find this line (around line 40):
SERVER_URL = os.environ.get('LICENSE_SERVER_URL', 'https://your-license-server.com')

# Change to your actual server URL:
SERVER_URL = 'https://your-license-server.com'  # Your server URL
```

Or set environment variable:
```bash
# Windows
set LICENSE_SERVER_URL=https://your-license-server.com

# Linux/Mac
export LICENSE_SERVER_URL=https://your-license-server.com
```

### Update Secret Key

The client's `license_manager.py` must have the **same SECRET_KEY** as your server:

```python
# In license_manager.py (client side)
self.secret_key = "YOUR_SECRET_KEY"  # Must match server's SECRET_KEY
```

## How It Works

1. **Customer receives license key** (from you, generated on server)
2. **Customer opens app** → Clicks "License" button
3. **App validates with server** → Checks payment status
4. **If paid** → License activates
5. **If not paid** → Activation fails

## Important Notes

- ❌ Client app **CANNOT** generate licenses
- ✅ Client app **CAN** validate licenses
- ✅ All license generation happens on your server
- ✅ Payment verification happens on your server

## Building EXE with Server Integration

The EXE will include the license validation code, but license generation is disabled. Users must get license keys from your server.

