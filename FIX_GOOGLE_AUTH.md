# Fix Google Authentication Error

## The Error You're Seeing:
**"Access blocked: Authorisation error - Missing required parameter: client_id"**

This happens because Google OAuth credentials haven't been configured yet.

## Quick Fix (5 minutes):

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. If prompted, configure the OAuth consent screen first (choose External)
6. For OAuth client ID:
   - Application type: **Web application**
   - Name: "AI Quiz Hub"
   - **Authorized redirect URIs**: Add this EXACT URL:
     ```
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
7. Click **CREATE**
8. **Copy the Client ID and Client Secret** (you'll need these in Step 3)

### Step 2: Start Django Server & Login to Admin

```bash
# Start server
python manage.py runserver

# Superuser already created:
# Username: admin
# Password: (set it now if not set)
```

If you need to set/reset admin password:
```bash
python manage.py changepassword admin
```

### Step 3: Configure in Django Admin

1. Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

2. Login with admin credentials

3. **Fix the Site:**
   - Click **Sites** (under "SITES" section)
   - Click on "example.com" 
   - Change:
     - Domain name: `127.0.0.1:8000`
     - Display name: `AI Quiz Hub`
   - Click **SAVE**

4. **Add Google OAuth App:**
   - Go back to admin home
   - Click **Social applications** (under "SOCIAL ACCOUNTS" section)
   - Click **ADD SOCIAL APPLICATION** (top right)
   - Fill in:
     - **Provider**: Select "Google" from dropdown
     - **Name**: `Google OAuth`
     - **Client id**: Paste the Client ID from Step 1
     - **Secret key**: Paste the Client Secret from Step 1
     - **Sites**: 
       - Find "127.0.0.1:8000" in the "Available sites" box
       - Select it and click the right arrow to move it to "Chosen sites"
   - Click **SAVE**

### Step 4: Test Google Sign-In

1. Go to [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
2. Click "Continue with Google"
3. Choose your Google account
4. ✅ You should be logged in!

## Troubleshooting:

### Still getting "invalid_request"?
- Make sure the redirect URI in Google Console is EXACTLY:
  `http://127.0.0.1:8000/accounts/google/login/callback/`
- Access site using `127.0.0.1:8000` not `localhost:8000`

### "redirect_uri_mismatch" error?
- Double-check the redirect URI in Google Console matches exactly
- Make sure there's no trailing slash issues

### Can't find Social Applications in admin?
- Server might need restart: Stop (Ctrl+C) and run `python manage.py runserver` again

### Google shows "This app isn't verified"
- This is normal for development
- Click "Advanced" → "Go to AI Quiz Hub (unsafe)" to continue
- For production, you'd need to verify your app

## Why This Approach?

Django Allauth stores OAuth credentials in the database (via Django Admin) rather than environment variables. This is more secure and flexible for production deployments.

## Need More Help?

See the full guide: `GOOGLE_OAUTH_SETUP.md`
