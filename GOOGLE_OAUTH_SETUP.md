# Google OAuth Setup Guide for AI Quiz Hub

This guide will help you set up Google Sign-In authentication for your Django application.

## Step 1: Install Dependencies

First, install the required packages:

```bash
pip install -r requirements.txt
```

## Step 2: Create Google OAuth Credentials

### 2.1 Go to Google Cloud Console
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account

### 2.2 Create a New Project (or select existing)
1. Click on the project dropdown at the top
2. Click "NEW PROJECT"
3. Name it "AI Quiz Hub" (or any name you prefer)
4. Click "CREATE"

### 2.3 Enable Google+ API
1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and click **ENABLE**

### 2.4 Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type
3. Click **CREATE**
4. Fill in the required fields:
   - **App name**: AI Quiz Hub
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **SAVE AND CONTINUE**
6. On the Scopes page, click **SAVE AND CONTINUE**
7. On Test users page (if in testing mode), add your email as a test user
8. Click **SAVE AND CONTINUE**

### 2.5 Create OAuth 2.0 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Choose **Web application**
4. Name it "AI Quiz Hub Web Client"
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
6. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
7. Click **CREATE**
8. **IMPORTANT**: Copy the **Client ID** and **Client Secret** that appear

## Step 3: Configure Environment Variables

### 3.1 Create/Update .env file
In your project root directory (same level as manage.py), create or edit the `.env` file:

```env
# OpenAI API (existing)
OPENAI_API_KEY=your_existing_openai_key_here

# Google OAuth Credentials (add these)
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here

# Django Settings
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
```

Replace:
- `your_client_id_here` with the Client ID from Step 2.5
- `your_client_secret_here` with the Client Secret from Step 2.5

**IMPORTANT**: Never commit the `.env` file to version control!

## Step 4: Run Database Migrations

Django Allauth needs to create tables in your database:

```bash
python manage.py migrate
```

## Step 5: Create Superuser (if not already created)

```bash
python manage.py createsuperuser
```

## Step 6: Configure Social App in Django Admin

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

3. Login with your superuser credentials

4. Navigate to **Sites** and click on "example.com"
   - Change **Domain name** to: `127.0.0.1:8000`
   - Change **Display name** to: `AI Quiz Hub`
   - Click **SAVE**

5. Navigate to **Social applications** → **Add social application**
   - **Provider**: Select "Google"
   - **Name**: Google OAuth
   - **Client id**: Paste your Client ID from Google Console
   - **Secret key**: Paste your Client Secret from Google Console
   - **Sites**: Select "127.0.0.1:8000" and move it to "Chosen sites" using the arrow
   - Click **SAVE**

## Step 7: Test Google Sign-In

1. Make sure your server is running
2. Go to [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
3. Click the "Continue with Google" button
4. You should be redirected to Google's login page
5. Sign in with your Google account
6. After authentication, you'll be redirected back to the application

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure the redirect URI in Google Console exactly matches:
  `http://127.0.0.1:8000/accounts/google/login/callback/`
- Check that you're accessing the site via `127.0.0.1:8000` not `localhost:8000`

### Error: "400 Bad Request"
- Ensure you've configured the Site in Django admin correctly
- Check that the Social Application is properly configured

### Users can't sign in
- If your OAuth consent screen is in "Testing" mode, only test users you've added can sign in
- To allow anyone, publish your app (though this requires verification for production)

### Environment variables not loading
- Make sure `.env` file is in the same directory as `manage.py`
- Restart your development server after changing `.env`

## For Production Deployment

When deploying to production:

1. Update **Authorized JavaScript origins** in Google Console with your production domain:
   ```
   https://yourdomain.com
   ```

2. Update **Authorized redirect URIs**:
   ```
   https://yourdomain.com/accounts/google/login/callback/
   ```

3. Update the Site in Django admin with your production domain

4. Set `DJANGO_DEBUG=False` in your production environment

5. Consider setting `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` in settings.py

6. Publish your OAuth consent screen (requires Google verification)

## Security Notes

- **Never** commit your `.env` file or expose your Client Secret
- Use strong `SECRET_KEY` in production
- Enable HTTPS in production
- Consider rate limiting login attempts
- Regularly rotate your OAuth credentials

## Additional Features You Can Add

1. **Email Verification**: Change `ACCOUNT_EMAIL_VERIFICATION` to `'mandatory'`
2. **Multiple Providers**: Add Facebook, GitHub, etc.
3. **Profile Completion**: Redirect new users to complete profile
4. **Account Linking**: Allow users to link multiple social accounts

---

For more information, visit:
- [Django Allauth Documentation](https://docs.allauth.org/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
