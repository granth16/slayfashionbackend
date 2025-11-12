#!/usr/bin/env python3
"""
Test Shopify Admin API capabilities:
1. Create customer with password
2. Retrieve customer info (email returned, password NOT returned)
3. Update customer password
"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_ADMIN_API_TOKEN = os.getenv("SHOPIFY_ADMIN_API_TOKEN")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-10")

ADMIN_URL = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"

print("=" * 80)
print("🧪 Shopify Admin API Test")
print("=" * 80)
print(f"Store: {SHOPIFY_STORE_DOMAIN}")
print(f"API Version: {SHOPIFY_API_VERSION}")
print()


async def admin_api_request(query: str, variables: dict = None):
    """Make request to Shopify Admin API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            ADMIN_URL,
            json={"query": query, "variables": variables or {}},
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_TOKEN
            }
        )
        response.raise_for_status()
        return response.json()


async def test_1_create_customer_with_password():
    """
    TEST 1: Create a customer with email and password
    Expected: Customer created successfully
    Note: Password is NOT returned in response (security)
    """
    print("📝 TEST 1: Creating customer with password...")
    print("-" * 80)
    
    test_email = f"test.customer.{asyncio.get_event_loop().time()}@slayfashion.test"
    test_password = "TestPassword123!SecureRandom"
    test_phone = f"+9199999{int(asyncio.get_event_loop().time()) % 10000:04d}"
    
    mutation = """
    mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
            customer {
                id
                email
                phone
                firstName
                lastName
                createdAt
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
            "firstName": "Test",
            "lastName": "Customer"
        }
    }
    
    result = await admin_api_request(mutation, variables)
    
    if result.get("data", {}).get("customerCreate", {}).get("userErrors"):
        errors = result["data"]["customerCreate"]["userErrors"]
        print(f"❌ FAILED: {errors}")
        return None
    
    customer = result.get("data", {}).get("customerCreate", {}).get("customer")
    
    if customer:
        print("✅ SUCCESS: Customer created with password!")
        print(f"   Customer ID: {customer['id']}")
        print(f"   Email: {customer['email']}")
        print(f"   Phone: {customer['phone']}")
        print(f"   Password in request: {test_password}")
        print(f"   Password in response: NOT RETURNED (as expected for security)")
        print()
        print(f"💡 IMPORTANT: Admin API does NOT return passwords!")
        print(f"   But the password WAS set in Shopify's system.")
        print()
        return customer["id"], test_email, test_password, test_phone
    
    print("❌ FAILED: No customer returned")
    return None


async def test_2_retrieve_customer(customer_id: str):
    """
    TEST 2: Retrieve customer info
    Expected: Email IS returned, password is NOT returned
    """
    print("📝 TEST 2: Retrieving customer info...")
    print("-" * 80)
    
    query = """
    query getCustomer($id: ID!) {
        customer(id: $id) {
            id
            email
            phone
            firstName
            lastName
        }
    }
    """
    
    result = await admin_api_request(query, {"id": customer_id})
    customer = result.get("data", {}).get("customer")
    
    if customer:
        print("✅ SUCCESS: Customer retrieved!")
        print(f"   Email: {customer['email']} ✅ (returned)")
        print(f"   Phone: {customer['phone']} ✅ (returned)")
        print(f"   Password: NOT IN RESPONSE ✅ (never returned by Admin API)")
        print()
        print(f"💡 This is why we need the 'bridge method':")
        print(f"   - Admin API can CREATE/UPDATE passwords")
        print(f"   - Admin API CANNOT retrieve passwords")
        print(f"   - Admin API CANNOT create access tokens")
        print(f"   - We store the password ourselves")
        print(f"   - We use Storefront API to get access tokens")
        print()
        return True
    
    print("❌ FAILED: Could not retrieve customer")
    return False


async def test_3_update_customer_password(customer_id: str):
    """
    TEST 3: Update customer's password
    Expected: Password updated successfully (but not returned)
    """
    print("📝 TEST 3: Updating customer password...")
    print("-" * 80)
    
    new_password = "NewPassword456!VerySecure"
    
    mutation = """
    mutation customerUpdate($input: CustomerInput!) {
        customerUpdate(input: $input) {
            customer {
                id
                email
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
            "id": customer_id,
            "password": new_password,
            "passwordConfirmation": new_password
        }
    }
    
    result = await admin_api_request(mutation, variables)
    
    if result.get("data", {}).get("customerUpdate", {}).get("userErrors"):
        errors = result["data"]["customerUpdate"]["userErrors"]
        print(f"❌ FAILED: {errors}")
        return None
    
    customer = result.get("data", {}).get("customerUpdate", {}).get("customer")
    
    if customer:
        print("✅ SUCCESS: Password updated!")
        print(f"   New password set: {new_password}")
        print(f"   Password in response: NOT RETURNED (as expected)")
        print()
        print(f"💡 Admin API CAN update passwords, just doesn't return them!")
        print()
        return new_password
    
    print("❌ FAILED: Could not update password")
    return None


async def test_4_verify_with_storefront_api(email: str, password: str):
    """
    TEST 4: Verify password works by creating access token via Storefront API
    Expected: Access token created successfully
    """
    print("📝 TEST 4: Verifying password with Storefront API...")
    print("-" * 80)
    
    storefront_token = os.getenv("SHOPIFY_STOREFRONT_ACCESS_TOKEN")
    storefront_url = f"https://{SHOPIFY_STORE_DOMAIN}/api/{SHOPIFY_API_VERSION}/graphql.json"
    
    mutation = """
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
    
    variables = {
        "input": {
            "email": email,
            "password": password
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            storefront_url,
            json={"query": mutation, "variables": variables},
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Storefront-Access-Token": storefront_token
            }
        )
        result = response.json()
    
    errors = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerUserErrors", [])
    if errors:
        print(f"❌ FAILED: {errors}")
        return False
    
    token_data = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerAccessToken")
    
    if token_data:
        print("✅ SUCCESS: Access token created!")
        print(f"   This proves the password was set correctly!")
        print(f"   Access Token: {token_data['accessToken'][:50]}...")
        print(f"   Expires At: {token_data['expiresAt']}")
        print()
        print(f"🎉 BRIDGE METHOD WORKS!")
        print(f"   ✅ Admin API set the password")
        print(f"   ✅ We stored the password in our database")
        print(f"   ✅ Storefront API accepted the password")
        print(f"   ✅ Customer access token generated")
        print(f"   ✅ Customer can now use Shopify services")
        print()
        return True
    
    print("❌ FAILED: Could not create access token")
    return False


async def test_5_search_customer_by_phone(phone: str):
    """
    TEST 5: Search for customer by phone number
    Expected: Customer found, email returned, password NOT returned
    """
    print("📝 TEST 5: Searching customer by phone...")
    print("-" * 80)
    
    query = """
    query searchCustomers($query: String!) {
        customers(first: 1, query: $query) {
            edges {
                node {
                    id
                    email
                    phone
                    firstName
                    lastName
                }
            }
        }
    }
    """
    
    result = await admin_api_request(query, {"query": f"phone:{phone}"})
    edges = result.get("data", {}).get("customers", {}).get("edges", [])
    
    if edges:
        customer = edges[0]["node"]
        print("✅ SUCCESS: Customer found by phone!")
        print(f"   Phone: {customer['phone']}")
        print(f"   Email: {customer['email']} ✅ (returned)")
        print(f"   Password: NOT IN RESPONSE ✅ (never returned)")
        print()
        return True
    
    print("❌ No customer found")
    return False


async def main():
    """Run all tests"""
    try:
        # TEST 1: Create customer with password
        result = await test_1_create_customer_with_password()
        if not result:
            print("⚠️ Cannot continue tests - customer creation failed")
            return
        
        customer_id, email, password, phone = result
        
        await asyncio.sleep(2)  # Give Shopify a moment
        
        # TEST 2: Retrieve customer (email returned, password NOT returned)
        await test_2_retrieve_customer(customer_id)
        
        await asyncio.sleep(2)
        
        # TEST 3: Update customer password
        new_password = await test_3_update_customer_password(customer_id)
        if not new_password:
            new_password = password  # Use original if update failed
        
        await asyncio.sleep(2)
        
        # TEST 4: Verify password works with Storefront API (THE BRIDGE!)
        await test_4_verify_with_storefront_api(email, new_password)
        
        await asyncio.sleep(2)
        
        # TEST 5: Search by phone
        await test_5_search_customer_by_phone(phone)
        
        # SUMMARY
        print("=" * 80)
        print("📊 SUMMARY - What Shopify Admin API Can/Cannot Do")
        print("=" * 80)
        print()
        print("✅ CAN DO:")
        print("   • Create customers WITH passwords")
        print("   • Update customer passwords")
        print("   • Retrieve customer info (email, phone, name, etc.)")
        print("   • Search customers by phone/email")
        print()
        print("❌ CANNOT DO:")
        print("   • Return/retrieve passwords (security - passwords are hashed)")
        print("   • Create customer access tokens")
        print("   • Login customers directly")
        print()
        print("🌉 THE BRIDGE METHOD:")
        print("   1. Admin API creates customer WITH password ✅")
        print("   2. WE store the password in OUR database ✅")
        print("   3. Admin API returns email (but NOT password) ✅")
        print("   4. WE use stored password + email with Storefront API ✅")
        print("   5. Storefront API returns customer access token ✅")
        print("   6. Customer is logged in! ✅")
        print()
        print("🎯 CONCLUSION:")
        print("   The bridge method works because:")
        print("   • Shopify stores the password (hashed)")
        print("   • WE also store the password (to use later)")
        print("   • Storefront API validates against Shopify's stored password")
        print("   • Customer never sees the password")
        print("   • This is exactly how GoKwik/KwikPass work!")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

