# 🚨 Security Fix - Exposed Shopify Token

## What Happened

GitHub detected a Shopify Admin API token in your code and blocked the push. This is **GOOD** - it's protecting your store from unauthorized access.

## ⚠️ IMPORTANT: Regenerate Your Token

Since the token was exposed (even briefly), you should **regenerate it immediately**:

### Step 1: Regenerate Shopify Admin API Token

1. Go to: https://f3lifestyle.myshopify.com/admin/settings/apps/development
2. Find your app: "SlayFashion Backend"
3. Click on it
4. Go to "API credentials"
5. Click **"Regenerate Admin API access token"**
6. Copy the new token (starts with `shpat_`)
7. **Update your `.env` file** with the new token

## 🧹 Clean Git History

The exposed token is in your git history. Here's how to remove it:

### Option 1: Remove Last Commit (If You Haven't Pushed Successfully)

```bash
# Go to your repo
cd /Users/granth/Desktop/slayfashionbackend

# Remove the last commit (keeps your changes)
git reset --soft HEAD~1

# Stage only the safe files
git add app/
git add requirements.txt
git add README.md
git add SETUP.md
git add QUICKSTART.md
git add INTEGRATION.md
git add ARCHITECTURE.md
git add DEPLOYMENT.md
git add docker-compose.yml
git add Dockerfile
git add .gitignore
git add run.py

# DO NOT add test files with hardcoded tokens!

# Commit again with clean code
git commit -m "Add FastAPI backend with OTP authentication (tokens removed)"

# Push
git push origin main
```

### Option 2: Force Remove Secret from History (Nuclear Option)

If the token is in multiple commits:

```bash
# Install BFG Repo Cleaner
brew install bfg

# Remove the token from entire history
bfg --replace-text <(echo 'shpat_YOUR_OLD_TOKEN_HERE==>TOKEN_REMOVED')

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (DANGER: rewrites history)
git push --force origin main
```

### Option 3: Click GitHub's "Allow Secret" Link (NOT RECOMMENDED)

GitHub gave you this option, but **DON'T DO IT**:
```
https://github.com/granth16/slayfashionbackend/security/secret-scanning/unblock-secret/35NKrTXJCIA58lPfdhN0iN3LjSo
```

This would push the secret publicly. Instead, regenerate your token!

## ✅ Proper Way to Handle Secrets

### Use Environment Variables

Create `.env` file (it's in .gitignore):

```bash
# .env (NEVER commit this!)
SHOPIFY_ADMIN_API_TOKEN=your_new_token_here
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_storefront_token
```

### Running Tests Safely

```bash
# Set environment variables before running tests
export SHOPIFY_ADMIN_API_TOKEN=shpat_your_new_token
export SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_token

# Then run tests
python3 test_full_backend.py
```

Or create `.env.test` file (also gitignored):

```bash
# Copy your tokens here
cp .env .env.test

# Edit with your tokens
nano .env.test

# Tests will load from .env automatically
python3 test_full_backend.py
```

## 📋 Checklist

- [ ] Regenerate Shopify Admin API token
- [ ] Update `.env` file with new token
- [ ] Clean git history (Option 1 recommended)
- [ ] Verify `.env` is in `.gitignore`
- [ ] Never commit tokens in code again
- [ ] Push clean code to GitHub

## 🔒 Prevention

The following files are now in `.gitignore`:

```
.env
.env.local
.env.test
.env.production
*.db
*.sqlite
```

**Always check before committing:**

```bash
# Check what you're committing
git diff --staged

# Look for "shpat_" or other tokens
git diff --staged | grep -i "shpat_"
```

## ✅ After Fix

Once you've:
1. Regenerated the token
2. Cleaned git history  
3. Updated `.env` with new token

You can safely push:

```bash
git push origin main
```

---

**Remember:** Tokens in git history are compromised forever. Always regenerate exposed tokens!

