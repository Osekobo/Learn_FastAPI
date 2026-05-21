# mpesa_handler.py - Simplified version with comments
import os
import time
import math
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load your secret keys from .env file
load_dotenv()

class MpesaPayment:
    """
    A simple class to handle M-Pesa STK Push payments
    Beginner-friendly with clear explanations
    """
    
    def __init__(self):
        """Setup everything needed to talk to M-Pesa"""
        
        # Get your credentials from .env file
        self.shortcode = os.getenv("SAF_SHORTCODE")
        self.consumer_key = os.getenv("SAF_CONSUMER_KEY")
        self.consumer_secret = os.getenv("SAF_CONSUMER_SECRET")
        self.passkey = os.getenv("SAF_PASS_KEY")
        self.callback_url = os.getenv("CALLBACK_URL")
        
        # M-Pesa API URLs (these are the same for everyone)
        self.token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        self.query_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        
        # Get access token when we start
        self.access_token = None
        self.token_expiry_time = None
        self.get_access_token()
        
        print("✅ M-Pesa handler ready!")
    
    def get_access_token(self):
        """Get permission to talk to M-Pesa API"""
        try:
            # Ask M-Pesa for permission using your keys
            response = requests.get(
                self.token_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
            )
            
            # Extract the token from response
            self.access_token = response.json()['access_token']
            self.token_expiry_time = time.time() + 3500  # Token expires in ~1 hour
            
            # Create headers with the token for future requests
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            print("✅ Got access token successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to get access token: {e}")
            return False
    
    def check_token(self):
        """Make sure our token is still valid, refresh if needed"""
        if self.access_token is None or time.time() >= self.token_expiry_time:
            print("Token expired, getting new one...")
            self.get_access_token()
        return self.access_token is not None
    
    def generate_password(self):
        """Create the special password M-Pesa requires"""
        # Get current timestamp in required format (YYYYMMDDHHMMSS)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Combine shortcode + passkey + timestamp
        password_string = self.shortcode + self.passkey + timestamp
        
        # Convert to base64 as M-Pesa requires
        password_bytes = password_string.encode()
        password_base64 = base64.b64encode(password_bytes).decode("utf-8")
        
        return password_base64, timestamp
    
    def send_payment_request(self, phone_number, amount, account_ref="Payment"):
        """
        Send payment request to customer's phone
        Returns: Response from M-Pesa
        """
        # Check if we have valid token
        if not self.check_token():
            return {"error": "Failed to authenticate with M-Pesa"}
        
        # Generate password and timestamp
        password, timestamp = self.generate_password()
        
        # Prepare the data to send to M-Pesa
        payment_data = {
            "BusinessShortCode": self.shortcode,      # Your business number
            "Password": password,                      # Generated password
            "Timestamp": timestamp,                    # Current timestamp
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(amount)),       # Amount to charge
            "PartyA": phone_number,                    # Customer's phone
            "PartyB": self.shortcode,                  # Your business number
            "PhoneNumber": phone_number,               # Customer's phone again
            "CallBackURL": self.callback_url,          # Where to send result
            "AccountReference": account_ref,           # Your reference
            "TransactionDesc": "Payment for goods",    # Description
        }
        
        # Send the request to M-Pesa
        try:
            response = requests.post(
                self.stk_push_url,
                json=payment_data,
                headers=self.headers,
                timeout=30
            )
            
            result = response.json()
            
            # Print friendly message
            if result.get("ResponseCode") == "0":
                print(f"✅ Payment request sent to {phone_number}")
                print(f"   Checkout ID: {result.get('CheckoutRequestID')}")
            else:
                print(f"❌ Failed: {result.get('ResponseDescription')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error sending payment request: {e}")
            return {"error": str(e)}
    
    def check_payment_status(self, checkout_id):
        """
        Check if customer has completed payment
        checkout_id: The ID you got from send_payment_request()
        """
        if not self.check_token():
            return {"error": "Failed to authenticate with M-Pesa"}
        
        # Generate fresh password and timestamp for query
        password, timestamp = self.generate_password()
        
        # Prepare query data
        query_data = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_id,
        }
        
        # Ask M-Pesa for status
        try:
            response = requests.post(
                self.query_url,
                json=query_data,
                headers=self.headers,
                timeout=30
            )
            
            result = response.json()
            
            # Show friendly status
            result_code = result.get("ResultCode")
            if result_code == "0":
                print("✅ Payment completed successfully!")
            elif result_code == "1037":
                print("⏳ Customer hasn't entered PIN yet")
            elif result_code == "1032":
                print("❌ Request timed out")
            else:
                print(f"Status: {result.get('ResultDesc', 'Unknown')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return {"error": str(e)}


# ============================================
# SIMPLE USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Create payment handler
    mpesa = MpesaPayment()
    
    # Send payment request to customer
    # Phone number must be in format: 254XXXXXXXX (12 digits)
    result = mpesa.send_payment_request(
        phone_number="254714391137",  # Customer's phone number
        amount=10,                     # Amount in KES
        account_ref="Order-123"        # Your reference
    )
    
    # If successful, save this ID to check payment later
    if result.get("ResponseCode") == "0":
        checkout_id = result.get("CheckoutRequestID")
        print(f"\n💡 Save this ID for later: {checkout_id}")
        
        # Wait a few seconds then check status
        print("\nChecking payment status after 5 seconds...")
        time.sleep(5)
        status = mpesa.check_payment_status(checkout_id)
        print(f"Status response: {status}")