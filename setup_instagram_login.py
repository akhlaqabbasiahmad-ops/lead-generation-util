"""
Setup Instagram Login Credentials
Run this script to securely store your Instagram credentials
"""

from instagram_credentials import InstagramCredentialsManager
import getpass

def setup_credentials():
    """Interactive setup for Instagram credentials."""
    print("=" * 60)
    print("Instagram Credentials Setup")
    print("=" * 60)
    print("\nThis will securely store your Instagram login credentials.")
    print("Your credentials will be encrypted and stored locally.\n")
    
    manager = InstagramCredentialsManager()
    
    # Check if credentials already exist
    if manager.has_credentials():
        username, _ = manager.load_credentials()
        print(f"⚠ Existing credentials found for: {username}")
        response = input("\nDo you want to update them? (y/n): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Get username
    username = input("Enter your Instagram username: ").strip()
    if not username:
        print("Username cannot be empty. Setup cancelled.")
        return
    
    # Get password (hidden input)
    password = getpass.getpass("Enter your Instagram password: ").strip()
    if not password:
        print("Password cannot be empty. Setup cancelled.")
        return
    
    # Confirm password
    password_confirm = getpass.getpass("Confirm password: ").strip()
    if password != password_confirm:
        print("Passwords do not match. Setup cancelled.")
        return
    
    # Save credentials
    if manager.save_credentials(username, password):
        print("\n✓ Credentials saved successfully!")
        print("You can now use Instagram login features in the influencer discovery tool.")
    else:
        print("\n✗ Failed to save credentials. Please try again.")

if __name__ == "__main__":
    try:
        setup_credentials()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")

