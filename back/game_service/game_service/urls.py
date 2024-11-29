from django.urls import path

from .views import *

urlpatterns = [
    path('api/games/history/', GameHistoryView.as_view()),
]
