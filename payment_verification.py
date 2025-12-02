"""
Payment Verification System
Checks if customer has paid before allowing license activation/usage
"""

import json
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime

class PaymentVerifier:
    """Verifies customer payment status"""
    
    def __init__(self, api_url: str = None):
        """
        Initialize payment verifier
        
        Args:
            api_url: URL of payment verification API
        """
        self.api_url = api_url or "https://your-payment-server.com/api/verify"  # Change this
        self.timeout = 10  # seconds
    
    def verify_payment(self, email: str, license_key: str = None) -> Tuple[bool, str, Dict]:
        """
        Verify if customer has paid
        
        Args:
            email: Customer email
            license_key: Optional license key
            
        Returns:
            (is_paid, message, payment_data)
        """
        try:
            payload = {
                "email": email,
                "license_key": license_key,
                "action": "verify_payment"
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                is_paid = data.get("paid", False)
                message = data.get("message", "Payment verified" if is_paid else "Payment not confirmed")
                payment_data = data.get("payment_data", {})
                
                return is_paid, message, payment_data
            else:
                return False, f"Payment verification failed: {response.status_code}", {}
                
        except requests.exceptions.RequestException as e:
            # If offline, allow but log warning
            return True, "Offline mode - payment check unavailable", {}
        except Exception as e:
            return False, f"Payment verification error: {str(e)}", {}
    
    def check_payment_status(self, email: str) -> Dict:
        """
        Get detailed payment status
        
        Returns:
            {
                "paid": bool,
                "payment_date": str,
                "amount": float,
                "method": str,
                "transaction_id": str,
                "status": str
            }
        """
        try:
            response = requests.get(
                f"{self.api_url}/status",
                params={"email": email},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"paid": False, "status": "unknown"}
                
        except:
            return {"paid": False, "status": "offline"}


class LocalPaymentTracker:
    """Local payment tracking (for offline or simple systems)"""
    
    def __init__(self, payment_file: str = "payments.json"):
        """
        Initialize local payment tracker
        
        Args:
            payment_file: File to store payment records
        """
        self.payment_file = payment_file
        self.payments = self.load_payments()
    
    def load_payments(self) -> Dict:
        """Load payment records"""
        try:
            with open(self.payment_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_payments(self):
        """Save payment records"""
        with open(self.payment_file, 'w') as f:
            json.dump(self.payments, f, indent=2)
    
    def mark_as_paid(self, email: str, amount: float = None, transaction_id: str = None):
        """Mark customer as paid"""
        if email not in self.payments:
            self.payments[email] = {}
        
        self.payments[email]["paid"] = True
        self.payments[email]["payment_date"] = datetime.now().isoformat()
        if amount:
            self.payments[email]["amount"] = amount
        if transaction_id:
            self.payments[email]["transaction_id"] = transaction_id
        
        self.save_payments()
    
    def mark_as_unpaid(self, email: str):
        """Mark customer as unpaid"""
        if email not in self.payments:
            self.payments[email] = {}
        
        self.payments[email]["paid"] = False
        self.save_payments()
    
    def is_paid(self, email: str) -> bool:
        """Check if customer has paid"""
        if email not in self.payments:
            return False
        
        return self.payments[email].get("paid", False)
    
    def get_payment_info(self, email: str) -> Dict:
        """Get payment information"""
        return self.payments.get(email, {"paid": False})

