import logging
import requests
import jwt

from datetime import timedelta

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Q

from friend_service.models import Friendship

from friend_service.decorators import jwt_required
from friend_service.utils import create_jwt

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class FriendshipStatusView(View):
	def get(self, request, friend_id):
		logger.info(f"Received GET request for friend_id {friend_id} from user {request.user_id}")

		user_id = request.user_id

		try:
			friendship = Friendship.objects.filter((
				Q(user_id=user_id, friend_id=friend_id) |
				Q(user_id=friend_id, friend_id=user_id)
			)).first()

			if friendship:
				return JsonResponse({'status': friendship.status}, status=200)
			else:
				return JsonResponse({'status': 'none'}, status=200)

		except Friendship.DoesNotExist:
			return JsonResponse({'status': 'none'}, status=200)

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return JsonResponse({'status': 'none'}, status=200)


@method_decorator(jwt_required, name='dispatch')
class FriendshipRequestView(View):
	def get(self, request):
		try:
			logging.info(f'getting friend requests')
			user_id = request.user_id

			requests = Friendship.objects.filter(
				friend_id=user_id,
				status='pending'
			)

			requests_data = []
			for request in requests:
				logging.info(f'request: {request.user_id} -- {request.friend_id} : {request.status}')
				friend_data = self.get_user_by_id(user_id, request.user_id)
				if friend_data:
					requests_data.append({
						'id': friend_data.get('id'),
						'username': friend_data.get('username'),
						'picture': friend_data.get('picture')
					})
			
			return JsonResponse({'requests': requests_data}, status=200)

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return JsonResponse({'error': 'error'}, status=400)


	def get_user_by_id(self, user_id, friend_id):
		try:
			url = f'http://user-service:8000/api/users/{friend_id}/'
			token = create_jwt(user_id, timedelta(minutes=2))
			headers = {
				'Authorization': f'Bearer {token}'
			}

			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				data = response.json()
				user = data.get('user')
				return user

			else:
				return None

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return None


@method_decorator(jwt_required, name='dispatch')
class FriendshipView(View):
	def get(self, request):
		try:
			logging.info(f'getting friends')
			
			user_id = request.user_id
			friendships = Friendship.objects.filter(
				Q(user_id=user_id) | Q(friend_id=user_id),
				status='accepted'
			)
			
			friends_data = []
			for friendship in friendships:
				logging.info(f'friendship: {friendship.user_id} -- {friendship.friend_id} : {friendship.status}')
				if friendship.user_id == user_id:
					friend_id = friendship.friend_id
				else:
					friend_id = friendship.user_id
				friend_data = self.get_user_by_id(user_id, friend_id)
				if friend_data:
					friends_data.append({
						'id': friend_data.get('id'),
						'username': friend_data.get('username'),
						'picture': friend_data.get('picture')
					})
			
			return JsonResponse({'friends': friends_data}, status=200)

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return JsonResponse({'error': 'error'}, status=400)


	def get_user_by_id(self, user_id, friend_id):
		try:
			url = f'http://user-service:8000/api/users/{friend_id}/'
			token = create_jwt(user_id, timedelta(minutes=2))
			headers = {
				'Authorization': f'Bearer {token}'
			}

			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				data = response.json()
				user = data.get('user')
				return user

			else:
				return None

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return None
