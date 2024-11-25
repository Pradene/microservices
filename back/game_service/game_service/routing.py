from django.urls import path

from .consumers import *

websocket_urlpatterns = [
    # path('ws/tournament/<int:tournament_id>/', TournamentConsumer.as_asgi()),
    # path('ws/game/<int:game_id>/', GameConsumer.as_asgi()),
    path('ws/game/local/', LocalGameConsumer.as_asgi()),
    # path('ws/matchmaking/<str:type>/', MatchmakingConsumer.as_asgi()),
]