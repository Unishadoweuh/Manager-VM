from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings


router = APIRouter(prefix="/payments")


@router.post("/webhook")
async def payment_webhook():
    """Payment webhook (Stripe/PayPal)"""
    
    if not settings.ENABLE_PAYMENTS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is currently disabled"
        )
    
    # TODO: Implement Stripe/PayPal webhook handling
    return {"message": "Webhook received"}


@router.post("/create-intent")
async def create_payment_intent():
    """Create payment intent"""
    
    if not settings.ENABLE_PAYMENTS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is currently disabled"
        )
    
    # TODO: Implement Stripe payment intent creation
    return {"client_secret": "placeholder"}
