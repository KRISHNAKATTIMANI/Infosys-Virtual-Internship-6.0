import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from quizzes.models import QuizAttempt
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("QUIZ DATA CHECK")
print("=" * 60)

users = User.objects.all()
print(f"\nTotal users: {users.count()}")

for user in users:
    total = QuizAttempt.objects.filter(user=user).count()
    completed = QuizAttempt.objects.filter(user=user, status=2).count()
    in_progress = QuizAttempt.objects.filter(user=user, status=1).count()
    
    print(f"\nUser: {user.email or user.username}")
    print(f"  Total attempts: {total}")
    print(f"  Completed (status=2): {completed}")
    print(f"  In Progress (status=1): {in_progress}")
    
    if total > 0:
        print(f"  Recent attempts:")
        attempts = QuizAttempt.objects.filter(user=user).order_by('-created_at')[:5]
        for attempt in attempts:
            print(f"    - ID: {str(attempt.id)[:8]}... Status: {attempt.status} ({attempt.get_status_display()})")
            print(f"      Score: {attempt.score}, Completed: {attempt.completed_at}")
            print(f"      Category: {attempt.category.name if attempt.category else 'N/A'}")

print("\n" + "=" * 60)
