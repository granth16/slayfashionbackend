from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class SendOTPRequest(BaseModel):
    """Request to send OTP to phone number"""
    phone: str = Field(..., description="Phone number with country code (e.g., +911234567890)")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Remove spaces and dashes
        v = v.replace(" ", "").replace("-", "")
        # Check if it starts with + and has digits
        if not re.match(r'^\+\d{10,15}$', v):
            raise ValueError('Phone must be in format +[country_code][number] (e.g., +911234567890)')
        return v


class SendOTPResponse(BaseModel):
    """Response after sending OTP"""
    success: bool
    message: str
    session_id: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP"""
    phone: str = Field(..., description="Phone number with country code")
    otp: str = Field(..., description="6-digit OTP code")
    session_id: str = Field(..., description="Session ID from send OTP request")
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not re.match(r'^\d{4,6}$', v):
            raise ValueError('OTP must be 4-6 digits')
        return v


class CustomerData(BaseModel):
    """Customer information"""
    id: str
    phone: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    shopify_customer_id: str


class VerifyOTPResponse(BaseModel):
    """Response after OTP verification"""
    success: bool
    message: str
    customer: Optional[CustomerData] = None
    access_token: Optional[str] = None  # Shopify customer access token
    token_expires_at: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response with customer access token"""
    success: bool
    customer: CustomerData
    access_token: str  # Shopify Storefront API customer access token
    expires_at: str


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    detail: Optional[str] = None

