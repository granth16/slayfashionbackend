#!/usr/bin/env python3
"""Simple test - create customer with password and verify it works"""
import requests
import json
import time
import os
import sys

# Try to read from .env file, fall back to environment variables
env_vars = {}
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
except FileNotFoundError:
    print("⚠️  .env file not found, using environment variables")
    print("   You can set them like:")
    print("   export SHOPIFY_STORE_DOMAIN=your-store.myshopify.com")
    print("   export SHOPIFY_ADMIN_API_TOKEN=shpat_xxx")
    print("   export SHOPIFY_STOREFRONT_ACCESS_TOKEN=xxx")
    print()

STORE = env_vars.get('SHOPIFY_STORE_DOMAIN') or os.getenv('SHOPIFY_STORE_DOMAIN') or 'f3lifestyle.myshopify.com'
ADMIN_TOKEN = env_vars.get('SHOPIFY_ADMIN_API_TOKEN') or os.getenv('SHOPIFY_ADMIN_API_TOKEN')
STOREFRONT_TOKEN = env_vars.get('SHOPIFY_STOREFRONT_ACCESS_TOKEN') or os.getenv('SHOPIFY_STOREFRONT_ACCESS_TOKEN') or 'aef92cf6067f10d1f18f3bd6cbee4012'
API_VERSION = env_vars.get('SHOPIFY_API_VERSION') or os.getenv('SHOPIFY_API_VERSION') or '2024-10'

if not ADMIN_TOKEN:
    print("❌ ERROR: SHOPIFY_ADMIN_API_TOKEN not set!")
    print()
    print("Please provide it as:")
    print("1. In .env file: SHOPIFY_ADMIN_API_TOKEN=shpat_xxx")
    print("2. Or as environment variable: export SHOPIFY_ADMIN_API_TOKEN=shpat_xxx")
    print("3. Or as command argument: python3 simple_test.py shpat_xxx")
    print()
    if len(sys.argv) > 1:
        ADMIN_TOKEN = sys.argv[1]
        print(f"✅ Using token from command line argument")
    else:
        sys.exit(1)

print("=" * 60)
print("Testing Shopify Admin API - Create Customer with Password")
print("=" * 60)
print(f"Store: {STORE}")
print()

# Test data
test_email = f"test{int(time.time())}@slayfashion.test"
test_password = "SecurePassword123!"
test_phone = f"+91999{int(time.time()) % 1000000:06d}"

print(f"Test Email: {test_email}")
print(f"Test Password: {test_password}")
print(f"Test Phone: {test_phone}")
print()

# STEP 1: Create customer with Admin API
print("STEP 1: Creating customer with Admin API...")
print("-" * 60)

admin_url = f"https://{STORE}/admin/api/{API_VERSION}/graphql.json"

mutation = """
mutation customerCreate($input: CustomerInput!) {
    customerCreate(input: $input) {
        customer {
            id
            email
            phone
        }
        userErrors {
            field
            message
        }
    }
}
"""

variables = {
    "input": {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "passwordConfirmation": test_password,
        "firstName": "Test"
    }
}

response = requests.post(
    admin_url,
    json={"query": mutation, "variables": variables},
    headers={
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ADMIN_TOKEN
    }
)

result = response.json()
print("Response from Admin API:")
print(json.dumps(result, indent=2))
print()

if result.get("data", {}).get("customerCreate", {}).get("userErrors"):
    print("❌ FAILED - Errors:", result["data"]["customerCreate"]["userErrors"])
    exit(1)

customer = result.get("data", {}).get("customerCreate", {}).get("customer")
if not customer:
    print("❌ FAILED - No customer created")
    exit(1)

print("✅ Customer created successfully!")
print(f"   ID: {customer['id']}")
print(f"   Email: {customer['email']}")
print(f"   Phone: {customer['phone']}")
print(f"   Password in response: NO (not returned by Admin API)")
print()

# Wait a moment for Shopify to process
time.sleep(3)

# STEP 2: Try to login with Storefront API using the password we set
print("STEP 2: Testing password with Storefront API...")
print("-" * 60)

storefront_url = f"https://{STORE}/api/{API_VERSION}/graphql.json"

login_mutation = """
mutation customerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) {
    customerAccessTokenCreate(input: $input) {
        customerAccessToken {
            accessToken
            expiresAt
        }
        customerUserErrors {
            code
            field
            message
        }
    }
}
"""

login_variables = {
    "input": {
        "email": test_email,
        "password": test_password
    }
}

response = requests.post(
    storefront_url,
    json={"query": login_mutation, "variables": login_variables},
    headers={
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": STOREFRONT_TOKEN
    }
)

result = response.json()
print("Response from Storefront API:")
print(json.dumps(result, indent=2))
print()

errors = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerUserErrors", [])
if errors:
    print("❌ FAILED - Could not login:", errors)
    exit(1)

token_data = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerAccessToken")
if not token_data:
    print("❌ FAILED - No access token returned")
    exit(1)

print("✅ Login successful with Storefront API!")
print(f"   Access Token: {token_data['accessToken'][:50]}...")
print(f"   Expires: {token_data['expiresAt']}")
print()

# CONCLUSION
print("=" * 60)
print("🎉 BRIDGE METHOD VERIFIED!")
print("=" * 60)
print()
print("What happened:")
print("1. ✅ Admin API created customer WITH password")
print("2. ✅ Admin API returned email (but NOT password)")
print("3. ✅ We kept the password in our code")
print("4. ✅ Storefront API accepted email + password")
print("5. ✅ Storefront API returned access token")
print()
print("Proof:")
print("- If password wasn't set, Storefront API would reject it")
print("- But it worked! This proves Admin API DID set the password")
print("- Admin API just doesn't RETURN passwords (security)")
print()
print("This is exactly how GoKwik/KwikPass work!")
print()

