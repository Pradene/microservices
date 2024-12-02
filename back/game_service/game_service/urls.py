from django.urls import path

from .views import *

urlpatterns = [
    path('api/games/', GameView.as_view()),
    path('api/games/stats/', GameStatView.as_view()),
    path('api/games/history/', GameHistoryView.as_view()),
]
