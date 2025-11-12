import httpx
import secrets
import string
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models import Customer
from ..config import get_settings

settings = get_settings()


class ShopifyService:
    """Service for interacting with Shopify Admin and Storefront APIs"""
    
    def __init__(self):
        self.store_domain = settings.shopify_store_domain
        self.admin_token = settings.shopify_admin_api_token
        self.storefront_token = settings.shopify_storefront_access_token
        self.api_version = settings.shopify_api_version
        
        self.admin_url = f"https://{self.store_domain}/admin/api/{self.api_version}/graphql.json"
        self.storefront_url = f"https://{self.store_domain}/api/{self.api_version}/graphql.json"
    
    @staticmethod
    def generate_random_password(length: int = 16) -> str:
        """Generate random password for Shopify customer"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_hidden_email(phone: str) -> str:
        """Generate hidden email for phone-based customer"""
        # Remove + and other special chars from phone
        clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
        # Create unique email that won't conflict
        return f"customer.{clean_phone}@slayfashion.internal"
    
    async def admin_api_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make request to Shopify Admin API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.admin_url,
                json={"query": query, "variables": variables or {}},
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Access-Token": self.admin_token
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise Exception(f"Shopify Admin API error: {data['errors']}")
            
            return data
    
    async def storefront_api_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make request to Shopify Storefront API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.storefront_url,
                json={"query": query, "variables": variables or {}},
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Storefront-Access-Token": self.storefront_token
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise Exception(f"Shopify Storefront API error: {data['errors']}")
            
            return data
    
    async def find_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Find customer in Shopify by phone number using Admin API"""
        query = """
        query($query: String!) {
            customers(first: 1, query: $query) {
                edges {
                    node {
                        id
                        email
                        phone
                        firstName
                        lastName
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        
        result = await self.admin_api_request(query, {"query": f"phone:{phone}"})
        
        edges = result.get("data", {}).get("customers", {}).get("edges", [])
        if edges:
            return edges[0]["node"]
        return None
    
    async def create_customer_in_shopify(self, phone: str, email: str, password: str) -> Dict[str, Any]:
        """
        Create customer in Shopify using REST Admin API with email and password
        
        NOTE: We use REST API (not GraphQL) because:
        - GraphQL Admin API does NOT support password fields in CustomerInput
        - REST Admin API DOES support password & password_confirmation fields
        - This is how GoKwik/KwikPass implement OTP login for Shopify
        """
        rest_url = f"https://{self.store_domain}/admin/api/{self.api_version}/customers.json"
        
        # Prepare customer data - phone is optional as it can cause validation issues
        customer_data = {
            "customer": {
                "email": email,
                "password": password,
                "password_confirmation": password,
                "send_email_welcome": False,
                "verified_email": True
            }
        }
        
        # Try to add phone if provided (but don't fail if Shopify rejects the format)
        if phone:
            customer_data["customer"]["phone"] = phone
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                rest_url,
                json=customer_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Shopify-Access-Token": self.admin_token
                }
            )
            
            # If phone validation fails, retry without phone
            if response.status_code == 422 and phone:
                error_data = response.json()
                if "phone" in error_data.get("errors", {}):
                    print(f"⚠️ Phone format rejected by Shopify, retrying without phone...")
                    del customer_data["customer"]["phone"]
                    response = await client.post(
                        rest_url,
                        json=customer_data,
                        headers={
                            "Content-Type": "application/json",
                            "X-Shopify-Access-Token": self.admin_token
                        }
                    )
            
            if response.status_code not in [200, 201]:
                error_data = response.json()
                raise Exception(f"Failed to create customer: {error_data}")
            
            result = response.json()
            customer = result.get("customer")
            
            if not customer:
                raise Exception("No customer returned from REST API")
            
            # Convert REST API response to match GraphQL format for consistency
            return {
                "id": customer.get("admin_graphql_api_id") or f"gid://shopify/Customer/{customer['id']}",
                "email": customer["email"],
                "phone": customer.get("phone"),
                "firstName": customer.get("first_name"),
                "lastName": customer.get("last_name")
            }
    
    async def create_customer_access_token(self, email: str, password: str) -> tuple[str, str]:
        """
        Create customer access token using Storefront API with email/password
        This is the "bridge method" - using hidden credentials to get access token
        Returns: (access_token, expires_at)
        """
        mutation = """
        mutation($input: CustomerAccessTokenCreateInput!) {
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
        
        result = await self.storefront_api_request(mutation, variables)
        
        errors = result.get("data", {}).get("customerAccessTokenCreate", {}).get("customerUserErrors", [])
        if errors:
            raise Exception(f"Failed to create access token: {errors}")
        
        token_data = result["data"]["customerAccessTokenCreate"]["customerAccessToken"]
        return token_data["accessToken"], token_data["expiresAt"]
    
    async def find_or_create_customer(self, phone: str, db: Session) -> tuple[Customer, str, str]:
        """
        Find or create customer using the "bridge method"
        Returns: (customer_record, access_token, expires_at)
        """
        # Check if we already have this customer in our database
        customer_record = db.query(Customer).filter(Customer.phone == phone).first()
        
        if customer_record:
            # Customer exists, get new access token using stored credentials
            print(f"✅ Customer found in database: {phone}")
            access_token, expires_at = await self.create_customer_access_token(
                customer_record.shopify_email,
                customer_record.shopify_password
            )
            return customer_record, access_token, expires_at
        
        # Customer not in our database, check Shopify
        shopify_customer = await self.find_customer_by_phone(phone)
        
        if shopify_customer:
            # Customer exists in Shopify but not in our DB
            # This is a problem - we don't have their password
            # We need to create a new customer with hidden credentials
            print(f"⚠️ Customer exists in Shopify but not in our DB: {phone}")
            # For now, we'll create a new entry (you might want to handle this differently)
        
        # Create new customer with hidden credentials
        print(f"🆕 Creating new customer: {phone}")
        
        hidden_email = self.generate_hidden_email(phone)
        hidden_password = self.generate_random_password()
        
        # Create in Shopify
        shopify_customer = await self.create_customer_in_shopify(
            phone=phone,
            email=hidden_email,
            password=hidden_password
        )
        
        # Store in our database
        customer_record = Customer(
            phone=phone,
            shopify_customer_id=shopify_customer["id"],
            shopify_email=hidden_email,
            shopify_password=hidden_password,  # Store plain password (consider encrypting)
            first_name=shopify_customer.get("firstName"),
            last_name=shopify_customer.get("lastName")
        )
        db.add(customer_record)
        db.commit()
        db.refresh(customer_record)
        
        # Get access token
        access_token, expires_at = await self.create_customer_access_token(
            hidden_email,
            hidden_password
        )
        
        return customer_record, access_token, expires_at

