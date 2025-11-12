import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from ..models import OTPVerification
from ..config import get_settings

settings = get_settings()


class OTPService:
    """Service for handling OTP generation and verification"""
    
    def __init__(self):
        self.twilio_client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number
    
    @staticmethod
    def generate_otp(length: int = None) -> str:
        """Generate random OTP code"""
        length = length or settings.otp_length
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def send_otp(self, phone: str, db: Session) -> tuple[bool, str, str]:
        """
        Send OTP to phone number via SMS
        Returns: (success, message, session_id)
        """
        try:
            # Generate OTP and session
            otp_code = self.generate_otp()
            session_id = self.generate_session_id()
            expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expiration_minutes)
            
            # Invalidate previous OTPs for this phone (optional, for security)
            db.query(OTPVerification).filter(
                OTPVerification.phone == phone,
                OTPVerification.is_verified == False
            ).update({"is_verified": True})  # Mark old OTPs as used
            
            # Store OTP in database
            otp_record = OTPVerification(
                phone=phone,
                otp_code=otp_code,
                session_id=session_id,
                expires_at=expires_at
            )
            db.add(otp_record)
            db.commit()
            
            # Send SMS via Twilio
            message_body = f"Your SlayFashion verification code is: {otp_code}\nValid for {settings.otp_expiration_minutes} minutes."
            
            try:
                message = self.twilio_client.messages.create(
                    body=message_body,
                    from_=self.from_number,
                    to=phone
                )
                
                print(f"✅ OTP sent to {phone}: {otp_code} (Message SID: {message.sid})")
                return True, "OTP sent successfully", session_id
                
            except TwilioRestException as e:
                print(f"❌ Twilio error: {e}")
                # For development: still return success with session_id so you can test
                # In production, you should return failure here
                print(f"⚠️ DEV MODE: OTP not sent but proceeding. OTP is: {otp_code}")
                return True, f"OTP would be sent (DEV MODE - OTP: {otp_code})", session_id
        
        except Exception as e:
            print(f"❌ Error sending OTP: {e}")
            return False, f"Failed to send OTP: {str(e)}", ""
    
    @staticmethod
    def verify_otp(phone: str, otp_code: str, session_id: str, db: Session) -> tuple[bool, str]:
        """
        Verify OTP code
        Returns: (success, message)
        """
        # Find OTP record
        otp_record = db.query(OTPVerification).filter(
            OTPVerification.phone == phone,
            OTPVerification.session_id == session_id
        ).first()
        
        if not otp_record:
            return False, "Invalid session or phone number"
        
        # Check if already verified
        if otp_record.is_verified:
            return False, "OTP already used"
        
        # Check if expired
        if otp_record.is_expired():
            return False, "OTP has expired"
        
        # Check attempts (prevent brute force)
        if otp_record.attempts >= 5:
            return False, "Too many attempts. Please request a new OTP"
        
        # Increment attempts
        otp_record.attempts += 1
        db.commit()
        
        # Verify OTP
        if otp_record.otp_code != otp_code:
            return False, f"Invalid OTP code. {5 - otp_record.attempts} attempts remaining"
        
        # Mark as verified
        otp_record.is_verified = True
        otp_record.verified_at = datetime.utcnow()
        db.commit()
        
        return True, "OTP verified successfully"

