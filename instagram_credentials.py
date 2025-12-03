"""
Secure Instagram Credentials Manager
Stores and retrieves Instagram login credentials securely
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography not available. Install with: pip install cryptography")


class InstagramCredentialsManager:
    """Manages Instagram login credentials securely."""
    
    def __init__(self, credentials_file: str = "instagram_credentials.enc"):
        """
        Initialize credentials manager.
        
        Args:
            credentials_file: Path to encrypted credentials file
        """
        self.credentials_file = Path(credentials_file)
        self.key_file = Path("instagram_key.key")
        self._key = None
        
        # Generate or load encryption key
        self._load_or_generate_key()
    
    def _load_or_generate_key(self):
        """Load existing encryption key or generate a new one."""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    self._key = f.read()
            except Exception as e:
                print(f"Error loading key: {e}")
                self._generate_key()
        else:
            self._generate_key()
    
    def _generate_key(self):
        """Generate a new encryption key."""
        if CRYPTO_AVAILABLE:
            self._key = Fernet.generate_key()
            try:
                with open(self.key_file, 'wb') as f:
                    f.write(self._key)
                # Set file permissions (readable only by owner)
                os.chmod(self.key_file, 0o600)
            except Exception as e:
                print(f"Error saving key: {e}")
        else:
            # Fallback: use simple base64 encoding (less secure)
            self._key = base64.urlsafe_b64encode(b'default_key_32_bytes_long!!')
    
    def _get_cipher(self):
        """Get Fernet cipher for encryption/decryption."""
        if CRYPTO_AVAILABLE:
            return Fernet(self._key)
        else:
            # Fallback: simple base64 encoding
            return None
    
    def save_credentials(self, username: str, password: str):
        """
        Save Instagram credentials securely.
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        try:
            credentials = {
                'username': username,
                'password': password
            }
            
            if CRYPTO_AVAILABLE:
                cipher = self._get_cipher()
                encrypted_data = cipher.encrypt(json.dumps(credentials).encode())
                
                with open(self.credentials_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # Fallback: base64 encoding (not secure, but better than plain text)
                encoded = base64.b64encode(json.dumps(credentials).encode())
                with open(self.credentials_file, 'wb') as f:
                    f.write(encoded)
            
            # Set file permissions (readable only by owner)
            os.chmod(self.credentials_file, 0o600)
            print(f"✓ Credentials saved securely to {self.credentials_file}")
            return True
            
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False
    
    def load_credentials(self):
        """
        Load Instagram credentials.
        
        Returns:
            Tuple of (username, password) or (None, None) if not found
        """
        if not self.credentials_file.exists():
            return None, None
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            if CRYPTO_AVAILABLE:
                cipher = self._get_cipher()
                decrypted_data = cipher.decrypt(encrypted_data)
                credentials = json.loads(decrypted_data.decode())
            else:
                # Fallback: base64 decoding
                decoded = base64.b64decode(encrypted_data)
                credentials = json.loads(decoded.decode())
            
            return credentials.get('username'), credentials.get('password')
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None, None
    
    def has_credentials(self):
        """Check if credentials are stored."""
        return self.credentials_file.exists()
    
    def delete_credentials(self):
        """Delete stored credentials."""
        try:
            if self.credentials_file.exists():
                os.remove(self.credentials_file)
                print("✓ Credentials deleted")
            return True
        except Exception as e:
            print(f"Error deleting credentials: {e}")
            return False


if __name__ == "__main__":
    # Test the credentials manager
    manager = InstagramCredentialsManager()
    
    # Example: Save credentials (uncomment to test)
    # manager.save_credentials("your_username", "your_password")
    
    # Load credentials
    username, password = manager.load_credentials()
    if username and password:
        print(f"Loaded credentials for: {username}")
    else:
        print("No credentials found")

