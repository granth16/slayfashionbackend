# 🛍️ SlayFashion Backend API

FastAPI backend for OTP-based Shopify customer authentication using the **"bridge method"** - the same approach used by **GoKwik** and **KwikPass** for phone/OTP login with Shopify.

## 🎯 Overview

Since Shopify's **Admin API cannot create customer access tokens** directly, this backend implements a workaround:

1. **Send OTP** to customer's phone via SMS
2. **Verify OTP** code
3. **Find or Create Customer** in Shopify using Admin API
4. **Store Hidden Credentials** (phone → Shopify ID → hidden email/password) in database
5. **Bridge to Storefront API** - Use hidden credentials to get customer access token
6. **Return Token** to frontend for seamless Shopify login

This allows customers to log in with just their phone number + OTP, without ever seeing email or password.

## 🏗️ Architecture

```
Customer Phone/OTP
        ↓
   Backend (FastAPI)
        ↓
   ┌─────────────────────┐
   │  OTP Verification   │
   │  (Twilio SMS)       │
   └─────────────────────┘
        ↓
   ┌─────────────────────┐
   │  Shopify Admin API  │
   │  Find/Create        │
   │  Customer           │
   └─────────────────────┘
        ↓
   ┌─────────────────────┐
   │  Our Database       │
   │  Phone → ID →       │
   │  Hidden Email/Pass  │
   └─────────────────────┘
        ↓
   ┌─────────────────────┐
   │ Shopify Storefront  │
   │ API (Hidden Creds)  │
   │ → Access Token      │
   └─────────────────────┘
        ↓
   Frontend (Token-based auth)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Database (start with SQLite for development)
DATABASE_URL=sqlite:///./slayfashion.db

# Shopify Configuration
SHOPIFY_STORE_DOMAIN=f3lifestyle.myshopify.com
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx
SHOPIFY_STOREFRONT_ACCESS_TOKEN=aef92cf6067f10d1f18f3bd6cbee4012
SHOPIFY_API_VERSION=2024-10

# Twilio (for OTP SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# JWT Secret
JWT_SECRET_KEY=your-super-secret-key-change-this

# OTP Settings
OTP_EXPIRATION_MINUTES=10
OTP_LENGTH=6
```

### 3. Run the Server

```bash
python run.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 🔐 Authentication

#### `POST /api/auth/send-otp`
Send OTP to customer's phone number

**Request:**
```json
{
  "phone": "+911234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "session_id": "abc123xyz789..."
}
```

---

#### `POST /api/auth/verify-otp`
Verify OTP and get Shopify customer access token

**Request:**
```json
{
  "phone": "+911234567890",
  "otp": "123456",
  "session_id": "abc123xyz789..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "customer": {
    "id": "1",
    "phone": "+911234567890",
    "email": "customer.911234567890@slayfashion.internal",
    "first_name": "John",
    "last_name": "Doe",
    "shopify_customer_id": "gid://shopify/Customer/123456"
  },
  "access_token": "customer_access_token_here",
  "token_expires_at": "2025-11-19T12:00:00Z"
}
```

The `access_token` can be used with **Shopify Storefront API** to:
- Fetch customer orders
- Get customer profile
- Manage customer addresses
- Create checkouts

---

### 👤 Customer

#### `GET /api/customer/profile?phone=+911234567890`
Get customer profile by phone

#### `GET /api/customer/check?phone=+911234567890`
Check if customer exists in database

---

## 🗄️ Database Schema

### `customers` table
Stores the phone → Shopify customer → hidden credentials mapping

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| phone | String | Customer phone (unique) |
| shopify_customer_id | String | Shopify customer ID (unique) |
| shopify_email | String | Hidden email for Shopify login |
| shopify_password | String | Hidden password (consider encrypting) |
| first_name | String | Customer first name |
| last_name | String | Customer last name |
| created_at | DateTime | Record creation time |
| updated_at | DateTime | Last update time |
| is_active | Boolean | Account status |

### `otp_verifications` table
Stores OTP codes for verification

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| phone | String | Phone number |
| otp_code | String | 6-digit OTP |
| session_id | String | Session identifier (unique) |
| is_verified | Boolean | Verification status |
| attempts | Integer | Verification attempts |
| created_at | DateTime | OTP creation time |
| expires_at | DateTime | OTP expiration time |
| verified_at | DateTime | Verification time |

---

## 🔒 Security Considerations

### ✅ Best Practices Implemented

1. **Hidden Credentials**: Email and password never exposed to customer
2. **OTP Expiration**: OTPs expire after 10 minutes
3. **Rate Limiting**: Max 5 OTP verification attempts
4. **Secure Password Generation**: Random 16-character passwords
5. **HTTPS**: Use HTTPS in production (configure reverse proxy)

### ⚠️ Production Recommendations

1. **Encrypt Passwords**: Use encryption (e.g., Fernet) for `shopify_password` field
2. **Rate Limiting**: Add rate limiting middleware (e.g., slowapi)
3. **Database**: Use PostgreSQL instead of SQLite
4. **Environment Variables**: Never commit `.env` file
5. **Monitoring**: Add logging and error tracking (e.g., Sentry)
6. **Backup**: Regular database backups
7. **SSL/TLS**: Use HTTPS everywhere

---

## 🔧 Development

### Project Structure

```
slayfashionbackend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings and environment
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   └── customer.py      # Customer endpoints
│   └── services/
│       ├── __init__.py
│       ├── otp_service.py   # OTP generation/verification
│       └── shopify_service.py  # Shopify API integration
├── .env                     # Environment variables (gitignored)
├── .env.example             # Environment template
├── .gitignore
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md
```

### Running Tests

```bash
# TODO: Add pytest tests
pytest
```

### Database Migrations

Using Alembic for migrations:

```bash
# Initialize migrations (first time)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add customers table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🌐 Deployment

### Deploy to Railway

1. Install Railway CLI: https://docs.railway.app/develop/cli
2. Login: `railway login`
3. Initialize: `railway init`
4. Add PostgreSQL: `railway add postgresql`
5. Set environment variables in Railway dashboard
6. Deploy: `railway up`

### Deploy to Heroku

```bash
# Create Heroku app
heroku create slayfashion-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
heroku config:set SHOPIFY_ADMIN_API_TOKEN=your-token
# ... set all other variables

# Deploy
git push heroku main
```

### Deploy to DigitalOcean

Use Docker for easy deployment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

---

## 🧪 Testing with Postman/Curl

### Send OTP
```bash
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+911234567890"}'
```

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+911234567890",
    "otp": "123456",
    "session_id": "your_session_id_here"
  }'
```

---

## 📚 Resources

- **Shopify Admin API**: https://shopify.dev/docs/api/admin-graphql
- **Shopify Storefront API**: https://shopify.dev/docs/api/storefront
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Twilio SMS API**: https://www.twilio.com/docs/sms
- **SQLAlchemy**: https://docs.sqlalchemy.org

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use this for your projects!

---

## ❓ FAQ

**Q: Why not use Shopify's Customer Account API?**  
A: The new Customer Account API is better but more complex to set up. This solution works with standard Shopify plans immediately.

**Q: Is this secure?**  
A: Yes, when properly configured with HTTPS, encrypted passwords, and rate limiting. The hidden credentials approach is used by major payment gateways like GoKwik.

**Q: Can I use this in production?**  
A: Yes! Just make sure to follow the security recommendations above.

**Q: What about SMS costs?**  
A: Twilio charges per SMS. Consider your scale and possibly implement WhatsApp OTP (free with Twilio) as an alternative.

---

Made with ❤️ for SlayFashion

# slayfashionbackend
