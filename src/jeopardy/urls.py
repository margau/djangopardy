from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview, name='overview'),
    path('cardset/<int:id>', views.cardset, name='cardset'),
    path('gameround/<int:id>', views.gameround, name='gameround'),
    path('play/<int:id>', views.play, name='play'),
    path('play/<int:gameround_id>/answer/<int:answer_id>', views.answer, name='answer'),
    path('play/<int:gameround_id>/answeraction/none/<int:answer_id>', views.question, {"action": "none"}, name='answer-none'),
    path('play/<int:gameround_id>/answeraction/correct/<int:answer_id>', views.question, {"action": "correct"}, name='answer-none'),
]
