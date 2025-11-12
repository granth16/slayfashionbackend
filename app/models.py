from sqlalchemy import Column, String, DateTime, Boolean, Integer
from datetime import datetime
from .database import Base


class Customer(Base):
    """Customer model - stores phone to Shopify customer mapping with hidden credentials"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    shopify_customer_id = Column(String, unique=True, index=True, nullable=False)
    shopify_email = Column(String, unique=True, nullable=False)  # Hidden email for Shopify
    shopify_password = Column(String, nullable=False)  # Hidden password (hashed)
    
    # Customer info from Shopify
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Customer(phone={self.phone}, shopify_id={self.shopify_customer_id})>"


class OTPVerification(Base):
    """OTP verification model - stores OTP codes for phone verification"""
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    
    # Status
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<OTPVerification(phone={self.phone}, verified={self.is_verified})>"

