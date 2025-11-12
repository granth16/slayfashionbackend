#!/usr/bin/env python3
"""Test Shopify REST Admin API - Create customer with password"""
import requests
import json
import time
import sys

# Get token from command line
if len(sys.argv) < 2:
    print("Usage: python3 test_rest_api.py YOUR_ADMIN_TOKEN")
    sys.exit(1)

ADMIN_TOKEN = sys.argv[1]
STORE = 'f3lifestyle.myshopify.com'
STOREFRONT_TOKEN = 'aef92cf6067f10d1f18f3bd6cbee4012'
API_VERSION = '2024-10'

print("=" * 60)
print("Testing Shopify REST Admin API - Create Customer with Password")
print("=" * 60)
print(f"Store: {STORE}")
print()

# Test data
test_email = f"test{int(time.time())}@slayfashion.test"
test_password = "SecurePassword123!"
test_phone = f"+91 999 {int(time.time()) % 1000000:06d}"  # Format with spaces

print(f"Test Email: {test_email}")
print(f"Test Password: {test_password}")
print(f"Test Phone: {test_phone}")
print()

# STEP 1: Create customer with REST Admin API
print("STEP 1: Creating customer with REST Admin API...")
print("-" * 60)

rest_url = f"https://{STORE}/admin/api/{API_VERSION}/customers.json"

customer_data = {
    "customer": {
        "email": test_email,
        # "phone": test_phone,  # Skip phone for now - format issues
        "first_name": "Test",
        "last_name": "Customer",
        "password": test_password,
        "password_confirmation": test_password,
        "send_email_welcome": False,
        "verified_email": True
    }
}

print(f"Sending to: {rest_url}")
print(f"Data: {json.dumps(customer_data, indent=2)}")
print()

response = requests.post(
    rest_url,
    json=customer_data,
    headers={
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ADMIN_TOKEN
    }
)

print(f"Status Code: {response.status_code}")
print("Response from REST Admin API:")
print(json.dumps(response.json(), indent=2))
print()

if response.status_code != 201:
    print("❌ FAILED - Could not create customer")
    print(f"Error: {response.json()}")
    sys.exit(1)

customer = response.json().get("customer")
if not customer:
    print("❌ FAILED - No customer in response")
    sys.exit(1)

print("✅ Customer created successfully with REST API!")
print(f"   ID: {customer['id']}")
print(f"   Email: {customer['email']}")
print(f"   Phone: {customer['phone']}")
print(f"   Password was SET: ✅ (REST API accepts password field)")
print()

# Wait for Shopify to process
print("Waiting 3 seconds for Shopify to process...")
time.sleep(3)

# STEP 2: Verify password works with Storefront API
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
    print("❌ FAILED - Could not login with password")
    print(f"Errors: {errors}")
    print()
    print("This might mean:")
    print("1. Password wasn't set properly")
    print("2. Shopify needs more time to process")
    print("3. Email needs to be verified first")
    sys.exit(1)

token_data = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerAccessToken")
if not token_data:
    print("❌ FAILED - No access token returned")
    sys.exit(1)

print("✅ Login successful with Storefront API!")
print(f"   Access Token: {token_data['accessToken'][:50]}...")
print(f"   Expires: {token_data['expiresAt']}")
print()

# SUCCESS SUMMARY
print("=" * 60)
print("🎉 BRIDGE METHOD VERIFIED WITH REST API!")
print("=" * 60)
print()
print("What happened:")
print("1. ✅ REST Admin API created customer WITH password")
print("2. ✅ REST Admin API returned customer data")
print("3. ✅ We stored the password in our code")
print("4. ✅ Storefront API accepted email + password")
print("5. ✅ Storefront API returned access token")
print()
print("Key Findings:")
print("• GraphQL Admin API: ❌ Does NOT support password fields")
print("• REST Admin API: ✅ DOES support password & password_confirmation")
print("• Storefront API: ✅ Validates passwords and returns tokens")
print()
print("This IS how GoKwik/KwikPass work!")
print("They use REST Admin API (not GraphQL) for customer creation.")
print()

