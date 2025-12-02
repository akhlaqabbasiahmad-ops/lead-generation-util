"""
License Key Generator - SERVER-SIDE ONLY
This script should run on your server, not on client machines.

For client-side usage, use the server API instead.
See server_admin_tools.py for server-side license generation.
"""

import sys
import os

# Check if running on server (you can add your own check)
if os.environ.get('RUNNING_ON_SERVER') != 'true':
    print("=" * 60)
    print("WARNING: License generation must happen on the server!")
    print("=" * 60)
    print("\nThis script should only run on your license server.")
    print("For server-side generation, use server_admin_tools.py")
    print("\nClient apps can only validate licenses, not generate them.")
    print("=" * 60)
    sys.exit(1)

# Only import if on server
try:
    from license_server import LicenseGenerator
    SERVER_MODE = True
except ImportError:
    print("Error: license_server.py not found. This must run on the server.")
    sys.exit(1)

def main():
    print("=" * 60)
    print("License Key Generator")
    print("=" * 60)
    print()
    
    # Initialize license generator (SERVER-SIDE ONLY)
    # This should only run on your server
    print("SERVER-SIDE LICENSE GENERATOR")
    print("This should only run on your license server!")
    print()
    
    # Get input
    print("Enter customer details:")
    email = input("Email: ").strip()
    
    if not email:
        print("Error: Email is required")
        return
    
    print("\nSubscription Tiers:")
    print("1. Trial (7 days, limited features)")
    print("2. Basic (30 days, Excel export)")
    print("3. Pro (30 days, all features)")
    print("4. Enterprise (365 days, unlimited)")
    
    tier_choice = input("\nSelect tier (1-4): ").strip()
    
    tier_map = {
        "1": (LicenseManager.TIER_TRIAL, LicenseManager.DURATION_TRIAL),
        "2": (LicenseManager.TIER_BASIC, LicenseManager.DURATION_MONTHLY),
        "3": (LicenseManager.TIER_PRO, LicenseManager.DURATION_MONTHLY),
        "4": (LicenseManager.TIER_ENTERPRISE, LicenseManager.DURATION_YEARLY)
    }
    
    if tier_choice not in tier_map:
        print("Error: Invalid tier selection")
        return
    
    tier, duration = tier_map[tier_choice]
    
    # Custom duration option
    custom_duration = input(f"\nDuration (default: {duration} days, press Enter to use default): ").strip()
    if custom_duration:
        try:
            duration = int(custom_duration)
        except ValueError:
            print("Invalid duration, using default")
    
    # Generate license (SERVER-SIDE)
    print("\nGenerating license key...")
    license_key = LicenseGenerator.generate_license_key(email, tier, duration)
    
    print("\n" + "=" * 60)
    print("LICENSE KEY GENERATED")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Tier: {tier.upper()}")
    print(f"Duration: {duration} days")
    print("\nLicense Key:")
    print("-" * 60)
    print(license_key)
    print("-" * 60)
    print("\nSend this key to the customer for activation.")
    print("=" * 60)
    
    # Save to file option
    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == 'y':
        from datetime import datetime
        filename = f"license_{email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(f"License Key for: {email}\n")
            f.write(f"Tier: {tier.upper()}\n")
            f.write(f"Duration: {duration} days\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nLicense Key:\n{license_key}\n")
        print(f"✓ Saved to: {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

