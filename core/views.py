
# core/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg
from quizzes.models import Feedback, QuizAttempt
from accounts.models import User

def index(request):
    # Get approved testimonials for the landing page
    testimonials = Feedback.objects.filter(
        is_approved=True
    ).select_related('user').order_by('-is_featured', '-rating', '-created_at')[:6]
    
    # Real-time stats from database
    total_users = User.objects.filter(is_active=True).count()
    total_quizzes = QuizAttempt.objects.filter(status=QuizAttempt.STATUS_COMPLETED).count()
    
    # Calculate satisfaction rate from feedback ratings (1-5 scale converted to percentage)
    avg_rating = Feedback.objects.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg']
    satisfaction_rate = int((avg_rating / 5) * 100) if avg_rating else 98  # Default to 98% if no feedback
    
    return render(request, "core/index_new.html", {
        'testimonials': testimonials,
        'total_users': total_users,
        'total_quizzes': total_quizzes,
        'satisfaction_rate': satisfaction_rate,
    })

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:login')

# Custom 404 error handler
def custom_404(request, exception):
    return render(request, '404.html', status=404)
