#!/usr/bin/env python3
"""
Quick setup validation script
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()

def check_env_var(var_name: str) -> tuple[bool, str]:
    """Check if environment variable is set"""
    value = os.getenv(var_name, "")
    is_set = bool(value) and value != f"your_{var_name.lower()}_here" and "change" not in value.lower()
    return is_set, value

def main():
    print("=" * 60)
    print("🔍 SlayFashion Backend Setup Check")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python version
    print("📦 Python Version:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        all_good = False
    print()
    
    # Check required files
    print("📁 Required Files:")
    required_files = [
        "requirements.txt",
        ".env",
        "app/main.py",
        "app/config.py",
        "run.py"
    ]
    for file in required_files:
        if check_file_exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
            all_good = False
    print()
    
    # Check environment variables
    print("🔧 Environment Variables (.env):")
    
    # Load .env file
    if check_file_exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
    
    required_vars = {
        "SHOPIFY_STORE_DOMAIN": "Shopify store domain",
        "SHOPIFY_ADMIN_API_TOKEN": "Shopify Admin API token",
        "SHOPIFY_STOREFRONT_ACCESS_TOKEN": "Shopify Storefront token",
        "TWILIO_ACCOUNT_SID": "Twilio Account SID",
        "TWILIO_AUTH_TOKEN": "Twilio Auth Token",
        "TWILIO_PHONE_NUMBER": "Twilio Phone Number",
    }
    
    warnings = []
    for var, description in required_vars.items():
        is_set, value = check_env_var(var)
        if is_set:
            print(f"   ✅ {var}")
        else:
            print(f"   ⚠️  {var} (not configured - {description})")
            warnings.append(var)
    print()
    
    # Summary
    print("=" * 60)
    if all_good and not warnings:
        print("✅ All checks passed! You're ready to run the backend.")
        print()
        print("Start the server with:")
        print("   python run.py")
    elif warnings and all_good:
        print("⚠️  Setup is mostly complete, but some configuration needed:")
        print()
        for var in warnings:
            print(f"   - Configure {var} in .env file")
        print()
        print("You can still run the backend, but some features won't work:")
        print("   python run.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        all_good = False
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

