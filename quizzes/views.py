from .models import AttemptQuestion
from django.db.models import Count, Q
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Sum, Count, Q
from django.db.models.functions import Coalesce, TruncDate
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime
import random
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Category, SubCategory, QuizAttempt, Question, Concept, Feedback

# for performance pdf functionality
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# AI Feedback recommendation
from .ai_feedback_service import generate_ai_feedback

#============================================================
# USER DASHBOARD
# ============================================================
@login_required
def dashboard(request):
    user = request.user

    # Base queryset: only completed quizzes
    completed_qs = QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_COMPLETED
    )

    total_attempted = QuizAttempt.objects.filter(user=user).count()
    total_completed = completed_qs.count()

    completion_rate = (
        (total_completed / total_attempted) * 100
        if total_attempted > 0 else 0
    )

    score_stats = completed_qs.aggregate(
        avg_score=Coalesce(Avg('score'), 0.0),
        best_score=Coalesce(Max('score'), 0.0),
        worst_score=Coalesce(Min('score'), 0.0),
    )

    difficulty_stats = completed_qs.values('difficulty').annotate(
        quizzes=Count('id'),
        avg_score=Avg('score')
    ).order_by('difficulty')

    category_stats = completed_qs.values(
        'category__name'
    ).annotate(
        quizzes=Count('id'),
        avg_score=Avg('score')
    ).order_by('-avg_score')

    recent_quizzes = completed_qs.select_related(
        'category', 'subcategory'
    ).order_by('-completed_at')[:10]

    last_7_days = completed_qs.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # ===== DATA FOR CHARTS (Past 30 Days) =====
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Daily quiz activity (quizzes completed per day)
    daily_activity = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('completed_at')
    ).values('date').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    ).order_by('date')
    
    # Prepare data for chart - fill in missing days with 0
    activity_dict = {item['date']: {'count': item['count'], 'avg_score': round(item['avg_score'] or 0, 1)} for item in daily_activity}
    
    chart_labels = []
    chart_quiz_counts = []
    chart_scores = []
    
    for i in range(30):
        date = (timezone.now() - timedelta(days=29-i)).date()
        chart_labels.append(date.strftime('%b %d'))
        data = activity_dict.get(date, {'count': 0, 'avg_score': 0})
        chart_quiz_counts.append(data['count'])
        chart_scores.append(data['avg_score'])
    
    # Category distribution for pie chart
    category_distribution = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    category_labels = [item['category__name'] or 'Unknown' for item in category_distribution]
    category_counts = [item['count'] for item in category_distribution]
    
    # Difficulty distribution
    difficulty_distribution = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).values('difficulty').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    ).order_by('difficulty')
    
    difficulty_labels = [item['difficulty'].capitalize() for item in difficulty_distribution]
    difficulty_counts = [item['count'] for item in difficulty_distribution]
    difficulty_scores = [round(item['avg_score'] or 0, 1) for item in difficulty_distribution]

    context = {
        "total_attempted": total_attempted,
        "total_completed": total_completed,
        "completion_rate": round(completion_rate, 2),

        "avg_score": round(score_stats["avg_score"], 2),
        "best_score": score_stats["best_score"],
        "worst_score": score_stats["worst_score"],

        "difficulty_stats": difficulty_stats,
        "category_stats": category_stats,
        "recent_quizzes": recent_quizzes,

        "last_7_days": last_7_days,
        
        # Chart data (JSON serialized for JavaScript)
        "chart_labels": json.dumps(chart_labels),
        "chart_quiz_counts": json.dumps(chart_quiz_counts),
        "chart_scores": json.dumps(chart_scores),
        "category_labels": json.dumps(category_labels),
        "category_counts": json.dumps(category_counts),
        "difficulty_labels": json.dumps(difficulty_labels),
        "difficulty_counts": json.dumps(difficulty_counts),
        "difficulty_scores": json.dumps(difficulty_scores),
    }
    return render(request, "quizzes/dashboard.html", context)


# ============================================================
# DASHBOARD CHARTS API - For Dynamic Updates
# ============================================================
@login_required
def dashboard_charts_api(request):
    """
    API endpoint to fetch chart data for dashboard.
    Returns JSON data for charts that update after quiz completion.
    """
    user = request.user
    
    # Base queryset: only completed quizzes
    completed_qs = QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_COMPLETED
    )
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Daily quiz activity (quizzes completed per day)
    daily_activity = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('completed_at')
    ).values('date').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    ).order_by('date')
    
    # Prepare data for chart - fill in missing days with 0
    activity_dict = {item['date']: {'count': item['count'], 'avg_score': round(item['avg_score'] or 0, 1)} for item in daily_activity}
    
    chart_labels = []
    chart_quiz_counts = []
    chart_scores = []
    
    for i in range(30):
        date = (timezone.now() - timedelta(days=29-i)).date()
        chart_labels.append(date.strftime('%b %d'))
        data = activity_dict.get(date, {'count': 0, 'avg_score': 0})
        chart_quiz_counts.append(data['count'])
        chart_scores.append(data['avg_score'])
    
    # Category distribution for pie chart
    category_distribution = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    category_labels = [item['category__name'] or 'Unknown' for item in category_distribution]
    category_counts = [item['count'] for item in category_distribution]
    
    # Difficulty distribution
    difficulty_distribution = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).values('difficulty').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    ).order_by('difficulty')
    
    difficulty_labels = [item['difficulty'].capitalize() for item in difficulty_distribution]
    difficulty_counts = [item['count'] for item in difficulty_distribution]
    difficulty_scores = [round(item['avg_score'] or 0, 1) for item in difficulty_distribution]
    
    # Summary stats
    total_completed = completed_qs.count()
    total_30_days = completed_qs.filter(completed_at__gte=thirty_days_ago).count()
    avg_score_30_days = completed_qs.filter(
        completed_at__gte=thirty_days_ago
    ).aggregate(avg=Avg('score'))['avg'] or 0
    
    return JsonResponse({
        'success': True,
        'chart_labels': chart_labels,
        'chart_quiz_counts': chart_quiz_counts,
        'chart_scores': chart_scores,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'difficulty_labels': difficulty_labels,
        'difficulty_counts': difficulty_counts,
        'difficulty_scores': difficulty_scores,
        'summary': {
            'total_completed': total_completed,
            'total_30_days': total_30_days,
            'avg_score_30_days': round(avg_score_30_days, 1),
        }
    })


