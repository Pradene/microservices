import logging
import requests
import jwt

from django.http import JsonResponse
from django.core.cache import cache
from django.views import View
from django.utils.decorators import method_decorator

from game_service.models import GameModel
from game_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class GameStatView(View):

	def get(self, request):
		user_id = request.GET.get('user_id')
		if user_id is None:
			return JsonResponse({'error': 'you have to pass an user id'}, status=400)

		try:
			games = GameModel.objects.filter(
				user_ids__contains=[user_id],
				status='finished'
			)

			wins = games.filter(winner_id=user_id).count()
			loses = games.exclude(winner_id=user_id).count()

			total_games = games.count()

			data = {
				'total_games': total_games,
				'wins': wins,
				'loses': loses,
			}
	
			return JsonResponse(data, safe=False, status=200)
	
		except Exception as e:
			return JsonResponse({'error': str(e)}, status=400)
