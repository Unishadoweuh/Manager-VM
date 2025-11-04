from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: int
    user_id: int
    amount: Decimal
    type: str
    description: Optional[str]
    balance_after: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list response"""
    transactions: list[TransactionResponse]
    total: int
    total_credits: Decimal
    total_debits: Decimal
