
# core/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from quizzes.models import Feedback

def index(request):
    # Get approved testimonials for the landing page
    testimonials = Feedback.objects.filter(
        is_approved=True
    ).select_related('user').order_by('-is_featured', '-rating', '-created_at')[:6]
    
    return render(request, "core/index_new.html", {
        'testimonials': testimonials
    })

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return redirect('accounts:login')

# Custom 404 error handler
def custom_404(request, exception):
    return render(request, '404.html', status=404)
