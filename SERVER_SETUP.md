# License Server Setup Guide

## Overview

License generation happens **ONLY on your server**. The client app can only validate and activate licenses - it cannot generate them.

## Server Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Your Server    │         │  Client App      │         │  Customer    │
│  (license_server│◄────────┤  (validates only)│◄────────┤  (uses app) │
│   .py)          │         │                  │         │              │
└─────────────────┘         └──────────────────┘         └──────────────┘
      │
      │ Generates licenses
      │ Verifies payments
      │ Manages customers
      ▼
┌─────────────────┐
│  Database/File  │
│  (customers,    │
│   payments)     │
└─────────────────┘
```

## Step 1: Deploy License Server

### Install Dependencies

```bash
pip install flask flask-cors
```

### Configure Server

1. **Set Secret Key** (in `license_server.py`):
   ```python
   SECRET_KEY = os.environ.get('LICENSE_SECRET_KEY', 'YOUR_SECURE_RANDOM_KEY_HERE')
   ```

2. **Set Admin Key**:
   ```bash
   export ADMIN_KEY="your-secure-admin-key"
   export LICENSE_SECRET_KEY="your-secure-secret-key"
   ```

3. **Deploy Server**:
   ```bash
   # Development
   python license_server.py
   
   # Production (using Gunicorn)
   gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
   ```

## Step 2: Update Client App

### Configure Client to Use Server

In `license_manager.py` initialization (or in your GUI), set the server URL:

```python
# In google_scraper_gui.py or wherever you initialize LicenseManager
license_manager = LicenseManager(
    api_url="https://your-server.com",  # Your license server URL
    require_payment=True  # Require payment verification
)
```

## Step 3: Workflow

### When Customer Pays:

1. **Mark Payment on Server**:
   ```python
   # On your server, run:
   from server_admin_tools import mark_customer_paid, generate_license_for_customer
   
   # Mark as paid
   mark_customer_paid("customer@email.com", amount=99.99, transaction_id="TXN123")
   
   # Generate license
   result = generate_license_for_customer("customer@email.com", tier="pro", duration=30)
   license_key = result["license_key"]
   ```

2. **Send License Key to Customer**:
   - Email the license key
   - Or provide via your customer portal

3. **Customer Activates**:
   - Customer opens app
   - Clicks "License" button
   - Pastes license key
   - App validates with your server
   - Server checks payment status
   - If paid → activation succeeds
   - If not paid → activation fails

### When Customer's License Expires:

1. **Customer Pays Renewal**

2. **On Your Server**:
   ```python
   from server_admin_tools import process_renewal
   
   # Mark payment and generate new license
   result = process_renewal(
       email="customer@email.com",
       tier="pro",
       duration=30,
       amount=99.99,
       transaction_id="TXN456"
   )
   ```

3. **Send New License Key to Customer**

4. **Customer Activates New Key**

## API Endpoints

### For Your Server (Admin):

- `POST /api/mark_payment` - Mark customer as paid
- `POST /api/generate_license` - Generate new license
- `POST /api/renew_license` - Renew expired license
- `GET /api/customer_status` - Check customer status

### For Client App:

- `POST /api/validate_license` - Validate/activate license
- `POST /api/verify_payment` - Verify payment status

## Security

1. **Never expose ADMIN_KEY to clients**
2. **Use HTTPS in production**
3. **Change SECRET_KEY** - Must match between server and client
4. **Use environment variables** for sensitive keys
5. **Implement rate limiting** on API endpoints
6. **Use authentication** for admin endpoints

## Example: Complete Customer Onboarding

```python
# On your server
from server_admin_tools import process_new_customer

# Customer pays $99.99
# Transaction ID: TXN789012

# Generate license
result = process_new_customer(
    email="newcustomer@example.com",
    tier="pro",
    duration=30,
    amount=99.99,
    transaction_id="TXN789012"
)

# Get license key
license_key = result["license_key"]

# Send to customer via email
send_email(
    to="newcustomer@example.com",
    subject="Your License Key",
    body=f"Your license key: {license_key}"
)
```

## Example: License Renewal

```python
# On your server
from server_admin_tools import process_renewal

# Customer pays renewal
result = process_renewal(
    email="customer@example.com",
    tier="pro",  # Can upgrade/downgrade
    duration=30,
    amount=99.99,
    transaction_id="TXN345678"
)

# Send new license key
send_email(
    to="customer@example.com",
    subject="License Renewed",
    body=f"Your renewed license key: {result['license_key']}"
)
```

## Database (Production)

Replace in-memory dictionaries with a real database:

```python
# Use SQLite, PostgreSQL, MySQL, etc.
import sqlite3

def get_customer(email):
    conn = sqlite3.connect('licenses.db')
    # ... database queries
```

## Testing

### Test Server Locally:

```bash
# Terminal 1: Start server
python license_server.py

# Terminal 2: Test admin functions
python -c "from server_admin_tools import process_new_customer; process_new_customer('test@example.com', 'pro', 30, 99.99, 'TEST123')"
```

## Summary

✅ **Server generates all licenses**  
✅ **Client only validates/activates**  
✅ **Payment verification required**  
✅ **No license generation in client app**  
✅ **Secure and controlled**

