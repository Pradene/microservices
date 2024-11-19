import logging
import json
import requests

from datetime import timedelta

from django.views import View
from django.http import JsonResponse
from django.db import DatabaseError
from django.utils.decorators import method_decorator

from user_service.celery import app
from user_service.models import Profile
from user_service.decorators import jwt_required
from user_service.utils import create_jwt

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class ProfileView(View):
	def get(self, request, user_id=None):
		try:
			profile = Profile.objects.get(user_id=user_id)
		except Profile.DoesNotExist:
			return JsonResponse({'error': 'user is unknown'}, status=400)

		profile_data = {
			'id': profile.user_id,
			'username': profile.username,
			'picture': profile.picture.url if profile.picture else None,
			'level': profile.level,
			'experience': profile.experience,
			'experience_required': profile.level * 100
		}

		if request.user_id == user_id:
			profile_data['is_2fa_enabled'] = profile.is_2fa_enabled
			profile_data['email'] = profile.email
		else:
			profile_data['status'] = self.get_status(request.user_id, user_id)
		
		return JsonResponse({'user': profile_data}, status=200)


	def post(self, request, user_id=None):
		if Profile.objects.filter(user_id=user_id).exists():
			return self.update_profile(request, user_id)
		
		data = json.loads(request.body)

		username = data.get('username')
		email = data.get('email')
		
		profile = Profile.objects.create(
			user_id=user_id,
			username=username,
			email=email
		)
		
		return JsonResponse({'message': 'User profile created'}, status=200)


	def put(self, request, user_id=None):
		return self.update_profile(request, user_id)


	def update_profile(self, request, user_id):
		try:
			profile = Profile.objects.get(user_id=user_id)
		except Profile.DoesNotExist:
			return JsonResponse({'error': 'User not found'}, status=400)

		username = request.POST.get('username', profile.username)
		bio = request.POST.get('bio', profile.bio)
		email = request.POST.get('email', profile.email)
		is_2fa_enabled = request.POST.get('is_2fa_enabled', profile.is_2fa_enabled)

		if 'picture' in request.FILES:
			picture = request.FILES['picture']
		else:
			picture = profile.picture

		if Profile.objects.exclude(user_id=profile.user_id).filter(username=username).exists():
			return JsonResponse({'error': 'Username is already taken'}, status=400)

		profile.username = username
		profile.email = email
		profile.picture = picture
		profile.bio = bio
		profile.is_2fa_enabled = True if is_2fa_enabled == 'true' else False
		
		profile.save()

		task = app.send_task(
			'auth_service.tasks.update_user',
			args=[user_id, username, email, is_2fa_enabled],
			queue='auth_queue'
		)

		return JsonResponse({'message': 'User profile updated'}, status=200)

	def get_status(self, user_id, friend_id):
		try:
			url = f'http://friend-service:8000/api/friends/{friend_id}/status/'

			token = create_jwt(user_id, timedelta(minutes=2))
			headers = { 'Authorization': f'Bearer {token}' }

			response = requests.get(url, headers=headers)
			if response.status_code != 200:
				logging.error(f'error: {response.status_code}')
				return 'none'

			data = response.json()
			status = data.get('status')
			return status
		
		except Exception as e:
			logger.error(f'error: {str(e)}')
			return 'none'