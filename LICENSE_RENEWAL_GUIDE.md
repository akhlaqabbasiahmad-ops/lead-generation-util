# License Renewal Guide

## When a Customer's License Expires

When a customer's license expires, you need to generate a **new license key** for them. The old license cannot be extended - you must issue a new one.

## Quick Renewal Process

### Method 1: Use the Renewal Tool (Recommended)

```bash
python renew_license.py
```

This will:
1. Ask for customer email
2. Let you select subscription tier
3. Set duration
4. Generate a new license key
5. Optionally save to a file

### Method 2: Use Python Directly

```python
from license_manager import LicenseManager
from datetime import datetime, timedelta

# Initialize
lm = LicenseManager()

# Generate new license
email = "customer@example.com"
tier = "pro"  # or "basic", "enterprise"
duration = 30  # days

new_license_key = lm.generate_license_key(email, tier, duration)

print(f"New License Key for {email}:")
print(new_license_key)
print(f"\nExpires: {(datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')}")
```

## Step-by-Step Renewal Process

### 1. Customer Reports Expiration

Customer sees: "License has expired" in the application

### 2. Verify Customer Identity

- Check their email matches your records
- Verify payment (if applicable)
- Confirm subscription tier

### 3. Generate New License

**Option A: Using renewal script**
```bash
python renew_license.py
# Follow prompts
```

**Option B: Using Python**
```python
from license_manager import LicenseManager

lm = LicenseManager()
new_key = lm.generate_license_key(
    email="customer@example.com",
    tier="pro",
    duration_days=30
)
```

### 4. Send New License Key

Send the new license key to the customer via:
- Email
- Your customer portal
- Support ticket system

### 5. Customer Activates

Customer:
1. Opens the application
2. Clicks "License" button
3. Pastes the new license key
4. Clicks "Activate License"

**Note:** The old license will be replaced with the new one.

## Renewal Best Practices

### 1. Keep Records

Track license renewals:
- Customer email
- Previous expiry date
- New expiry date
- Subscription tier
- License key (store securely)

### 2. Proactive Renewal

Send renewal reminders 7 days before expiry:
```
Subject: Your License Expires Soon

Hi [Customer],

Your license expires on [Date]. 
To renew, please contact support or visit [your website].

[Generate and send new license key]
```

### 3. Different Renewal Options

**Same Tier Renewal:**
```python
# Customer had Pro, renewing Pro
new_key = lm.generate_license_key("customer@email.com", "pro", 30)
```

**Upgrade Renewal:**
```python
# Customer had Basic, upgrading to Pro
new_key = lm.generate_license_key("customer@email.com", "pro", 30)
```

**Extended Duration:**
```python
# Renewing for longer period
new_key = lm.generate_license_key("customer@email.com", "pro", 90)  # 3 months
```

## Example Renewal Workflow

### Scenario: Customer's Pro License Expired

1. **Customer contacts you:**
   - "My license expired, I need a renewal"

2. **You verify:**
   - Check their email: customer@example.com
   - Previous license: Pro tier, expired yesterday
   - Payment: Confirmed

3. **Generate renewal:**
   ```bash
   python renew_license.py
   # Enter: customer@example.com
   # Select: 3 (Pro)
   # Duration: 30 days
   ```

4. **Send license key:**
   ```
   Subject: Your License Renewal

   Hi [Customer],
   
   Here's your new license key:
   
   [LICENSE_KEY_HERE]
   
   Please activate it in the application.
   ```

5. **Customer activates:**
   - Opens app → License → Paste key → Activate

## Bulk Renewal

If you need to renew multiple licenses:

```python
from license_manager import LicenseManager
from datetime import timedelta

lm = LicenseManager()

customers = [
    {"email": "customer1@example.com", "tier": "pro", "days": 30},
    {"email": "customer2@example.com", "tier": "basic", "days": 30},
    {"email": "customer3@example.com", "tier": "enterprise", "days": 365},
]

for customer in customers:
    key = lm.generate_license_key(
        customer["email"],
        customer["tier"],
        customer["days"]
    )
    print(f"{customer['email']}: {key}\n")
```

## Important Notes

1. **Old License Cannot Be Extended**
   - You must generate a NEW license key
   - The old key is replaced when customer activates new one

2. **Machine Binding**
   - New license can be activated on the same machine
   - Or customer can activate on a different machine (new machine binding)

3. **License Key Format**
   - Long base64-encoded string
   - Copy the entire key (no line breaks)
   - Customer pastes it exactly as provided

4. **Expiry Date**
   - Starts from generation date
   - Not from old license expiry
   - Example: If old license expired Dec 1, new license starts Dec 1 (not Dec 2)

## Troubleshooting Renewal

**Customer: "I can't activate the new license"**
- Check if they copied the entire key
- Verify the key is valid (test it yourself)
- Ensure they're using the latest version of the app

**Customer: "License still shows expired"**
- They need to activate the NEW key
- Old license won't work - must activate new one
- Check if they pasted the key correctly

**Customer: "Can I use on different computer?"**
- Yes, new license can be activated on any machine
- Old license was machine-bound, new one can be different

## Automation Ideas

### Create a Renewal Database

```python
# renewal_tracker.py
import json
from datetime import datetime

renewals = {
    "customer@example.com": {
        "last_renewal": "2024-12-01",
        "tier": "pro",
        "duration": 30,
        "next_expiry": "2024-12-31"
    }
}

# Save to file
with open("renewals.json", "w") as f:
    json.dump(renewals, f, indent=2)
```

### Automated Renewal Script

```python
# auto_renew.py
from license_manager import LicenseManager
from datetime import datetime, timedelta

def auto_renew_customer(email, tier, days):
    lm = LicenseManager()
    new_key = lm.generate_license_key(email, tier, days)
    
    # Send email (implement your email sending)
    send_renewal_email(email, new_key)
    
    return new_key
```

## Summary

**To renew an expired license:**
1. Run `python renew_license.py`
2. Enter customer email
3. Select tier and duration
4. Send the generated key to customer
5. Customer activates in the application

**That's it!** The new license replaces the old one.

