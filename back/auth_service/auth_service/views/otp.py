import logging
import json

from datetime import timedelta

from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import login

from auth_service.celery import app
from auth_service.models import CustomUser, OTP
from auth_service.utils import create_jwt

logger = logging.getLogger(__name__)

class OTPView(View):
	def get(self, request, *args, **kwargs):
		user_id = request.session.get('2fa_user_id', '')
		if user_id is None:
			return JsonResponse({'error': 'You should login before'}, status=400)

		try:
			user = CustomUser.objects.get(id=user_id)
		except CustomUser.DoesNotExist:
			return JsonResponse({'error': 'user does not exist'}, status=400)

		code = OTP.generate(user.id)
		logger.info(f'OTP code: {code}')
		task = app.send_task(
			'mail_service.tasks.send_otp_email',
			args=[
				user.email,
				user.username,
				code
			],
			queue='mail_queue'
		)

		return JsonResponse({'message': 'OTP sended by email'}, status=200)

	def post(self, request, *args, **kwargs):
		user_id = request.session.get('2fa_user_id', '')
		logger.info(f'user id trying to send otp: {user_id}')

		if user_id is None:
			return JsonResponse({'error': 'You should login before'}, status=400)
		
		data = json.loads(request.body)
		code = data.get('code')

		user = CustomUser.objects.get(id=user_id)

		if user.is_2fa_enabled is True:
			if not OTP.validate(user_id, code):
				return JsonResponse({'error': 'Code is not valid'}, status=400)

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
		