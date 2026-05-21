# main.py - Your FastAPI app
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mpesa_handler import MpesaPayment
import logging

# Setup
app = FastAPI(title="M-Pesa Payment API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create one M-Pesa handler for the whole app
mpesa = MpesaPayment()

# Define what a payment request looks like
class PaymentRequest(BaseModel):
    phone_number: str  # Example: "254714391137"
    amount: float      # Example: 100
    reference: str = "Payment"  # Optional, defaults to "Payment"

# Define what a status check looks like
class StatusCheck(BaseModel):
    checkout_id: str  # The ID you got from payment request

@app.post("/pay")
def request_payment(payment: PaymentRequest):
    """
    Send payment request to customer's phone
    Use this endpoint when customer wants to pay
    """
    # Validate phone number format
    if not payment.phone_number.startswith("254") or len(payment.phone_number) != 12:
        raise HTTPException(
            status_code=400, 
            detail="Phone number must be 12 digits starting with 254"
        )
    
    # Send the payment request
    result = mpesa.send_payment_request(
        phone_number=payment.phone_number,
        amount=payment.amount,
        account_ref=payment.reference
    )
    
    # Check if successful
    if result.get("ResponseCode") == "0":
        return {
            "success": True,
            "message": "Payment request sent to phone",
            "checkout_id": result.get("CheckoutRequestID"),
            "customer_message": result.get("CustomerMessage")
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=result.get("ResponseDescription", "Payment failed")
        )

@app.post("/check-status")
def check_status(status: StatusCheck):
    """
    Check if customer has completed payment
    Use the checkout_id from /pay endpoint
    """
    result = mpesa.check_payment_status(status.checkout_id)
    
    if result.get("ResultCode") == "0":
        return {
            "success": True,
            "status": "completed",
            "message": result.get("ResultDesc", "Payment successful")
        }
    else:
        return {
            "success": False,
            "status": "pending",
            "message": result.get("ResultDesc", "Payment not completed yet")
        }

@app.get("/")
def home():
    return {
        "message": "M-Pesa Payment API is running!",
        "endpoints": {
            "POST /pay": "Send payment request to customer",
            "POST /check-status": "Check payment status"
        }
    }