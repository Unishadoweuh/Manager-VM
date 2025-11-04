from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_async_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.user import UserResponse, UserCreditsResponse
from app.schemas.transaction import TransactionResponse


router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.get("/credits", response_model=UserCreditsResponse)
async def get_user_credits(
    current_user: User = Depends(get_current_active_user)
):
    """Get user credit balance"""
    return UserCreditsResponse(balance=current_user.balance)


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user transaction history"""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    transactions = result.scalars().all()
    return transactions