# ============================================================
# STEP 4 — INSTRUCTIONS BEFORE START
# ============================================================
def instructions(request, subcategory_id, difficulty):
    """
    Show user instructions, selected difficulty & start button.
    """
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # If the selected subcategory is not leaf, redirect user to children list to pick a leaf.
    if not subcategory.is_leaf:
        children = SubCategory.objects.filter(parent_subcat=subcategory)
        if children.exists():
            return redirect('quizzes:subcategory_children', sub_id=subcategory.id)

    return render(request, "quizzes/step_instructions.html", {
        "subcategory": subcategory,
        "difficulty": difficulty
    })

# ============================================================
# START QUIZ — only allowed for leaf nodes and logged-in users
# ============================================================

def pre_start_quiz(request):
    """
    Entry point before the quiz navigation
    """
    active_quiz=QuizAttempt.objects.filter(user=request.user,status__in=[QuizAttempt.STATUS_IN_PROGRESS,QuizAttempt.STATUS_GENERATING],completed_at__isnull=True).first()

    if active_quiz:
        return redirect('quizzes:resume_quiz_prompt',attempt_id=active_quiz.id)
    
    # No active quiz-> allow navigation
    return redirect('quizzes:quiz_selector')


@login_required
def start_quiz(request, subcategory_id, difficulty):
    """
    Create quiz attempt and show loading page
    """
    active_quiz=get_active_quiz(request.user)

    if active_quiz:
        return redirect('quizzes:resume_quiz_prompt',attempt_id=active_quiz.id)
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    
    # Safety: only leaf nodes should start a quiz
    if not subcategory.is_leaf:
        return redirect('quizzes:subcategory_children', sub_id=subcategory.id)
    
    # Create quiz attempt
    quiz_attempt = QuizAttempt.objects.create(
        user=request.user,
        category=subcategory.category,
        subcategory=subcategory,
        difficulty=difficulty,
        total_questions=10,
        status=QuizAttempt.STATUS_GENERATING,
        started_at=timezone.now()  # Add this line
    )
    
    # Show loading page that will trigger AJAX to generate questions
    return render(request, "quizzes/generating_quiz.html", {
        "quiz_attempt": quiz_attempt,
        "subcategory": subcategory,
        "difficulty": difficulty,
    })


# get active quiz function
def get_active_quiz(user):
    return QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_IN_PROGRESS,
        completed_at__isnull=True
    ).order_by('-started_at').first()


# If user is reumes quiz
# RESUME / QUIT PROMPT VIEW
@login_required
def resume_quiz_prompt(request,attempt_id):
    quiz_attempt=get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    if quiz_attempt.status != QuizAttempt.STATUS_IN_PROGRESS:
        return redirect(
            'quizzes:quiz_results',
            attempt_id=quiz_attempt.id
        )

    return render(request,'quizzes/resume_prompt.html',{
        'quiz':quiz_attempt
    })

# RESUME ACITON
@login_required
def resume_quiz(request, attempt_id):
    """
    Resume quiz - RESUME the timer from where it was paused
    """
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    # Clear the paused_at to indicate quiz is active again
    quiz_attempt.paused_at = None
   
    quiz_attempt.save(update_fields=['paused_at'])

    return redirect(
        'quizzes:show_question',
        attempt_id=quiz_attempt.id
    )

@login_required
def previous_question(request, attempt_id):
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    # Move back only if possible
    if quiz_attempt.current_question_index > 0:
        quiz_attempt.current_question_index -= 1
        quiz_attempt.save(update_fields=['current_question_index'])

    return redirect(
        'quizzes:show_question',
        attempt_id=quiz_attempt.id
    )

# QUIT & END ACTION 
@login_required
def quit_quiz(request, attempt_id):
    """
    Quit & End quiz - PAUSE the timer
    """
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    # Calculate time spent so far and add to accumulated time
    if quiz_attempt.started_at and not quiz_attempt.paused_at:
        time_spent = int((timezone.now() - quiz_attempt.started_at).total_seconds())
        quiz_attempt.time_spent_seconds += time_spent
    
    # Mark when quiz was paused
    quiz_attempt.paused_at = timezone.now()
    
    quiz_attempt.status = QuizAttempt.STATUS_ABANDONED
    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.save(update_fields=['time_spent_seconds', 'paused_at', 'status', 'completed_at'])

    return redirect('quizzes:dashboard')

