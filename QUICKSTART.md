# ⚡ Quick Start (5 Minutes)

Get the backend running in 5 minutes!

## Step 1: Install (1 min)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (2 min)

The `.env` file is already created. You need to update **2 critical values**:

### Required: Shopify Admin API Token

1. Go to: https://f3lifestyle.myshopify.com/admin/settings/apps/development
2. Click **"Create an app"**
3. Name: "SlayFashion Backend"
4. Configure **Admin API scopes**:
   - ✅ `read_customers`
   - ✅ `write_customers`
5. Click **"Install app"**
6. Copy the **Admin API access token** (starts with `shpat_`)

Open `.env` and paste it:

```env
SHOPIFY_ADMIN_API_TOKEN=shpat_xxxxxxxxxxxxx  # ← Paste your token here
```

### Optional: Twilio (for real SMS)

For now, skip this! The backend will run in **dev mode** and print OTP codes to the console.

Later, when you need real SMS:
1. Sign up at https://www.twilio.com
2. Get credentials and update `.env`

## Step 3: Run! (1 min)

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

## Step 4: Test (1 min)

Open your browser: **http://localhost:8000/docs**

### Send OTP

1. Find **POST /api/auth/send-otp**
2. Click **"Try it out"**
3. Enter:
   ```json
   {
     "phone": "+919876543210"
   }
   ```
4. Click **Execute**
5. Copy the `session_id` from response

### Check Console for OTP

Look at your terminal where the backend is running. You'll see:

```
⚠️ DEV MODE: OTP not sent but proceeding. OTP is: 123456
```

### Verify OTP

1. Find **POST /api/auth/verify-otp**
2. Click **"Try it out"**
3. Enter:
   ```json
   {
     "phone": "+919876543210",
     "otp": "123456",
     "session_id": "paste_session_id_here"
   }
   ```
4. Click **Execute**

You should get:
```json
{
  "success": true,
  "message": "Login successful",
  "customer": { ... },
  "access_token": "eyJ..."
}
```

🎉 **It works!**

## What's Next?

### Option 1: Integrate with React Native App

See **INTEGRATION.md** for complete frontend integration guide.

Quick version:
```typescript
// Update backend URL
const API_URL = Platform.OS === 'android' 
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'http://localhost:8000'; // iOS simulator

// For physical device, use your computer's IP:
// const API_URL = 'http://192.168.1.100:8000';
```

### Option 2: Deploy to Production

See **README.md** for deployment guides (Railway, Heroku, DigitalOcean).

### Option 3: Enable Real SMS

Update `.env` with Twilio credentials:
```env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

Restart the backend and OTPs will be sent via SMS!

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Port 8000 already in use
Change port in `.env`:
```env
PORT=8001
```

### Shopify API errors
- Make sure `SHOPIFY_ADMIN_API_TOKEN` is correct
- Check API scopes include `read_customers` and `write_customers`
- Verify store domain doesn't include "https://" (just: `f3lifestyle.myshopify.com`)

---

## Files Overview

```
slayfashionbackend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── models.py        # Database models
│   ├── routers/
│   │   └── auth.py      # Auth endpoints
│   └── services/
│       ├── otp_service.py       # OTP logic
│       └── shopify_service.py   # Shopify API
├── .env                 # Configuration (UPDATE THIS)
├── run.py              # Start server
└── README.md           # Full documentation
```

---

## Need Help?

- 📚 **Full Docs**: `README.md`
- 🔧 **Setup Guide**: `SETUP.md`
- 📱 **Frontend Integration**: `INTEGRATION.md`
- 🧪 **Test API**: Open http://localhost:8000/docs

---

**You're all set! 🚀**

Start building your Shopify OTP login experience!

