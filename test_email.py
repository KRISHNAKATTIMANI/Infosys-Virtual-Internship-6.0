# test_email.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        subject='Test Email',
        message='If you see this, email is working!',
        from_email='aiquizhub1@gmail.com',
        recipient_list=['adityanaik26112005@gmail.com'],  # ← change this
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")