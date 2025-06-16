from django.contrib import admin
from django.apps import apps
from .models import Points, Cardset, Category, AnswerQuestion, AnswerQuestionAsked, GameRound, Player
from django.db.models import Count

@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    pass

@admin.register(Cardset)
class CardsetAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

class NumAskedListFilter(admin.SimpleListFilter):
    title = "Number of times asked"
    parameter_name = "num_asked"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return (
            (0, "0"),
            (1, ">0")
        )

    def queryset(self, request, queryset):
        val = self.value()
        print(val)
        print(type(val))
        if self.value() == "0":
            return queryset.filter(num_asked=self.value())
        elif self.value() == "1":
            return queryset.filter(num_asked__gt=0)
        return queryset

@admin.register(AnswerQuestion)
class AnswerQuestionAdmin(admin.ModelAdmin):
    list_filter = ["category", "points", "answer_media_type", NumAskedListFilter]
    list_display = ["category", "points", "internal_notes", "answer_text", "answer_media_type", "num_asked"]

    def num_asked(self, obj):
        return obj.num_asked

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