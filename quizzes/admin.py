from django.contrib import admin
from .models import Category, SubCategory, QuizAttempt, Concept, Feedback


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "level", "is_leaf")
    list_filter = ("category", "level", "is_leaf")
    search_fields = ("name",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "subcategory", "score", "started_at")
    list_filter = ("category", "difficulty", "status")


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'difficulty')
    list_filter = ('difficulty', 'subcategory')
    search_fields = ('name',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_approved', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_featured')
    search_fields = ('user__username', 'comment')
    list_editable = ('is_approved', 'is_featured')
    ordering = ('-created_at',)
