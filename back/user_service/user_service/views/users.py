import logging
import json

from django.views import View
from django.http import JsonResponse
from django.db import DatabaseError
from django.utils.decorators import method_decorator

from user_service.models import Profile
from user_service.decorators import jwt_required

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class UserView(View):
	def get(self, request, user_id=None):
		try:
			profile = Profile.objects.get(user_id=user_id)
		except Profile.DoesNotExist:
			return JsonResponse({'error': 'user is unknown'}, status=400)

		profile_data = {
			'id': profile.user_id,
			'username': profile.username,
			'picture': profile.picture.url if profile.picture else None
		}
		
		return JsonResponse({'user': profile_data}, status=200)


@method_decorator(jwt_required, name='dispatch')
class UserListView(View):
	def get(self, request):
		query = request.GET.get('q', '')

		if query:
			users = Profile.objects.filter(username__icontains=query)
		else:
			users = Profile.objects.all()
		
		users_data = [
			{
				'id': user.user_id,
				'username': user.username,
				'picture': user.picture.url if user.picture else None
			} for user in users
		]

		return JsonResponse({'users': users_data}, status=200)