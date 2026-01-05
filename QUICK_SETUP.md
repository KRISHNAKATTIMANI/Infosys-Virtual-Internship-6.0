# Quick Setup Instructions for Google OAuth

## ✅ What's Been Done:
1. ✅ Installed `django-allauth` package
2. ✅ Configured Django settings for Google OAuth
3. ✅ Updated URL configuration
4. ✅ Run database migrations

## 📋 What You Need to Do:

### 1. Get Google OAuth Credentials (5-10 minutes)

Go to [Google Cloud Console](https://console.cloud.google.com/) and:
- Create OAuth 2.0 credentials
- Add authorized redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`
- Get your Client ID and Client Secret

**Important:** The redirect URI must be EXACTLY as shown above.

See detailed steps in `GOOGLE_OAUTH_SETUP.md` or `FIX_GOOGLE_AUTH.md`

### 2. Configure in Django Admin (NOT .env file)

**Note:** Django Allauth stores credentials in the database, not .env file.

You don't need to add anything to the .env file for Google OAuth!

### 3. Configure in Django Admin

1. Start the server:
   ```bash
   python manage.py runserver
   ```

2. Go to http://127.0.0.1:8000/admin/

3. Update the Site:
   - Navigate to **Sites**
   - Click on "example.com"
   - Change Domain name to: `127.0.0.1:8000`
   - Change Display name to: `AI Quiz Hub`
   - Save

4. Add Social Application:
   - Navigate to **Social applications** → **Add**
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client id: (paste from .env)
   - Secret key: (paste from .env)
   - Sites: Move `127.0.0.1:8000` to "Chosen sites"
   - Save

### 4. Test It!

1. Go to http://127.0.0.1:8000/accounts/login/
2. Click "Continue with Google"
3. Sign in with your Google account
4. You'll be redirected back to the dashboard

## 🔧 Technical Details

The Google Sign-In button is already present in:
- `accounts/templates/accounts/login.html`
- `accounts/templates/accounts/register.html`

The button URL: `/accounts/google/login/?process=login`

This is handled by django-allauth, which:
- Redirects to Google for authentication
- Handles the OAuth2 flow
- Creates/updates user accounts automatically
- Manages email verification (currently optional)

## 🛡️ Security Notes

- **NEVER** commit your `.env` file
- The `.env` file is already in `.gitignore`
- Use `.env.example` as a template for other developers
- For production, use environment variables, not .env file

## 📚 Additional Resources

- Full setup guide: `GOOGLE_OAUTH_SETUP.md`
- Django Allauth docs: https://docs.allauth.org/
- Google OAuth docs: https://developers.google.com/identity/protocols/oauth2

## ❓ Having Issues?

Check the Troubleshooting section in `GOOGLE_OAUTH_SETUP.md`

Common issues:
- `redirect_uri_mismatch`: Check redirect URI in Google Console
- `400 Bad Request`: Configure Site in Django admin
- Module not found: Run `pip install -r requirements.txt`
