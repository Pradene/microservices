from django.urls import path
from .consumers import FriendsConsumer

websocket_urlpatterns = [
    path('ws/friends/', FriendsConsumer.as_asgi()),
]