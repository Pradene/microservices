from django.urls import path, include

from user_service.views import *

urlpatterns = [
    path('api/', include([
        path('users/', UserListView.as_view()),
        path('users/<int:user_id>/', UserView.as_view()),
        path('users/<int:user_id>/profile/', ProfileView.as_view())
    ]))
]
