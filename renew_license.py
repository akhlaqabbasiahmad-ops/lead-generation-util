"""
License Renewal Tool - SERVER-SIDE ONLY
This should run on your server, not on client machines.

Use server_admin_tools.py or the server API for renewals.
"""

import sys
import os
from datetime import datetime, timedelta

# Check if this is running on server
if os.environ.get('RUNNING_ON_SERVER') != 'true':
    print("=" * 60)
    print("WARNING: License renewal must happen on the server!")
    print("=" * 60)
    print("\nUse server_admin_tools.py on your server instead.")
    print("Or use the server API: POST /api/renew_license")
    print("=" * 60)
    sys.exit(1)

# Server-side imports
try:
    import requests
    SERVER_URL = os.environ.get('LICENSE_SERVER_URL', 'http://localhost:5000')
    ADMIN_KEY = os.environ.get('ADMIN_KEY', 'your-admin-secret-key')
except:
    print("Error: Server tools not available")
    sys.exit(1)

def main():
    print("=" * 60)
    print("License Renewal Tool")
    print("=" * 60)
    print()
    
    # Use server API for renewal
    print("Enter customer details:")
    email = input("Customer Email: ").strip()
    
    if not email:
        print("Error: Email is required")
        return
    
    # Get subscription tier
    print("\nSubscription Tiers:")
    print("1. Trial (7 days, limited features)")
    print("2. Basic (30 days, Excel export)")
    print("3. Pro (30 days, all features)")
    print("4. Enterprise (365 days, unlimited)")
    
    tier_choice = input("\nSelect tier (1-4): ").strip()
    
    tier_map = {
        "1": ("trial", 7),
        "2": ("basic", 30),
        "3": ("pro", 30),
        "4": ("enterprise", 365)
    }
    
    if tier_choice not in tier_map:
        print("Error: Invalid tier selection")
        return
    
    tier, default_duration = tier_map[tier_choice]
    
    # Duration
    print(f"\nDefault duration: {default_duration} days")
    duration_input = input("Enter duration in days (press Enter for default): ").strip()
    
    if duration_input:
        try:
            duration = int(duration_input)
        except ValueError:
            print("Invalid duration, using default")
            duration = default_duration
    else:
        duration = default_duration
    
    # Call server API to renew license
    print("\nRequesting license renewal from server...")
    try:
        response = requests.post(
            f"{SERVER_URL}/api/renew_license",
            json={
                "admin_key": ADMIN_KEY,
                "email": email,
                "tier": tier,
                "duration": duration
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            license_key = data["license_key"]
        elif response.status_code == 402:
            print("Error: Payment not confirmed. Mark customer as paid first.")
            return
        else:
            print(f"Error: {response.json()}")
            return
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return
    
    print("\n" + "=" * 60)
    print("NEW LICENSE KEY GENERATED")
    print("=" * 60)
    print(f"Customer Email: {email}")
    print(f"Tier: {tier.upper()}")
    print(f"Duration: {duration} days")
    print(f"Expiry Date: {(datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')}")
    print("\nLicense Key:")
    print("-" * 60)
    print(license_key)
    print("-" * 60)
    print("\n✓ Send this new key to the customer")
    print("✓ Customer needs to activate it in the application")
    print("=" * 60)
    
    # Save to file (optional)
    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"license_{email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(f"License Key for: {email}\n")
            f.write(f"Tier: {tier.upper()}\n")
            f.write(f"Duration: {duration} days\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nLicense Key:\n{license_key}\n")
        print(f"✓ Saved to: {filename}")

if __name__ == "__main__":
    from datetime import timedelta
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

