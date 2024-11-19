import logging
import json

from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from auth_service.celery import app

from auth_service.models import CustomUser

logger = logging.getLogger(__name__)

class OTPView(View):
	def get(self, request, *args, **kwargs):
		user_id = request.session.get('user_id')
		if user_id is None:
			return JsonResponse({'error': 'You should login before'}, status=400)

		logger.info(f'need to implement code sending')

		return JsonResponse({'message': 'OTP sended by email'}, status=200)

	def post(self, request, *args, **kwargs):
		data = json.loads(request.body)
		code = data.get('code')
		user_id = data.get('user_id')

		user = CustomUser.objects.get(id=user_id)

		if user.is_2fa_enabled is False:
			login(request, user)

			user.is_online = True
			user.save()

			access_token = create_jwt(user.id, timedelta(minutes=5))
			refresh_token = create_jwt(user.id, timedelta(days=1))
			
			response = JsonResponse({
				'message': 'User logged in succesfully',
			}, status=200)
			
			response.set_cookie(
				key='access_token',
				value=access_token,
				httponly=False,
				secure=True,
				samesite='None'
			)
			response.set_cookie(
				key='refresh_token',
				value=refresh_token,
				httponly=True,
				secure=True,
				samesite='None'
			)

			return response
			
		else:
			return JsonResponse({'error': 'Code is invalid'}, status=400)



		