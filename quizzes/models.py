# quizzes/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
import hashlib
import re
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=150)
    level = models.SmallIntegerField(default=1)
    parent_subcat = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_leaf = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['category', 'level', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class QuizAttempt(models.Model):

    AUTO_SUBMIT_NONE = 0
    AUTO_SUBMIT_TIME_UP = 1
    AUTO_SUBMIT_TAB_SWITCH = 2

    AUTO_SUBMIT_REASON_CHOICES = [
        (AUTO_SUBMIT_NONE, "None"),
        (AUTO_SUBMIT_TIME_UP, "Time Up"),
        (AUTO_SUBMIT_TAB_SWITCH, "Tab Switch"),
    ]

    auto_submit_reason = models.SmallIntegerField(
        choices=AUTO_SUBMIT_REASON_CHOICES,
        default=AUTO_SUBMIT_NONE
    )
    correct_answers = models.SmallIntegerField(default=0)
    attempted_questions = models.SmallIntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    # Status choices
    STATUS_GENERATING = 0
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_ABANDONED = 3
    
    STATUS_CHOICES = [
        (STATUS_GENERATING, 'Generating Questions'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ABANDONED, 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ],
    default='medium')
    time_limit_seconds = models.IntegerField(default=600)  # 10 minutes default
    paused_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(default=0)
    remaining_seconds = models.PositiveIntegerField(null=True, blank=True)  # NEW


    # JSON structure for questions:
    # [
    #   {
    #     "id": 1,
    #     "question": "What is...",
    #     "option_a": "...",
    #     "option_b": "...",
    #     "option_c": "...",
    #     "option_d": "...",
    #     "correct_answer": "A",
    #     "explanation": "...",
    #     "user_answer": null,  # filled when user answers
    #     "is_correct": null    # calculated when user answers
    #   }
    # ]
    questions = models.JSONField(null=True, blank=True)
    
    # AI metadata (model used, tokens, generation time, etc.)
    ai_meta = models.JSONField(null=True, blank=True)
    
    status = models.SmallIntegerField(default=STATUS_GENERATING, choices=STATUS_CHOICES)
    total_questions = models.SmallIntegerField(default=10)
    current_question_index = models.SmallIntegerField(default=0)  # Track progress
    score = models.FloatField(default=0.0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tab_violations = models.IntegerField(default=0)
    is_auto_submitted = models.BooleanField(default=False)
    flagged_for_review = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['category', 'subcategory']),
            models.Index(fields=['status']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.subcategory.name if self.subcategory else 'N/A'} ({self.difficulty})"
    
    def calculate_score(self):
        """Calculate score based on correct answers"""
        if not self.questions:
            return 0
        
        correct_count = sum(1 for q in self.questions if q.get('is_correct') == True)
        self.score = (correct_count / len(self.questions)) * 100
        return self.score
    
    def get_current_question(self):
        """Get the current question based on index"""
        if self.questions and 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def is_quiz_complete(self):
        """Check if all questions are answered"""
        if not self.questions:
            return False
        return all(q.get('user_answer') is not None for q in self.questions)
    
class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10)

    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField()

    normalized_hash = models.CharField(max_length=64, db_index=True, unique=True)

    source = models.CharField(
        max_length=10,
        choices=[('ai', 'AI'), ('manual', 'Manual')],
        default='ai'
    )

    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def make_hash(cls, text):
        return hashlib.sha256(cls.normalize(text).encode()).hexdigest()

    def __str__(self):
        return self.question_text[:60]

class Concept(models.Model):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="concepts"
    )
    difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ]
    )
    name = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subcategory', 'difficulty', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.subcategory.name} - {self.name} ({self.difficulty})"


class Feedback(models.Model):
    """User feedback after completing a quiz, displayed in testimonials"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1-5 stars
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    quiz_attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(max_length=500)
    is_approved = models.BooleanField(default=True)  # For moderation if needed
    is_featured = models.BooleanField(default=False)  # Featured on landing page
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.rating}★ - {self.created_at.strftime('%Y-%m-%d')}"

class AttemptQuestion(models.Model):
    """
    Tracks per-question state for a quiz attempt.
    This powers:
    - Question navigation palette
    - Review / Skip
    - Resume functionality
    """

    STATUS_UNVISITED = 0
    STATUS_SOLVED = 1
    STATUS_REVIEW = 2
    STATUS_SKIPPED = 3

    STATUS_CHOICES = [
        (STATUS_UNVISITED, "Unvisited"),
        (STATUS_SOLVED, "Solved"),
        (STATUS_REVIEW, "Marked for Review"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="attempt_questions"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,  # Allow null for AI-generated quizzes
        blank=True
    )

    question_order = models.PositiveSmallIntegerField()
    selected_option = models.CharField(
        max_length=1,
        null=True,
        blank=True
    )

    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_UNVISITED
    )

    is_correct = models.BooleanField(null=True, blank=True)

    visited_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('attempt', 'question_order')  # Changed: use question_order instead of question
        ordering = ['question_order']
        indexes = [
            models.Index(fields=['attempt', 'status']),
            models.Index(fields=['attempt', 'question_order']),
        ]

    def __str__(self):
        return f"{self.attempt.id} - Q{self.question_order} ({self.get_status_display()})"


class SharedQuiz(models.Model):
    """
    Represents a quiz that can be shared via link for classroom use.
    The creator can preview and edit questions before sharing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Creator of the shared quiz
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_shared_quizzes'
    )
    
    # Quiz metadata
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    
    # Questions (edited by creator)
    # Same JSON structure as QuizAttempt.questions but without user_answer/is_correct
    questions = models.JSONField(default=list)
    
    # Time settings
    time_limit_seconds = models.IntegerField(default=600)  # 10 minutes default
    
    # Sharing settings
    share_code = models.CharField(max_length=12, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)  # Can disable sharing
    max_attempts = models.PositiveIntegerField(default=1)  # Attempts per user
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional expiry
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['creator', 'created_at']),
            models.Index(fields=['share_code']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            # Generate a unique 8-character code
            import secrets
            import string
            while True:
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                if not SharedQuiz.objects.filter(share_code=code).exists():
                    self.share_code = code
                    break
        super().save(*args, **kwargs)
    
    def get_share_url(self):
        """Get the full shareable URL"""
        from django.urls import reverse
        return reverse('quizzes:take_shared_quiz', kwargs={'share_code': self.share_code})
    
    def get_attempts_count(self):
        """Get number of attempts for this shared quiz"""
        return self.shared_attempts.count()
    
    def get_completed_attempts(self):
        """Get completed attempts"""
        return self.shared_attempts.filter(status=QuizAttempt.STATUS_COMPLETED)
    
    def is_expired(self):
        """Check if quiz has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class SharedQuizAttempt(models.Model):
    """
    Links a QuizAttempt to a SharedQuiz for tracking shared quiz participation.
    """
    shared_quiz = models.ForeignKey(
        SharedQuiz, 
        on_delete=models.CASCADE, 
        related_name='shared_attempts'
    )
    attempt = models.OneToOneField(
        QuizAttempt, 
        on_delete=models.CASCADE, 
        related_name='shared_quiz_link'
    )
    
    # Track when user accessed via shared link
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('shared_quiz', 'attempt')
        indexes = [
            models.Index(fields=['shared_quiz', 'accessed_at']),
        ]
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.shared_quiz.title}"
