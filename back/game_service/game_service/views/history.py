import logging
import requests
import jwt

from django.http import JsonResponse
from django.core.cache import cache
from django.views import View
from django.utils.decorators import method_decorator

from game_service.models import GameModel, ScoreModel
from game_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class GameHistoryView(View):

	def get(self, request):
		user_id = request.user_id

		try:
			games = GameModel.objects.filter(user_ids__contains=[user_id]).order_by('created_at')

			games_data = []
			for game in games:
				# Fetch scores for the game
				scores = {score.user_id: score.score for score in ScoreModel.objects.filter(game_id=game.id)}

				# Fetch user data and embed score
				users_data = []
				for uid in game.user_ids:
					user_data = self.get_user(request, uid)
					if user_data:
						users_data.append({
							'id': user_data['id'],
							'username': user_data['username'],
							'picture': user_data['picture'],
							'score': scores.get(uid, 0)  # Default score is 0 if not found
						})
					

				game_info = {
					'id': game.id,
					'users': users_data,
					'winner_id': game.winner_id
				}
				games_data.append(game_info)

			return JsonResponse({'games': games_data}, status=200)

		except Exception as e:
			logger.error(f'Error during getting game history: {e}')
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
