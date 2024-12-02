import logging
import json

from datetime import timedelta

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

from auth_service.utils import create_jwt
from auth_service.models import OTP
from auth_service.celery import app

logger = logging.getLogger(__name__)

class LoginView(View):
	def post(self, request, *args, **kwargs):
		try:
			data = json.loads(request.body)

			username = data.get('username')
			password = data.get('password')
			remember_me = data.get('remember_me', False)

			user = authenticate(request, username=username, password=password)
			if user is None:
				return JsonResponse({'error': 'Login failed'}, status=400)

			if not user.is_2fa_enabled:
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
				request.session['2fa_user_id'] = user.id
				code = OTP.generate(user.id)
				logger.info(f'OTP code for user {user.id}: {code}')

				task = app.send_task(
					'mail_service.tasks.send_otp_email',
					args=[
						user.email,
						user.username,
						code
					],
					queue='mail_queue'
				)

				return JsonResponse({'2fa': True}, status=200)
		
		except Exception as e:
			logger.error(f'Error during the login: {e}')
			return JsonResponse({'error': 'An error occuried during while creating the user'}, status=400)
