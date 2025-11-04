from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TransactionType(str, enum.Enum):
    """Transaction types"""
    CREDIT = "credit"  # Adding credits (payment, admin credit)
    DEBIT = "debit"  # Removing credits (VM usage)
    ADMIN_ADJUST = "admin_adjust"  # Manual admin adjustment
    REFUND = "refund"  # Refund
    PAYMENT = "payment"  # Payment received


class Transaction(Base):
    """Transaction model for credit history"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Numeric(10, 2), nullable=False)  # Positive = credit, Negative = debit
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    
    # Related entities
    vm_id = Column(Integer, ForeignKey("user_vms.id", ondelete="SET NULL"), nullable=True)
    
    # Description & metadata
    description = Column(String(500), nullable=True)
    transaction_metadata = Column(JSON, nullable=True)  # Additional data (payment gateway info, etc.)
    
    # Payment gateway reference
    payment_id = Column(String(255), nullable=True, index=True)  # Stripe charge ID, PayPal transaction ID
    payment_method = Column(String(50), nullable=True)  # stripe, paypal, manual
    
    # Admin who performed manual adjustment
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Balance after transaction
    balance_after = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])
    vm = relationship("VM")
    admin = relationship("User", foreign_keys=[admin_id])
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount}, user_id={self.user_id})>"
