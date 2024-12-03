import logging
import requests
import jwt
import json

from django.http import JsonResponse
from django.core.cache import cache
from django.views import View
from django.utils.decorators import method_decorator

from game_service.models import TournamentModel, GameModel, ScoreModel
from game_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class TournamentView(View):
	def get(self, request, *args, **kwargs):
		try:
			tournament_id = kwargs.get('tournament_id')
			tournament = TournamentModel.objects.get(id=tournament_id)

			games = GameModel.objects.filter(tournament_id=tournament_id)

			tournament_data = {
				'id': tournament.id,
				'games': [],
				'users': [],
			}

			for game in games:
				game_data = {
					'id': game.id,
					'user_ids': game.user_ids,
					'winner_id': game.winner_id if game.winner_id else None,
					'round': game.tournament_round
				}

				tournament_data['games'].append(game_data)

			user_ids = set(tournament.user_ids)
			for user_id in user_ids:
				user_info = self.get_user(request, user_id)
				if user_info:
					tournament_data['users'].append(user_info)

			return JsonResponse({'tournament': tournament_data}, status=200)

		except TournamentModel.DoesNotExist:
			return JsonResponse({}, status=400)

		except Exception as e:
			return JsonResponse({}, status=400)


	def get_user(self, request, user_id):
		"""
		Retrieve user data from cache or the user service.
		"""
		cached_user = cache.get(f'user:{user_id}')
		if cached_user:
			return cached_user

		try:
			token =  request.COOKIES.get('access_token')
			if not token:
				raise Exception('Token is missing')

			# Make a request to the user service if the user is not cached
			headers = {'Authorization': f'Bearer {token}'}
			response = requests.get(f'http://user-service:8000/api/users/{user_id}/', headers=headers)

			if response.status_code == 200:
				data = response.json()

				# Cache the user data for future requests
				cache.set(f'user:{user_id}', data['user'], timeout=60 * 15)
				return data['user']
			
			else:
				logger.error(f'Error fetching user {user_id} from user service: {response.status_code}')
				return {}  # Default user data if fetch fails
		
		except Exception as e:
			logger.error(f'Error fetching user {user_id}: {e}')
			return {}
