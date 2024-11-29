import logging
import json
import requests
import os

from datetime import timedelta

from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth import login

from urllib.parse import urlencode

from auth_service.celery import app
from auth_service.models import CustomUser
from auth_service.utils import create_jwt, create_profile

logger = logging.getLogger(__name__)

class OAuthView(View):
	def get(self, request):
		try:
			uid = settings.OAUTH_UID
			redirect_uri = settings.OAUTH_REDIRECT_URI

			params = {
				'grant_type': 'client_credentials',
				'client_id': uid,
				'redirect_uri': redirect_uri,
				'response_type': 'code',
				'scope': 'public'
			}

			oauth_url = settings.OAUTH_URL
			url = f'{oauth_url}/oauth/authorize?{urlencode(params)}'
			return JsonResponse({'url': url}, status=200)
		
		except Exception as e:
			logger.error(f'Error during oauth: {str(e)}')
			return JsonResponse({'error': 'Could not connect with oauth'}, status=400)


class OAuthCallbackView(View):
	def get(self, request):
		code = request.GET.get('code', '')		
		if code is None:
			return JsonResponse({'error': 'Code is not valid'}, status=400)
		
		uid = settings.OAUTH_UID
		secret = settings.OAUTH_SECRET
		redirect_uri = settings.OAUTH_REDIRECT_URI
		
		params = {
			'grant_type': 'authorization_code',
			'client_id': uid,
			'client_secret': secret,
			'redirect_uri': redirect_uri,
			'code': code
		}
		
		oauth_url = settings.OAUTH_URL
		url = f'{oauth_url}/oauth/token'
		
		response = requests.post(url, data=params)
		
		if response.status_code != 200:
			logging.error(f'Error in response from oauth: {response.status_code} = {response.text}')
			return HttpResponseRedirect(f'https://localhost:5000/login/')
	
		data = response.json()
		oauth_token = data.get('access_token')
	
		user = self.get_user(oauth_token)
		if user is None:
			return HttpResponseRedirect(f'https://localhost:5000/login/')

		login(request, user)
		
		user.is_online = True
		user.save()
	
		access_token = create_jwt(user.id, timedelta(minutes=5))
		refresh_token = create_jwt(user.id, timedelta(hours=1))
	
		response = HttpResponseRedirect(f"https://localhost:5000/")
	
		response.set_cookie(
			'access_token',
			access_token,
			httponly=False,
			secure=True,
			samesite='Lax'
		)
		
		response.set_cookie(
			'refresh_token',
			refresh_token,
			httponly=True,
			secure=True,
			samesite='Lax'
		)
	
		return response


	def get_user(self, token):		
		try:
			headers = {
				"Authorization": f"Bearer {token}"
			}

			response = requests.get(f'{settings.OAUTH_URL}/v2/me', headers=headers)
			data = response.json()

			id_42 = data.get("id")
			login = data.get("login")
			email = data.get("email")
			
			if CustomUser.objects.filter(id_42=id_42).exists():
				user = CustomUser.objects.get(id_42=id_42)
				return user

			suffix = 42
			username = login
			while CustomUser.objects.filter(username=username).exists():
				username = f"{login}_{suffix}"
				suffix += 1

			user = CustomUser.objects.create_user(
				username=username,
				email=email,
				id_42=id_42
			)

			create_profile(
				user.id, 
				user.username,
				user.email
			)

			return user

		except IntegrityError as e:
			logger.error(f'Integrity Error: {str(e)}')
			return None

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return None