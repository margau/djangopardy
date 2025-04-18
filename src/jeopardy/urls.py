from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview, name='overview'),
    path('cardset/<int:id>', views.cardset, name='cardset'),
    path('gameround/<int:id>', views.gameround, name='gameround'),
    path('play/<int:id>', views.play, name='play'),
]
