from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    CustomerData,
    ErrorResponse
)
from ..services import OTPService, ShopifyService
from ..utils.rate_limiter import otp_rate_limiter, verify_rate_limiter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP to customer's phone number
    
    This endpoint:
    1. Generates a 6-digit OTP code
    2. Sends it via SMS (Twilio)
    3. Returns a session ID for verification
    """
    # Rate limiting - prevent OTP spam
    allowed, message = otp_rate_limiter.is_allowed(request.phone)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    otp_service = OTPService()
    
    success, message, session_id = otp_service.send_otp(request.phone, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return SendOTPResponse(
        success=True,
        message=message,
        session_id=session_id
    )


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and login customer using the "bridge method"
    
    This endpoint:
    1. Verifies the OTP code
    2. Finds or creates customer in Shopify using Admin API
    3. Stores phone → customer_id → hidden email/password mapping in database
    4. Uses Storefront API with hidden credentials to get customer access token
    5. Returns the access token for Shopify login
    
    This is the same approach used by GoKwik/KwikPass for OTP-based Shopify login
    """
    # Rate limiting - prevent brute force OTP attempts
    allowed, message = verify_rate_limiter.is_allowed(request.phone)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    otp_service = OTPService()
    shopify_service = ShopifyService()
    
    # Step 1: Verify OTP
    otp_valid, otp_message = otp_service.verify_otp(
        request.phone,
        request.otp,
        request.session_id,
        db
    )
    
    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=otp_message
        )
    
    try:
        # Step 2-5: Find/create customer and get access token (Bridge Method)
        customer_record, access_token, expires_at = await shopify_service.find_or_create_customer(
            request.phone,
            db
        )
        
        # Prepare customer data
        customer_data = CustomerData(
            id=str(customer_record.id),
            phone=customer_record.phone,
            email=customer_record.shopify_email,
            first_name=customer_record.first_name,
            last_name=customer_record.last_name,
            shopify_customer_id=customer_record.shopify_customer_id
        )
        
        return VerifyOTPResponse(
            success=True,
            message="Login successful",
            customer=customer_data,
            access_token=access_token,
            token_expires_at=expires_at
        )
    
    except Exception as e:
        print(f"❌ Error in verify_otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate customer: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SlayFashion Auth API",
        "version": "1.0.0"
    }