# shuffle correct options
def shuffle_mcq(question_dict):
    """
    Shuffles MCQ options while keeping correct_answer accurate
    """

    options = [
        ('A', question_dict['option_a']),
        ('B', question_dict['option_b']),
        ('C', question_dict['option_c']),
        ('D', question_dict['option_d']),
    ]

    correct_text = dict(options)[question_dict['correct_answer']]

    random.shuffle(options)

    new_correct = None
    for idx, (_, text) in enumerate(options):
        letter = chr(ord('A') + idx)
        question_dict[f'option_{letter.lower()}'] = text
        if text == correct_text:
            new_correct = letter

    question_dict['correct_answer'] = new_correct
    return question_dict

@login_required
@require_POST
def generate_questions(request, attempt_id):
    """
    AJAX endpoint to generate questions using AI
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    # Check if questions already generated
    if quiz_attempt.questions:
        return JsonResponse({
            'success': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
        })

    try:
        from .ai_service import generate_quiz_questions
        from .models import Question, Concept
        import random
        from datetime import timedelta

        REQUIRED_QUESTIONS = quiz_attempt.total_questions  # usually 10
        MAX_RETRIES = 3
        
        formatted_questions = []
        question_id = 1
        
        # ============================================
        # STEP 1: Get questions user has seen recently (last 7 days)
        # ============================================
        recent_attempts = QuizAttempt.objects.filter(
            user=request.user,
            subcategory=quiz_attempt.subcategory,
            status=QuizAttempt.STATUS_COMPLETED,
            completed_at__gte=timezone.now() - timedelta(days=7)
        )
        
        # Collect question hashes the user has seen
        seen_question_texts = set()
        for attempt in recent_attempts:
            if attempt.questions:
                for q in attempt.questions:
                    seen_question_texts.add(q.get('question', ''))
        
        # ============================================
        # STEP 2: Try to use existing questions from DB that user hasn't seen
        # ============================================
        existing_questions = Question.objects.filter(
            subcategory=quiz_attempt.subcategory,
            difficulty=quiz_attempt.difficulty
        ).order_by('?')  # Random order
        
        # Filter out questions user has seen recently
        unseen_questions = [
            q for q in existing_questions 
            if q.question_text not in seen_question_texts
        ]
        
        # Use up to REQUIRED_QUESTIONS from existing pool
        for q in unseen_questions[:REQUIRED_QUESTIONS]:
            
            question_data = {
                "id": question_id,
                "question": q.question_text,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "user_answer": None,
                "is_correct": None
            }

            question_data = shuffle_mcq(question_data)
            formatted_questions.append(question_data)

            # Update usage count
            q.usage_count += 1
            q.save(update_fields=['usage_count'])
            question_id += 1
        
        # ============================================
        # STEP 3: Generate NEW questions if we don't have enough
        # ============================================
        if len(formatted_questions) < REQUIRED_QUESTIONS:
            questions_needed = REQUIRED_QUESTIONS - len(formatted_questions)
            retry_count = 0
            
            while len(formatted_questions) < REQUIRED_QUESTIONS and retry_count < MAX_RETRIES:
                retry_count += 1
                
                # Fetch concepts
                concepts_qs = Concept.objects.filter(
                    subcategory=quiz_attempt.subcategory,
                    difficulty=quiz_attempt.difficulty
                )
                concept_names = list(concepts_qs.values_list('name', flat=True))
                
                if len(concept_names) < questions_needed:
                    break  # Not enough concepts, use what we have
                
                # Pick random concepts for new questions
                selected_concepts = random.sample(concept_names, min(questions_needed, len(concept_names)))
                
                # Generate with AI
                questions_data = generate_quiz_questions(
                    topic=quiz_attempt.subcategory.name,
                    category=quiz_attempt.category.name,
                    difficulty=quiz_attempt.difficulty,
                    count=questions_needed,
                    concepts=selected_concepts
                )
                
                for q in questions_data:
                    if len(formatted_questions) >= REQUIRED_QUESTIONS:
                        break
                    
                    q_hash = Question.make_hash(q["question"])
                    
                    # Skip if this exact question exists OR user has seen it
                    if Question.objects.filter(normalized_hash=q_hash).exists():
                        continue
                    if q["question"] in seen_question_texts:
                        continue
                    
                    # Create new question in DB
                    question_obj = Question.objects.create(
                        category=quiz_attempt.category,
                        subcategory=quiz_attempt.subcategory,
                        difficulty=quiz_attempt.difficulty,
                        question_text=q["question"],
                        option_a=q["option_a"],
                        option_b=q["option_b"],
                        option_c=q["option_c"],
                        option_d=q["option_d"],
                        correct_answer=q["correct_answer"],
                        explanation=q.get("explanation", ""),
                        normalized_hash=q_hash,
                        usage_count=1
                    )
                    
                    question_data = {
                        "id": question_id,
                        "question": question_obj.question_text,
                        "option_a": question_obj.option_a,
                        "option_b": question_obj.option_b,
                        "option_c": question_obj.option_c,
                        "option_d": question_obj.option_d,
                        "correct_answer": question_obj.correct_answer,
                        "explanation": question_obj.explanation,
                        "user_answer": None,
                        "is_correct": None
                    }

                    question_data = shuffle_mcq(question_data)
                    formatted_questions.append(question_data)

                    question_id += 1
        
        # ============================================
        # STEP 4: Check if we have enough questions
        # ============================================
        if len(formatted_questions) < REQUIRED_QUESTIONS:
            quiz_attempt.status = QuizAttempt.STATUS_ABANDONED
            quiz_attempt.save()
            return JsonResponse({
                'success': False,
                'error': f'Could not generate enough unique questions. Got {len(formatted_questions)}/{REQUIRED_QUESTIONS}. Try again later.'
            }, status=500)
        
        # Shuffle to mix existing and new questions
        random.shuffle(formatted_questions)
        
        # Re-number after shuffle
        for i, q in enumerate(formatted_questions):
            q['id'] = i + 1
        
        # ============================================
        # STEP 5: Save and return
        # ============================================
        quiz_attempt.questions = formatted_questions
        quiz_attempt.status = QuizAttempt.STATUS_IN_PROGRESS
        quiz_attempt.ai_meta = {
            'model': 'gpt-3.5-turbo',
            'generated_at': timezone.now().isoformat(),
            'existing_used': sum(1 for q in formatted_questions if q.get('id')),
            'newly_generated': REQUIRED_QUESTIONS - sum(1 for q in formatted_questions if q.get('id'))
        }
        quiz_attempt.save(update_fields=['questions', 'status', 'ai_meta'])

        # ============================
        # CREATE AttemptQuestion ROWS
        # ============================
        AttemptQuestion.objects.filter(attempt=quiz_attempt).delete()

        for idx, q in enumerate(formatted_questions):
            question_obj = Question.objects.filter(
                question_text=q["question"],
                subcategory=quiz_attempt.subcategory
            ).first()

            if not question_obj:
                continue

            AttemptQuestion.objects.create(
                attempt=quiz_attempt,
                question=question_obj,
                question_order=idx,
                status=AttemptQuestion.STATUS_UNVISITED
            )

        return JsonResponse({
            'success': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
        })

    except Exception as e:
        quiz_attempt.status = QuizAttempt.STATUS_ABANDONED
        quiz_attempt.save()

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def show_question(request, attempt_id):
    """
    Show current question in the quiz
    """
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user
    )

    # If quiz already completed → results
    if quiz_attempt.status == QuizAttempt.STATUS_COMPLETED:
        return redirect(
            'quizzes:quiz_results',
            attempt_id=quiz_attempt.id
        )

    # ADD: Fetch AttemptQuestion
    attempt_questions = quiz_attempt.attempt_questions.all()
    current_aq = attempt_questions.filter(
        question_order=quiz_attempt.current_question_index
    ).first()

    # Mark VISITED automatically
    if current_aq and current_aq.visited_at is None:
        current_aq.visited_at = timezone.now()
        current_aq.save(update_fields=['visited_at'])

    # Get current question
    current_question = quiz_attempt.get_current_question()
    if not current_question:
        return redirect(
            'quizzes:quiz_results',
            attempt_id=quiz_attempt.id
        )

    # Preserve previously selected answer
    current_idx = quiz_attempt.current_question_index
    user_answer = None
    if current_idx < len(quiz_attempt.questions):
        user_answer = quiz_attempt.questions[current_idx].get('user_answer')

    current_question_with_answer = dict(current_question)
    current_question_with_answer['user_answer'] = user_answer

    # Progress
    answered_count = sum(
        1 for q in quiz_attempt.questions
        if q.get('user_answer') is not None
    )

    # ✅ SINGLE SOURCE OF TRUTH FOR TIMER
    remaining_seconds = (
        quiz_attempt.remaining_seconds
        if quiz_attempt.remaining_seconds is not None
        else quiz_attempt.time_limit_seconds
    )

    return render(request, "quizzes/quiz_question.html", {
        "quiz_attempt": quiz_attempt,
        "question": current_question_with_answer,
        "question_number": quiz_attempt.current_question_index + 1,
        "total_questions": quiz_attempt.total_questions,
        "answered_count": answered_count,
        "has_prev": quiz_attempt.current_question_index > 0,
        "remaining_seconds": remaining_seconds,
        "attempt_questions": attempt_questions,
        "current_status": current_aq.status if current_aq else None,
    })



@login_required
@require_POST
def submit_answer(request, attempt_id):
    """
    Submit answer for current question
    """

    

    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if quiz_attempt.is_auto_submitted:
        return JsonResponse({
            "success": False,
            "redirect_url": f"/quiz/attempt/{quiz_attempt.id}/results/?auto_submitted=true"
        })

    # Get user's answer
    user_answer = request.POST.get('answer', '').upper()

    if user_answer not in ['A', 'B', 'C', 'D']:
        return JsonResponse({'error': 'Invalid answer'}, status=400)
    
    # ADD DB UPDATE
    current_idx = quiz_attempt.current_question_index

    aq = AttemptQuestion.objects.filter(
        attempt=quiz_attempt,
        question_order=current_idx
    ).first()

    if not aq:
        return JsonResponse({'error': 'Question state not found'}, status=400)

    aq.selected_option = user_answer
    aq.status = AttemptQuestion.STATUS_SOLVED
    aq.answered_at = timezone.now()
    aq.is_correct = (
        user_answer == quiz_attempt.questions[current_idx]['correct_answer']
    )

    aq.save(update_fields=[
        'selected_option',
        'status',
        'answered_at',
        'is_correct'
    ])
    
    if current_idx >= len(quiz_attempt.questions):
        return JsonResponse({'error': 'No more questions'}, status=400)
    
    # Update question with user's answer
    quiz_attempt.questions[current_idx]['user_answer'] = user_answer
    quiz_attempt.questions[current_idx]['is_correct'] = (
        user_answer == quiz_attempt.questions[current_idx]['correct_answer']
    )
    
    # Move to next question
    quiz_attempt.current_question_index += 1

    # Persist only the changed fields to ensure JSONField is saved
    quiz_attempt.save(update_fields=['questions', 'current_question_index'])
    
    # Check if quiz is complete
    if quiz_attempt.is_quiz_complete():
        finalize_quiz_attempt(quiz_attempt)

        return JsonResponse({
            'success': True,
            'completed': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/results/'
        })

    
    return JsonResponse({
        'success': True,
        'completed': False,
        'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
    })

@login_required
@require_POST
def auto_submit_quiz(request, attempt_id):
    """
    Auto-submit quiz when timer expires
    Marks all unanswered questions as attempted but incorrect
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    quiz_attempt.is_auto_submitted = True
    quiz_attempt.auto_submit_reason = QuizAttempt.AUTO_SUBMIT_TIME_UP
    quiz_attempt.save(update_fields=[
        'is_auto_submitted',
        'auto_submit_reason'
    ])

    # Mark quiz as completed
    finalize_quiz_attempt(quiz_attempt)
    
    return redirect(
        'quizzes:quiz_results',
        attempt_id=quiz_attempt.id
    )

