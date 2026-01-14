<p align="center">
  <img src="assets/progress.gif" width="120" alt="Work in progress animation" />
</p>

<p align="center">
  <b>🚧 Work in Progress — More Features Coming Soon 🚧</b>
</p>

---

# AI Quiz Hub

A Django-based quiz platform with authentication, password reset, quizzes, attempts tracking, and dashboard UI.

---

## 🔄 Post‑Merge Setup Checklist (READ THIS EVERY TIME)

Whenever you **create a feature branch**, test changes, and **merge it back into `main`**, you **must run the steps below** before starting the server.

Skipping any step can cause:

* login failures
* missing categories/data
* migration errors
* pages loading with no data

---

### 1️⃣ Activate Virtual Environment

```bash
venv\Scripts\activate
```

---

### 2️⃣ Install / Update Dependencies

```bash
pip install -r requirements.txt
```

Run this if:

* a new package was added in another branch
* `requirements.txt` changed

---

### 3️⃣ Database Migrations (CRITICAL)

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

### 4️⃣ Load Required Initial Data (VERY IMPORTANT)

Some features depend on **preloaded JSON fixture data** present in the `fixtures/` directory.

If these are not loaded, you may see:

* empty dashboards
* missing categories / subcategories
* quiz generation failures

#### 📁 Available Fixtures

* `categories.json`
* `subcategories.json`
* `concepts.json`
* `initial_data.json`

> ⚠️ Files with `_utf8.json` are backups / alternate encodings and are **not required** unless explicitly needed.

#### ✅ Recommended: Load ALL required fixtures

```bash
python manage.py loaddata categories.json subcategories.json concepts.json initial_data.json
```

📌 Run this:

* once per **new database**
* after **database reset**
* after switching databases (SQLite ↔ MySQL)

---

### 5️⃣ Collect Static Files (When UI Changes)

```bash
python manage.py collectstatic
```

Required if:

* CSS / JS / images were modified
* admin UI or dashboard styles look broken

---

### 6️⃣ Create Users (If Database Was Reset)

Create admin user:

```bash
python manage.py createsuperuser
```

Or create normal users via the registration page.

---

### 7️⃣ Run System Check (Recommended)

```bash
python manage.py check
```

Catches:

* URL misconfigurations
* missing settings
* app loading issues

---

### 8️⃣ Start Development Server

```bash
python manage.py runserver
```

---

## 🧠 Golden Rule (Memorize This)

> **After every merge → migrate → load data → runserver**

---

## 🗂️ Notes

* Database data (users, attempts) is **NOT** version-controlled
* Schema changes are shared via **migrations**
* Required seed data is loaded via **fixtures (`loaddata`)**
* Never commit `db.sqlite3`, media uploads, or credentials

---

Happy coding 🚀
