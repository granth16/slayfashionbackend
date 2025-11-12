# 🚀 Quick Setup Guide

## Prerequisites

- Python 3.9+ installed
- Shopify store with Admin API access
- Twilio account for SMS (or use dev mode)

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Shopify

### Get Admin API Token

1. Go to your Shopify Admin: `https://YOUR-STORE.myshopify.com/admin`
2. Navigate to: **Settings** → **Apps and sales channels** → **Develop apps**
3. Click **Create an app**
4. Name it: "SlayFashion Backend"
5. Configure **Admin API scopes**:
   - `read_customers`
   - `write_customers`
6. Click **Install app**
7. Copy the **Admin API access token** (starts with `shpat_`)

### Get Storefront API Token

1. In the same app, go to **Storefront API** tab
2. Configure **Storefront API scopes**:
   - `unauthenticated_read_customers`
   - `unauthenticated_write_customers`
3. Copy the **Storefront access token**

### Update .env file

Open `.env` and update:

```env
SHOPIFY_STORE_DOMAIN=YOUR-STORE.myshopify.com
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_storefront_token
```

## Step 3: Configure Twilio (Optional for Dev)

### Option A: Use Real Twilio (Production)

1. Sign up at https://www.twilio.com
2. Get a phone number
3. Copy credentials from dashboard:
   - Account SID
   - Auth Token
   - Phone Number

Update `.env`:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Option B: Dev Mode (Testing Without SMS)

The OTP service includes a dev mode that prints OTP to console instead of sending SMS.

Just leave Twilio credentials as-is and check the terminal for OTP codes:

```
⚠️ DEV MODE: OTP not sent but proceeding. OTP is: 123456
```

## Step 4: Run the Server

```bash
python run.py
```

You should see:

```
============================================================
🚀 SlayFashion Backend API
============================================================
📍 Host: 0.0.0.0
🔌 Port: 8000
📦 Shopify Store: f3lifestyle.myshopify.com
📚 API Docs: http://0.0.0.0:8000/docs
============================================================
```

## Step 5: Test the API

Open your browser to: **http://localhost:8000/docs**

### Test Flow:

1. **Send OTP**
   - Endpoint: `POST /api/auth/send-otp`
   - Body: `{"phone": "+911234567890"}`
   - Copy the `session_id` from response

2. **Check Console for OTP** (if in dev mode)
   - Look for: `⚠️ DEV MODE: OTP not sent but proceeding. OTP is: 123456`

3. **Verify OTP**
   - Endpoint: `POST /api/auth/verify-otp`
   - Body:
     ```json
     {
       "phone": "+911234567890",
       "otp": "123456",
       "session_id": "your_session_id_here"
     }
     ```
   - You'll get back a Shopify customer access token!

## Step 6: Integrate with Frontend

Update your React Native app's backend URL:

```typescript
// src/config/backend.ts
const BACKEND_API_URL = 'http://YOUR-IP:8000';
// For Android emulator: http://10.0.2.2:8000
// For iOS simulator: http://localhost:8000
// For physical device: http://192.168.1.XXX:8000
```

## Troubleshooting

### Database Errors
```bash
# Reset database
rm slayfashion.db
python run.py  # Will recreate tables
```

### Shopify API Errors
- Check that API tokens are correct
- Verify API scopes are enabled
- Make sure store domain doesn't include "https://"

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Change port in .env
PORT=8001
```

## Next Steps

✅ Backend is ready!

Now you can:
1. Deploy to production (Railway, Heroku, DigitalOcean)
2. Set up PostgreSQL for production database
3. Add rate limiting and monitoring
4. Integrate with your React Native app

## Need Help?

Check the main `README.md` for:
- Deployment guides
- Security recommendations
- API documentation
- FAQ

---

Happy coding! 🎉