@login_required
def quiz_results(request, attempt_id):
    """
    Show quiz results with score and review
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Calculate results
    total = len(quiz_attempt.questions) if quiz_attempt.questions else 0
    correct = sum(1 for q in quiz_attempt.questions if q.get('is_correct')) if quiz_attempt.questions else 0
    incorrect = total - correct
    percentage = round((correct * 100) / total, 2) if total else 0

    
    # Determine grade
    if percentage >= 90:
        grade = 'A+'
    elif percentage >= 80:
        grade = 'A'
    elif percentage >= 70:
        grade = 'B'
    elif percentage >= 60:
        grade = 'C'
    else:
        grade = 'F'
    
    # Check if this was an auto-submit
    auto_submitted = request.GET.get('auto_submitted') == 'true'
    
    # Generate AI Feedback
    ai_feedback = None
    strong_areas = []
    weak_areas = []
    
    try:
        # Analyze questions for strong/weak areas
        questions = quiz_attempt.questions or []
        
        for q in questions:
            topic = q.get('topic', quiz_attempt.subcategory.name)
            if q.get('is_correct'):
                if topic not in strong_areas:
                    strong_areas.append(topic)
            else:
                if topic not in weak_areas:
                    weak_areas.append(topic)
        
        # Remove overlaps - if in both, keep in weak
        strong_areas = [a for a in strong_areas if a not in weak_areas]
        
        # Generate AI feedback
        summary_data = {
            "subcategory": quiz_attempt.subcategory.name,
            "category": quiz_attempt.category.name,
            "difficulty": quiz_attempt.difficulty,
            "score": percentage,
            "correct": correct,
            "total": total,
            "strong_areas": strong_areas[:3],
            "weak_areas": weak_areas[:3],
        }
        
        ai_feedback = generate_ai_feedback(str(summary_data))
    except Exception as e:
        print(f"AI Feedback error: {e}")
        ai_feedback = None
    
    # Check if user already submitted feedback for this quiz
    existing_feedback = Feedback.objects.filter(quiz_attempt=quiz_attempt).first()
    
    return render(request, "quizzes/quiz_results.html", {
        "quiz_attempt": quiz_attempt,
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "percentage": percentage,
        "grade": grade,
        "auto_submitted": auto_submitted,
        "ai_feedback": ai_feedback,
        "strong_areas": strong_areas[:3],
        "weak_areas": weak_areas[:3],
        "existing_feedback": existing_feedback,
    })

def finalize_quiz_attempt(quiz_attempt):
    aq_qs = AttemptQuestion.objects.filter(attempt=quiz_attempt)

    attempted = aq_qs.filter(selected_option__isnull=False).count()
    correct = aq_qs.filter(is_correct=True).count()

    quiz_attempt.attempted_questions = attempted
    quiz_attempt.correct_answers = correct

    quiz_attempt.score = (
        round((correct * 100) / quiz_attempt.total_questions, 2)
        if quiz_attempt.total_questions > 0 else 0
    )

    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.status = QuizAttempt.STATUS_COMPLETED
    quiz_attempt.paused_at = None

    # Time calc
    if quiz_attempt.started_at:
        quiz_attempt.time_taken_seconds = int(
            (timezone.now() - quiz_attempt.started_at).total_seconds()
        )
    else:
        quiz_attempt.time_taken_seconds = 0

    quiz_attempt.time_spent_seconds = quiz_attempt.time_taken_seconds

    quiz_attempt.save(update_fields=[
        'attempted_questions',
        'correct_answers',
        'score',
        'time_taken_seconds',
        'time_spent_seconds',
        'completed_at',
        'status',
        'paused_at'
    ])



# streak
def calculate_streak(user):
    """
    Calculate consecutive-day quiz streak for a user.
    """
    streak = 0
    today = timezone.now().date()

    while True:
        # Calculate the date we are checking
        check_date = today - timedelta(days=streak)

        # Start & end time of that day
        day_start = timezone.make_aware(
            datetime.combine(check_date, datetime.min.time())
        )
        day_end = timezone.make_aware(
            datetime.combine(check_date, datetime.max.time())
        )

        # Check if user attempted any quiz on that day
        attempted = QuizAttempt.objects.filter(
            user=user,
            started_at__range=(day_start, day_end)
        ).exists()

        if attempted:
            streak += 1
        else:
            break

    return streak

# Performance Analysis and AI-Feedback 
@login_required
def performance_dashboard(request):
    request.session.pop("ai_feedback", None)

    user = request.user

    completed_qs = QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_COMPLETED
    )

    # ---------------------------
    # 1. OVERALL STATS
    # ---------------------------
    overall = completed_qs.aggregate(
        total_quizzes=Count('id'),
        avg_score=Avg('score'),          
        total_correct=Sum('correct_answers'),
        total_attempted=Sum('attempted_questions'),
        total_time=Sum('time_taken_seconds')
    )

    overall_accuracy = (
        (overall['total_correct'] / overall['total_attempted']) * 100
        if overall['total_attempted']
        else 0
    )

    avg_time_per_question = (
        overall['total_time'] / overall['total_attempted']
        if overall['total_attempted']
        else 0
    )

    # ---------------------------
    # 2. CATEGORY-WISE DISTRIBUTION
    # ---------------------------
    category_distribution = (
        completed_qs
        .exclude(category__isnull=True)
        .values('category__name')        
        .annotate(quiz_count=Count('id'))
        .order_by('-quiz_count')
    )

    # ---------------------------
    # 3. SUBCATEGORY-WISE ACCURACY
    # ---------------------------
    subcategory_stats = (
        completed_qs
        .exclude(subcategory__isnull=True)
        .values('subcategory__name')
        .annotate(
            correct=Sum('correct_answers'),
            attempted=Sum('attempted_questions')
        )
    )

    subcategory_accuracy = []
    for item in subcategory_stats:
        accuracy = (
            (item['correct'] / item['attempted']) * 100
            if item['attempted']
            else 0
        )
        subcategory_accuracy.append({
            'subcategory': item['subcategory__name'],
            'accuracy': round(accuracy, 2)
        })

    # ---------------------------
    # STRONG vs WEAK TOPICS
    # ---------------------------
    strong_topics = []
    weak_topics = []

    for item in subcategory_accuracy:
        if item['accuracy'] >= 75:
            strong_topics.append(item)
        elif item['accuracy'] <= 50:
            weak_topics.append(item)

    # ---------------------------
    # 4. DIFFICULTY-WISE PERFORMANCE
    # ---------------------------
    difficulty_performance = completed_qs.values(
        'difficulty'
    ).annotate(
        avg_score=Avg('score')
    )

    # ---------------------------
    # 5. PERFORMANCE OVER TIME
    # ---------------------------
    performance_over_time = (
        completed_qs
        .exclude(completed_at__isnull=True)
        .annotate(date=TruncDate('completed_at'))
        .values('date')
        .annotate(avg_score=Avg('score'))
        .order_by('date')
    )

    # ---------------------------
    # 6. INSIGHTS
    # ---------------------------
    insights = []

    if overall_accuracy >= 80:
        insights.append("Excellent accuracy! You have strong conceptual clarity.")
    elif overall_accuracy >= 60:
        insights.append("Good accuracy. Focus on weaker topics to improve further.")
    else:
        insights.append("Accuracy is low. Try revising concepts before attempting quizzes.")

    if avg_time_per_question < 30:
        insights.append("You answer quickly. Ensure accuracy is not affected.")
    else:
        insights.append("You take time to answer. Accuracy is more important than speed.")

    # ---------------------------
    # 7. AI-GENERATED FEEDBACK 
    # ---------------------------
    total_quizzes = overall['total_quizzes'] or 0

    if total_quizzes == 0:
        ai_feedback = (
            "You haven’t attempted any quizzes yet. 🚀 "
            "Start your first quiz to receive personalized AI-powered feedback!"
        )
    else:
        difficulty_map = {
            d['difficulty']: round(d['avg_score'] or 0, 2)
            for d in difficulty_performance
        }
        weak_concepts = []

        for wt in weak_topics:
            concepts = Concept.objects.filter(
                subcategory__name=wt['subcategory']
            ).values_list('name', flat=True)

            weak_concepts.extend(list(concepts[:5]))  # limit per topic
        ai_summary = {
            "overall_accuracy": round(overall_accuracy, 2),
            "avg_time_per_question": round(avg_time_per_question, 2),
            "difficulty_performance": difficulty_map,
            "strong_topics": [t['subcategory'] for t in strong_topics],
            "weak_topics": [t['subcategory'] for t in weak_topics],
            "weak_concepts": weak_concepts,
        }

        if not request.session.get("ai_feedback"):
            try:
                request.session["ai_feedback"] = generate_ai_feedback(ai_summary)
            except Exception:
                request.session["ai_feedback"] = (
                    "Your performance data is being analyzed. "
                    "Keep practicing regularly to strengthen your understanding."
                )

        ai_feedback = request.session["ai_feedback"]

    # streak
    streak = calculate_streak(request.user)

    # ---------------------------
    # FINAL CONTEXT
    # ---------------------------
    context = {
        'total_quizzes': total_quizzes or 0,
        'avg_score': round(overall['avg_score'] or 0, 2),
        'overall_accuracy': round(overall_accuracy, 2),
        'avg_time_per_question': round(avg_time_per_question, 2),

        'category_distribution': list(category_distribution),
        'subcategory_accuracy': subcategory_accuracy,
        'difficulty_performance': list(difficulty_performance),
        'performance_over_time': list(performance_over_time),

        'insights': insights,
        'strong_topics': strong_topics,
        'weak_topics': weak_topics,
        'ai_feedback': ai_feedback,
        'streak':streak,
    }

    return render(request, 'quizzes/performance_dashboard.html', context)

def draw_page_layout(canvas, doc):
    canvas.saveState()

    # Page border
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(1)
    canvas.rect(20, 20, A4[0] - 40, A4[1] - 40)

    # Header
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, A4[1] - 40, "AI Quiz Hub – Performance Report")

    # Footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(
        A4[0] / 2,
        30,
        f"Page {doc.page}"
    )

    canvas.restoreState()

@login_required
def download_performance_pdf(request):
    user = request.user

    completed_qs = QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_COMPLETED
    )

    overall = completed_qs.aggregate(
        total_quizzes=Count('id'),
        avg_score=Avg('score'),
        total_correct=Sum('correct_answers'),
        total_attempted=Sum('attempted_questions'),
    )

    overall_accuracy = (
        (overall['total_correct'] / overall['total_attempted']) * 100
        if overall['total_attempted'] else 0
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="AI_Quiz_Hub_Performance_Report.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontSize=22,
        alignment=1,
        spaceAfter=14,
        textColor=colors.HexColor("#111827"),
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor("#1f2937"),
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        fontSize=10,
        spaceAfter=6,
        textColor=colors.black
    ))

    styles.add(ParagraphStyle(
        name="MutedText",
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    ))

    elements = []

    # ---------------- HEADER ----------------
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=20,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor("#1f2937")
    )

    subtitle_style = ParagraphStyle(
        name="SubtitleStyle",
        fontSize=12,
        alignment=1,
        spaceAfter=20,
        textColor=colors.grey
    )

    elements.append(Paragraph("AI Quiz Hub", styles["ReportTitle"]))
    elements.append(Paragraph(
        "Personal Performance Report",
        styles["MutedText"]
    ))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"Dear <b>{user.username}</b>,<br/><br/>"
        "This report provides a detailed overview of your quiz performance, "
        "accuracy, and topic-wise strengths. Use this insight to track progress "
        "and identify improvement areas.",
        styles["BodyText"]
    ))


    # ---------------- USER INFO ----------------
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("User Information", styles["SectionTitle"]))

    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"<b>Username:</b> {user.username}", styles['Normal']
    ))
    elements.append(Paragraph(
        f"<b>Generated on:</b> {now().strftime('%d %b %Y')}", styles['Normal']
    ))

    elements.append(Spacer(1, 16))

    # ---------------- SUMMARY ----------------
    elements.append(Paragraph("Performance Summary", styles["SectionTitle"]))

    elements.append(Spacer(1, 8))

    summary_table = Table([
        ["Total Quizzes Attempted", overall['total_quizzes'] or 0],
        ["Average Score", f"{round(overall['avg_score'] or 0, 2)} %"],
        ["Overall Accuracy", f"{round(overall_accuracy, 2)} %"],
    ], colWidths=[250, 150])

    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.8, colors.grey),
        ('FONT', (0,0), (-1,-1), 'Helvetica'),
        ('FONT', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))


    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ---------------- TOPIC TABLE ----------------
    elements.append(Paragraph("Topic-wise Accuracy", styles["SectionTitle"]))

    elements.append(Spacer(1, 8))

    topic_data = [["Topic", "Accuracy (%)"]]

    subcategory_stats = completed_qs.values(
        'subcategory__name'
    ).annotate(
        correct=Sum('correct_answers'),
        attempted=Sum('attempted_questions')
    )

    for item in subcategory_stats:
        if item['attempted']:
            acc = round((item['correct'] / item['attempted']) * 100, 2)
            topic_data.append([item['subcategory__name'], acc])

    topic_table = Table(topic_data, colWidths=[300, 100])
    topic_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e5e7eb")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))

    elements.append(topic_table)

    # ---------------- FOOTER ----------------
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "This report is system-generated and reflects quiz attempts completed on AI Quiz Hub.",
        styles["MutedText"]
    ))


    doc.build(
        elements,
        onFirstPage=draw_page_layout,
        onLaterPages=draw_page_layout
    )

    return response

# RECENT QUIZZES
@login_required
def recent_quizzes_view(request):
    recent_quizzes = (
        QuizAttempt.objects
        .filter(
            user=request.user,
            status=QuizAttempt.STATUS_COMPLETED
        )
        .select_related('subcategory')
        .order_by('-completed_at')[:10]
    )

    return render(request, 'quizzes/recent_quizzes.html', {
        'recent_quizzes': recent_quizzes
    })

@login_required
def attempts_summary_view(request):
    user = request.user

    total_attempts = QuizAttempt.objects.filter(user=user, status__in=[
        QuizAttempt.STATUS_COMPLETED,
        QuizAttempt.STATUS_ABANDONED
    ]).count()

    status_counts = QuizAttempt.objects.filter(user=user).aggregate(
        completed=Count('id', filter=Q(status=QuizAttempt.STATUS_COMPLETED)),
        abandoned=Count('id', filter=Q(status=QuizAttempt.STATUS_ABANDONED)),
    )

    timeup_auto = QuizAttempt.objects.filter(
        user=request.user,
        is_auto_submitted=True,
        auto_submit_reason=QuizAttempt.AUTO_SUBMIT_TIME_UP
    ).count()

    tabswitch_auto = QuizAttempt.objects.filter(
        user=request.user,
        is_auto_submitted=True,
        auto_submit_reason=QuizAttempt.AUTO_SUBMIT_TAB_SWITCH
    ).count()

    # last_7_days_attempts = QuizAttempt.objects.filter(
    #     user=user,
    #     started_at__gte=now() - timedelta(days=7)
    # ).count()

    context = {
        'total_attempts': total_attempts,
        'completed_attempts': status_counts['completed'],
        'abandoned_attempts': status_counts['abandoned'],
        # 'last_7_days_attempts': last_7_days_attempts,
        "timeup_auto": timeup_auto,
        "tabswitch_auto": tabswitch_auto,
    }

    return render(request, 'quizzes/attempts_summary.html', context)

# Leaderboard

@login_required
def leaderboard(request):
    leaderboard_data = (
        QuizAttempt.objects
        .filter(status=QuizAttempt.STATUS_COMPLETED)
        .values('user__username')
        .annotate(
            avg_score=Avg('score'),
            quizzes_attempted=Count('id')
        )
        .filter(quizzes_attempted__gte=1)  # minimum 1 attempt to appear
        .order_by('-avg_score', '-quizzes_attempted')[:20]
    )

    return render(request, 'quizzes/leaderboard.html', {
        'leaderboard': leaderboard_data
    })

@login_required
@require_POST
def save_timer(request, attempt_id):
    try:
        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id,
            user=request.user
        )

        if attempt.status != QuizAttempt.STATUS_IN_PROGRESS:
            return JsonResponse({'status': 'ignored'})

        remaining = request.POST.get('remaining_seconds')
        if remaining is not None:
            attempt.remaining_seconds = int(remaining)

            # ✅ DO NOT calculate time_spent here
            attempt.save(update_fields=['remaining_seconds'])

        return JsonResponse({'status': 'saved'})

    except Exception:
        return JsonResponse({'status': 'error'}, status=400)


# ============================================================
# FEEDBACK SUBMISSION
# ============================================================
@login_required
@require_POST
def submit_feedback(request, attempt_id):
    """
    Submit user feedback after quiz completion (optional).
    Displayed on landing page testimonials.
    """
    try:
        quiz_attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id,
            user=request.user,
            status=QuizAttempt.STATUS_COMPLETED
        )
        
        # Check if feedback already exists
        if Feedback.objects.filter(quiz_attempt=quiz_attempt).exists():
            return JsonResponse({
                'success': False,
                'error': 'Feedback already submitted for this quiz'
            }, status=400)
        
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            return JsonResponse({
                'success': False,
                'error': 'Please provide a comment'
            }, status=400)
        
        if len(comment) > 500:
            return JsonResponse({
                'success': False,
                'error': 'Comment must be under 500 characters'
            }, status=400)
        
        # Create feedback
        feedback = Feedback.objects.create(
            user=request.user,
            quiz_attempt=quiz_attempt,
            rating=int(rating),
            comment=comment,
            is_approved=True  # Auto-approve for now
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    

# tab-switch
@login_required
@require_POST
def tab_violation(request):
    try:
        data = json.loads(request.body)
        attempt_id = data.get("attempt_id")

        if not attempt_id:
            return JsonResponse({"error": "Missing attempt_id"}, status=400)

        attempt = QuizAttempt.objects.get(
            id=attempt_id,
            user=request.user  # 🔐 prevent tampering
        )

        attempt.tab_violations += 1

        if attempt.tab_violations >= 4:
            attempt.is_auto_submitted = True
            attempt.flagged_for_review = True
            attempt.auto_submit_reason = QuizAttempt.AUTO_SUBMIT_TAB_SWITCH

            finalize_quiz_attempt(attempt)

            attempt.is_auto_submitted = True
            attempt.flagged_for_review = True
            attempt.auto_submit_reason = QuizAttempt.AUTO_SUBMIT_TAB_SWITCH

            attempt.save(update_fields=[
                'is_auto_submitted',
                'auto_submit_reason',
                'flagged_for_review'
            ])

            return JsonResponse({
                "status": "auto_submitted"
            })

        attempt.save()
        return JsonResponse({
            "status": "warning",
            "count": attempt.tab_violations
        })

    except QuizAttempt.DoesNotExist:
        return JsonResponse({"error": "Invalid attempt"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# SKIP QUESTION
@login_required
@require_POST
def skip_question(request, attempt_id):
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    current_idx = quiz_attempt.current_question_index

    aq = AttemptQuestion.objects.filter(
        attempt=quiz_attempt,
        question_order=current_idx
    ).first()

    if not aq:
        return JsonResponse({'error': 'Question state not found'}, status=400)


    aq.status = AttemptQuestion.STATUS_SKIPPED
    aq.selected_option = None
    aq.save(update_fields=['status', 'selected_option'])

    quiz_attempt.current_question_index += 1
    quiz_attempt.save(update_fields=['current_question_index'])

    return redirect('quizzes:show_question',attempt_id=quiz_attempt.id)


# MARK FOR REVIEW
@login_required
@require_POST
def mark_for_review(request, attempt_id):
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    current_idx = quiz_attempt.current_question_index

    aq = AttemptQuestion.objects.filter(
        attempt=quiz_attempt,
        question_order=current_idx
    ).first()

    if not aq:
        return JsonResponse({'error': 'Question state not found'}, status=400)

    aq.status = AttemptQuestion.STATUS_REVIEW
    aq.save(update_fields=['status'])

    quiz_attempt.current_question_index += 1
    quiz_attempt.save(update_fields=['current_question_index'])

    return redirect('quizzes:show_question',attempt_id=quiz_attempt.id)


# ADD QUESTION JUMP (Navigation Click)
@login_required
def jump_to_question(request, attempt_id, q_no):
    quiz_attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status=QuizAttempt.STATUS_IN_PROGRESS
    )

    if 0 <= q_no < quiz_attempt.total_questions:
        quiz_attempt.current_question_index = q_no
        quiz_attempt.save(update_fields=['current_question_index'])

    return redirect('quizzes:show_question', attempt_id=attempt_id)
