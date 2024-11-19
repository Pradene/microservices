import logging
import json
import jwt
import requests

from datetime import timedelta

from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from auth_service.celery import app

from auth_service.models import CustomUser
from auth_service.utils.jwt import create_jwt

class TokenView(View):
	def get(self, request):
		pass

	# Refresh the access token
	def post(self, request):
		token = request.COOKIES.get('refresh_token')

		if token is None:
			return JsonResponse({'error': 'Invalid token, could not refresh the token'}, status=400)

		user_id = self.decode_token(token)

		if user_id:
			try:
				user = CustomUser.objects.get(id=user_id)
			except CustomUser.DoesNotExist:
				return JsonResponse({'error': 'Invalid token, could not refresh the token'}, status=400)

			access_token = create_jwt(user.id, timedelta(minutes=5))
			response = JsonResponse({}, status=200)

			response.set_cookie(
				key='access_token',
				value=access_token,
				httponly=False,
				secure=True,
				samesite='None'
			)

			return response

		else:
			return JsonResponse({'error': 'Invalid token, could not refresh the token'}, status=400)

	def decode_token(self, token):
		try:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
			return payload['user_id']
		except jwt.ExpiredSignatureError:
			return None
		except jwt.InvalidTokenError:
			return None