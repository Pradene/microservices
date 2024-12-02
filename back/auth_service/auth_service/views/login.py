import logging
import json

from datetime import timedelta

from django.views import View
from django.http import JsonResponse

from django.contrib.auth import authenticate, login
from auth_service.utils.jwt import create_jwt

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
				# Generate an OTP
				# code = OTP.generate(user)
				code = 000000

				task = app.send_task(
					'mail_service.tasks.send_otp_email',
					args=[
						user.email,
						user.username,
						code
					],
					queue='mail_queue'
				)

				return JsonResponse({'message': '2fa need an implementation'}, status=200)
		
		except Exception as e:
			logger.error(f'error: {e}')
			return JsonResponse({'error': 'An error occuried during while creating the user'}, status=400)
