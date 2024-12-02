import logging
import requests
import jwt
import json

from django.http import JsonResponse
from django.core.cache import cache
from django.views import View
from django.utils.decorators import method_decorator

from game_service.models import GameModel
from game_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class GameView(View):
	def post(self, request):
		try:
			data = json.loads(request.body)
			user_ids = data.get('user_ids')
			if user_ids is None:
				logger.error(f'Error user_ids is not defined')
				return JsonResponse({}, status=400)

			game = GameModel.objects.create(
				user_ids=user_ids
			)

			return JsonResponse({'game_id': game.id}, status=200)
		
		except Exception as e:
			logger.error(f'Error during game creation: {e}')
			return JsonResponse({}, status=400)