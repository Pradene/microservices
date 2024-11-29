import logging
import requests
import jwt

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator

from game_service.models import GameModel
from game_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class GameHistoryView(View):
	def get(self, request):
		user_id = request.user_id

		try:
			games = GameModel.objects.filter(
				user_ids__contains=[user_id]
			)

			games_data = []
			for game in games:
				game_info = {
					'id': game.id,
					'users': game.user_ids,
					'winner': game.winner_id
				}
				games_data.append(game_info)

			return JsonResponse({'games': games_data}, status=200)

		except Exception as e:
			logger.error(f'Error during getting game history: {e}')
			return JsonResponse({}, status=400)