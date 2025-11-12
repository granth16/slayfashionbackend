#!/usr/bin/env python3
"""
End-to-end test of the full backend flow:
1. Send OTP (simulated - prints to console in dev mode)
2. Verify OTP
3. Create customer with REST API
4. Get access token via bridge method
"""
import os
import sys
import time

# Set environment variables from actual .env file or environment
# IMPORTANT: Never hardcode tokens in code!
import sys

# Load from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Check required variables are set
required_vars = ['SHOPIFY_ADMIN_API_TOKEN', 'SHOPIFY_STOREFRONT_ACCESS_TOKEN']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print("❌ ERROR: Missing required environment variables:")
    for var in missing:
        print(f"   - {var}")
    print()
    print("Set them in .env file or pass as environment variables:")
    print("   export SHOPIFY_ADMIN_API_TOKEN=your_token")
    print("   export SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_token")
    sys.exit(1)

# Set defaults for optional vars
os.environ.setdefault('SHOPIFY_STORE_DOMAIN', 'f3lifestyle.myshopify.com')
os.environ.setdefault('SHOPIFY_API_VERSION', '2024-10')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test_slayfashion.db')
os.environ.setdefault('TWILIO_ACCOUNT_SID', 'test')
os.environ.setdefault('TWILIO_AUTH_TOKEN', 'test')
os.environ.setdefault('TWILIO_PHONE_NUMBER', '+1234567890')
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key')

import asyncio
from app.database import init_db, SessionLocal
from app.services.otp_service import OTPService
from app.services.shopify_service import ShopifyService
from app.models import Customer, OTPVerification

print("=" * 70)
print("🧪 Full Backend Test - OTP Login with Shopify Bridge Method")
print("=" * 70)
print()

# Initialize database
print("📦 Initializing test database...")
init_db()
db = SessionLocal()
print("✅ Database initialized")
print()

# Test phone number
test_phone = f"+91999{int(time.time()) % 1000000:06d}"
print(f"📱 Test Phone: {test_phone}")
print()

# STEP 1: Send OTP
print("STEP 1: Send OTP")
print("-" * 70)
otp_service = OTPService()
success, message, session_id = otp_service.send_otp(test_phone, db)

if not success:
    print(f"❌ FAILED: {message}")
    sys.exit(1)

print(f"✅ OTP sent!")
print(f"   Session ID: {session_id}")
print(f"   Message: {message}")
print()

# Get the OTP from database (in dev mode)
otp_record = db.query(OTPVerification).filter(
    OTPVerification.session_id == session_id
).first()
test_otp = otp_record.otp_code
print(f"🔍 DEV MODE - OTP Code: {test_otp}")
print()

# STEP 2: Verify OTP
print("STEP 2: Verify OTP")
print("-" * 70)
otp_valid, otp_message = otp_service.verify_otp(test_phone, test_otp, session_id, db)

if not otp_valid:
    print(f"❌ FAILED: {otp_message}")
    sys.exit(1)

print(f"✅ OTP verified!")
print(f"   Message: {otp_message}")
print()

# STEP 3: Create customer and get access token (Bridge Method)
print("STEP 3: Find/Create Customer & Get Access Token (Bridge Method)")
print("-" * 70)

async def test_bridge_method():
    shopify_service = ShopifyService()
    
    try:
        customer_record, access_token, expires_at = await shopify_service.find_or_create_customer(
            test_phone, db
        )
        
        print("✅ Bridge Method Successful!")
        print()
        print("📋 Customer Record in Our Database:")
        print(f"   ID: {customer_record.id}")
        print(f"   Phone: {customer_record.phone}")
        print(f"   Shopify Customer ID: {customer_record.shopify_customer_id}")
        print(f"   Hidden Email: {customer_record.shopify_email}")
        print(f"   Hidden Password: {customer_record.shopify_password}")
        print()
        print("🎫 Shopify Customer Access Token:")
        print(f"   Token: {access_token[:50]}...")
        print(f"   Expires: {expires_at}")
        print()
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_bridge_method())

if not result:
    sys.exit(1)

# SUMMARY
print("=" * 70)
print("🎉 FULL BACKEND TEST PASSED!")
print("=" * 70)
print()
print("What happened:")
print("1. ✅ OTP sent to phone (dev mode - printed to console)")
print("2. ✅ OTP verified successfully")
print("3. ✅ Customer created in Shopify using REST Admin API")
print("4. ✅ Hidden email/password stored in our database")
print("5. ✅ Access token obtained via Storefront API (bridge method)")
print()
print("🌉 Bridge Method Flow:")
print("   Phone/OTP → REST Admin API (create with password)")
print("   → Store credentials in DB → Storefront API (login)")
print("   → Customer Access Token → User logged in!")
print()
print("This is exactly how GoKwik/KwikPass work! ✅")
print()

# Cleanup
db.close()
print("✅ Test completed successfully!")

