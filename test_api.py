#!/usr/bin/env python3
"""
Simple test script to verify the API is working
"""
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

async def test_send_otp():
    """Test sending OTP"""
    print("📱 Testing send OTP...")
    test_phone = "+919876543210"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"phone": test_phone}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}\n")
        
        if data.get("success"):
            print(f"✅ OTP sent! Session ID: {data.get('session_id')}")
            print(f"⚠️ Check console for OTP code (if in dev mode)\n")
            return data.get("session_id")
        else:
            print(f"❌ Failed to send OTP: {data.get('message')}\n")
            return None

async def test_verify_otp(session_id: str, otp: str):
    """Test verifying OTP"""
    print("✅ Testing verify OTP...")
    test_phone = "+919876543210"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={
                "phone": test_phone,
                "otp": otp,
                "session_id": session_id
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}\n")
        
        if data.get("success"):
            print(f"✅ Login successful!")
            print(f"Customer: {data.get('customer')}")
            print(f"Access Token: {data.get('access_token')[:50]}...\n")
        else:
            print(f"❌ Failed to verify OTP: {data.get('message')}\n")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 SlayFashion Backend API Test")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    await test_health()
    
    # Test 2: Send OTP
    session_id = await test_send_otp()
    
    if session_id:
        print("=" * 60)
        print("📝 Manual Step Required:")
        print("=" * 60)
        print("1. Check the backend console for the OTP code")
        print("2. Run this command to verify:")
        print(f"   python -c \"")
        print(f"   import asyncio")
        print(f"   from test_api import test_verify_otp")
        print(f"   asyncio.run(test_verify_otp('{session_id}', 'YOUR_OTP_HERE'))")
        print(f"   \"")
        print()
        
        # For demo purposes, try with a dummy OTP
        # (This will fail unless you replace with actual OTP)
        # user_input = input("Enter OTP from console (or press Enter to skip): ")
        # if user_input:
        #     await test_verify_otp(session_id, user_input)

if __name__ == "__main__":
    asyncio.run(main())

