from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Avg, Sum
from django.http import JsonResponse

from .forms import RegistrationForm, UserUpdateForm

# ---------------------------
# LANDING PAGE
# ---------------------------
def index(request):
    return render(request, 'core/index.html')


# ---------------------------
# REGISTRATION
# ---------------------------
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages

def register_view(request):
    if request.user.is_authenticated:
        return redirect('quizzes:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            #Authenticate FIRST (sets backend)
            authenticated_user = authenticate(
                request,
                email=user.email,   # use username if not email-based
                password=form.cleaned_data['password1']
            )

            if authenticated_user is not None:
                login(request, authenticated_user)

            messages.success(
                request,
                "Registration successful! Welcome to AI Quiz Hub."
            )
            return redirect('quizzes:dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ---------------------------
# LOGIN VIEW (Custom Redirection)
# ---------------------------
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True    # Prevent logged users from seeing login page

    # override success URL
    def get_success_url(self):
         return reverse_lazy('quizzes:dashboard')

# ---------------------------
# PROFILE PAGE (User model only — no UserProfile)
# ---------------------------
@login_required
def profile_view(request):
    user = request.user
    
    # Import QuizAttempt here to avoid circular imports
    from quizzes.models import QuizAttempt
    
    if request.method == "POST":
        # Handle built-in avatar selection
        builtin_avatar = request.POST.get("builtin_avatar")
        if builtin_avatar:
            # Clear custom avatar and use the built-in one
            user.avatar_path = builtin_avatar
            user.save()
            return JsonResponse({'success': True, 'message': 'Avatar updated successfully'})
        
        if "avatar_path" in request.FILES:
            user.avatar_path = request.FILES["avatar_path"]

        user.email = request.POST.get("email", user.email)
        user.full_name = request.POST.get("full_name", user.full_name)

        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("accounts:profile")
    
    # Get user statistics
    completed_quizzes = QuizAttempt.objects.filter(
        user=user, 
        status=QuizAttempt.STATUS_COMPLETED
    )
    
    quizzes_taken = completed_quizzes.count()
    avg_score = completed_quizzes.aggregate(avg=Avg('score'))['avg'] or 0
    
    # Calculate total time spent (in seconds, convert to hours)
    total_time = completed_quizzes.aggregate(total=Sum('time_spent_seconds'))['total'] or 0
    time_spent_hours = round(total_time / 3600, 1)
    
    # Calculate current streak (consecutive days with completed quizzes)
    current_streak = 0
    # Simplified streak - just count recent quizzes for now
    
    context = {
        'quizzes_taken': quizzes_taken,
        'avg_score': round(avg_score, 1),
        'current_streak': current_streak,
        'time_spent': time_spent_hours,
    }

    return render(request, "accounts/profile.html", context)



# ---------------------------
# LOGOUT
# ---------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')
