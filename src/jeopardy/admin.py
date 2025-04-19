from django.contrib import admin
from django.apps import apps
from .models import Points, Cardset, Category, AnswerQuestion, AnswerQuestionAsked, GameRound, Player

@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    pass

@admin.register(Cardset)
class CardsetAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(AnswerQuestion)
class AnswerQuestionAdmin(admin.ModelAdmin):
    list_filter = ["category", "points", "answer_media_type"]
    list_display = ["category", "points", "internal_notes", "answer_text", "answer_media_type"]

@admin.register(AnswerQuestionAsked)
class AnswerQuestionAskedAdmin(admin.ModelAdmin):
    list_filter = ["gameround", "player_correct"]
    list_display = ["gameround", "player_correct", "time_asked", "time_updated", "answer_question"]

@admin.register(GameRound)
class GameRoundAdmin(admin.ModelAdmin):
    pass

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass