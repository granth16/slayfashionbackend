"""
Security utilities for password encryption and phone validation
"""
from cryptography.fernet import Fernet
import re
from typing import Optional


class PasswordEncryption:
    """
    Utility for encrypting/decrypting passwords
    
    Usage:
        encryptor = PasswordEncryption(settings.jwt_secret_key)
        encrypted = encryptor.encrypt("my_password")
        decrypted = encryptor.decrypt(encrypted)
    """
    
    def __init__(self, key: str):
        """Initialize with a secret key (use JWT_SECRET_KEY from settings)"""
        # Convert key to valid Fernet key (32 url-safe base64-encoded bytes)
        import hashlib
        import base64
        key_bytes = hashlib.sha256(key.encode()).digest()
        self.key = base64.urlsafe_b64encode(key_bytes)
        self.fernet = Fernet(self.key)
    
    def encrypt(self, plain_text: str) -> str:
        """Encrypt a string"""
        return self.fernet.encrypt(plain_text.encode()).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt a string"""
        return self.fernet.decrypt(encrypted_text.encode()).decode()


def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate phone number format
    Returns: (is_valid, formatted_phone)
    """
    # Remove common formatting
    cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Check if it starts with + and has digits
    if re.match(r'^\+\d{10,15}$', cleaned):
        return True, cleaned
    
    # Try to add country code for Indian numbers
    if re.match(r'^\d{10}$', cleaned):
        return True, f"+91{cleaned}"
    
    return False, None


def sanitize_phone_for_email(phone: str) -> str:
    """
    Convert phone number to email-safe string
    Example: +911234567890 -> customer.911234567890
    """
    return phone.replace("+", "").replace("-", "").replace(" ", "")


def is_strong_password(password: str, min_length: int = 8) -> tuple[bool, str]:
    """
    Check if password is strong enough
    Returns: (is_strong, message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    has_upper = re.search(r'[A-Z]', password) is not None
    has_lower = re.search(r'[a-z]', password) is not None
    has_digit = re.search(r'\d', password) is not None
    has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digits"
    
    return True, "Password is strong"

