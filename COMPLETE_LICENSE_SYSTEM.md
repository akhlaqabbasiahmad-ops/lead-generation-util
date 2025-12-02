# Complete License System - Server-Side Generation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR SERVER                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │  license_server.py                               │  │
│  │  - Generates ALL license keys                    │  │
│  │  - Verifies payments                             │  │
│  │  - Manages customers                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  server_admin_tools.py                          │  │
│  │  - Mark customers as paid                        │  │
│  │  - Generate licenses                             │  │
│  │  - Renew licenses                                │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
                        │ API Calls
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  CLIENT APP (EXE)                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  license_manager.py                             │  │
│  │  - CANNOT generate licenses                     │  │
│  │  - Only validates licenses                      │  │
│  │  - Checks payment with server                   │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Key Features

✅ **Server generates all licenses** - Client cannot generate  
✅ **Payment verification required** - App won't work without payment  
✅ **Unique keys per customer** - Each license is unique  
✅ **Automatic renewal** - Generate new key when expired  
✅ **Secure** - Secret key on server only

## Setup Instructions

### Step 1: Deploy License Server

1. **Upload to your server:**
   - `license_server.py`
   - `server_admin_tools.py`
   - `requirements_server.txt`

2. **Install dependencies:**
   ```bash
   pip install -r requirements_server.txt
   ```

3. **Configure:**
   ```bash
   export SECRET_KEY="your-secure-random-key-here"
   export ADMIN_KEY="your-admin-secret-key"
   ```

4. **Run server:**
   ```bash
   # Development
   python license_server.py
   
   # Production
   gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
   ```

### Step 2: Configure Client App

In `google_scraper_gui.py`, set your server URL:

```python
SERVER_URL = 'https://your-license-server.com'
```

### Step 3: Update Secret Key

**IMPORTANT:** Client and server must have the SAME secret key:

- **Server** (`license_server.py`): `SECRET_KEY = "your-key"`
- **Client** (`license_manager.py`): `self.secret_key = "your-key"`

## Workflow: New Customer

### 1. Customer Pays

### 2. On Your Server:

```python
from server_admin_tools import process_new_customer

result = process_new_customer(
    email="customer@email.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN123"
)

license_key = result["license_key"]
```

### 3. Send License Key to Customer

### 4. Customer Activates in App

- App validates with your server
- Server checks payment status
- If paid → Activation succeeds
- If not paid → Activation fails

## Workflow: License Renewal

### 1. Customer's License Expires

### 2. Customer Pays Renewal

### 3. On Your Server:

```python
from server_admin_tools import process_renewal

result = process_renewal(
    email="customer@email.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN456"
)

new_license_key = result["license_key"]
```

### 4. Send New License Key to Customer

### 5. Customer Activates New Key

## API Endpoints

### Admin Endpoints (Your Server)

- `POST /api/mark_payment` - Mark customer as paid
- `POST /api/generate_license` - Generate new license
- `POST /api/renew_license` - Renew expired license
- `GET /api/customer_status` - Check customer status

### Client Endpoints (Called by App)

- `POST /api/validate_license` - Validate/activate license
- `POST /api/verify_payment` - Verify payment status

## Security

1. **Never expose ADMIN_KEY** - Keep it secret
2. **Use HTTPS** - Encrypt all communication
3. **Same SECRET_KEY** - Must match on server and client
4. **Environment variables** - Don't hardcode keys
5. **Rate limiting** - Prevent abuse
6. **Authentication** - Protect admin endpoints

## Example: Complete Process

```python
# ============================================
# ON YOUR SERVER
# ============================================

from server_admin_tools import process_new_customer

# Customer paid $99.99, transaction TXN789
result = process_new_customer(
    email="newcustomer@example.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN789"
)

license_key = result["license_key"]

# Send to customer
send_email(
    to="newcustomer@example.com",
    subject="Your License Key",
    body=f"Your license key: {license_key}\n\nActivate it in the application."
)
```

```python
# ============================================
# ON CUSTOMER'S COMPUTER (Client App)
# ============================================

# Customer opens app
# Clicks "License" button
# Pastes license key
# App calls: POST https://your-server.com/api/validate_license
# Server checks payment → Paid ✓
# License activates successfully
```

## Payment Verification

The app **WILL NOT WORK** if:
- ❌ Customer hasn't paid
- ❌ Payment not marked on server
- ❌ Server cannot verify payment

The app **WILL WORK** if:
- ✅ Customer has paid
- ✅ Payment marked on server
- ✅ License key is valid
- ✅ License not expired

## Summary

| Action | Location | Who Can Do It |
|--------|----------|---------------|
| Generate License | Server Only | You (admin) |
| Validate License | Client App | Customer |
| Check Payment | Server | Server (automatic) |
| Renew License | Server Only | You (admin) |

**Result:** Customers cannot use the app without paying and getting a valid license from your server.

