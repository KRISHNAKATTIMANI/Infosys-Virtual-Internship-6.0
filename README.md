
<p align="center">
  <img src="assets/progress.gif" width="120" alt="Work in progress animation" />
</p>

<p align="center">
  <b>🚧 Work in Progress — More Features Coming Soon 🚧</b>
</p>

---

# AI Quiz Hub

A Django-based quiz platform with authentication, Google OAuth, AI-powered quiz generation, password reset, quiz attempts tracking, and a modern dashboard UI.

---

## 🔐 Environment Variables & API Configuration (MANDATORY)

This project relies on **Google OAuth**, **OpenAI**, **email services**, and **secure Django settings**.

⚠️ **The project will NOT run correctly without these variables.**

---

### 0️⃣ Create `.env` File

Create a file named **`.env`** in the **root directory** (same level as `manage.py`).

```env
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Django
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_DEBUG=True

# Email Configuration
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

---

### 🔑 Environment Variable Explanation

| Variable                     | Purpose                                        |
| ---------------------------- | ---------------------------------------------- |
| `GOOGLE_OAUTH_CLIENT_ID`     | Google OAuth Client ID                         |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth Client Secret                     |
| `DJANGO_SECRET_KEY`          | Django cryptographic secret key                |
| `DJANGO_DEBUG`               | Debug mode (`True` for local development only) |
| `EMAIL_HOST_USER`            | Email used for OTPs & password reset           |
| `EMAIL_HOST_PASSWORD`        | Email app password                             |
| `OPENAI_API_KEY`             | OpenAI API key for AI-based quiz generation    |

---

### 🌐 Google OAuth Setup (Quick Steps)

1. Go to **Google Cloud Console**
2. Create or select a project
3. Enable **OAuth 2.0**
4. Add the following **Authorized Redirect URI**:

   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
5. Copy **Client ID** and **Client Secret** into `.env`

---

### 📧 Email Setup (Gmail Recommended)

1. Enable **2-Step Verification** on your Google account
2. Generate an **App Password**
3. Use:

   * Gmail address → `EMAIL_HOST_USER`
   * App password → `EMAIL_HOST_PASSWORD`

⚠️ **Do NOT use your normal Gmail password**

---

### 🤖 OpenAI API Setup

1. Go to **[https://platform.openai.com/](https://platform.openai.com/)**
2. Create an API key
3. Add it to `.env`:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

This key is used for:

* AI-based quiz/question generation
* Smart evaluation & suggestions (future features)

---

## 🌍 Django Sites Framework Configuration (REQUIRED)

Google OAuth and email links depend on Django’s **Sites Framework**.

---

### 1️⃣ Configure Site Domain & Name

After starting the server **for the first time**:

```bash
python manage.py runserver
```

1. Open Admin Panel:

   ```
   http://127.0.0.1:8000/admin/
   ```
2. Login using superuser credentials
3. Navigate to:

   ```
   Sites → Sites
   ```
4. Edit the existing site:

   * **Domain name:**

     ```
     localhost:8000
     ```
   * **Display name:**

     ```
     AI Quiz Hub
     ```
5. Click **Save**

✅ This step is **CRITICAL** for:

* Google OAuth login
* Password reset emails
* Absolute URL generation

---

## 🔄 Post-Merge Setup Checklist (READ THIS EVERY TIME)

Whenever you **create a feature branch**, test changes, and **merge it back into `main`**, you **must run the steps below** before starting the server.

Skipping any step can cause:

* login failures
* missing categories/data
* migration errors
* pages loading with no data

---

### 2️⃣ Activate Virtual Environment

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install / Update Dependencies

```bash
pip install -r requirements.txt
```

Run this if:

* a new package was added
* `requirements.txt` changed

---

### 4️⃣ Database Migrations (CRITICAL)

```bash
python manage.py makemigrations
python manage.py migrate
```

Required if:

* models were changed
* new tables / fields were added

If skipped, you may see:

```
no such table
column does not exist
```

---

### 5️⃣ Load Required Initial Data (VERY IMPORTANT)

Some features depend on **preloaded JSON fixture data** in the `fixtures/` directory.

If skipped, you may see:

* empty dashboards
* missing categories / subcategories
* quiz generation failures

#### 📁 Available Fixtures

* `categories.json`
* `subcategories.json`
* `concepts.json`
* `initial_data.json`

> Files with `_utf8.json` are backups and usually not required.

#### ✅ Load Required Fixtures

```bash
python manage.py loaddata categories.json subcategories.json concepts.json
```

📌 Run this:

* once per **new database**
* after **database reset**
* after switching databases

---

### 6️⃣ Collect Static Files (When UI Changes)

```bash
python manage.py collectstatic
```

Required if:

* CSS / JS / images were modified
* admin or dashboard UI looks broken

---

### 7️⃣ Create Users (If Database Was Reset)

Create superuser:

```bash
python manage.py createsuperuser
```

Or create users via the registration page.

---

### 8️⃣ Run System Check (Recommended)

```bash
python manage.py check
```

Detects:

* missing settings
* URL misconfigurations
* app loading issues

---

### 9️⃣ Start Development Server

```bash
python manage.py runserver
```

---

## 🧠 Golden Rule (Memorize This)

> **After every merge → migrate → load data → runserver**

---

## 🗂️ Notes

* Database data (users, attempts) is **NOT version-controlled**
* Schema changes are shared via **migrations**
* Required seed data is loaded via **fixtures**
* Never commit:

  * `.env`
  * `db.sqlite3`
  * media uploads
  * credentials

---

## ⚠️ Security Rules (IMPORTANT)

* ❌ Never push `.env` to GitHub
* ❌ Never expose API keys in README
* ✔️ `.env` must be in `.gitignore`
* ✔️ Use environment variables only

---

Happy coding 🚀
**AI Quiz Hub Team**
