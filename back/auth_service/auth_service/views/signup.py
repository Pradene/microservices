import logging
import json
import requests

from datetime import timedelta

from django.views import View
from django.http import JsonResponse
from django.db import IntegrityError

from auth_service.celery import app

from auth_service.models import CustomUser
from auth_service.utils import create_jwt, create_profile

logger = logging.getLogger(__name__)

class SignUpView(View):
	def post(self, request, *args, **kwargs):
		try:
			data = json.loads(request.body)

			email = data.get('email')
			username = data.get('username')
			password = data.get('password')
			password_confirmation = data.get('password_confirmation')

			if not username or not email or not password or not password_confirmation:
				return JsonResponse({'errors': {'global': 'One field required is null.'}}, status=400)

			if password != password_confirmation:
				return JsonResponse({'errors': {'password': 'Passwords are not the same'}}, status=400)

			user = CustomUser.objects.create(
				username=username,
				email=email
			)

			user.set_password(password)
			user.save()

			create_profile(
				user.id,
				user.username,
				user.email
			)

			app.send_task(
				'mail_service.tasks.send_welcome_email',
				args=[email, username],
				queue='mail_queue'
			)

			return JsonResponse({'message': 'User created'}, status=201)
		
		except json.JSONDecodeError:
			return JsonResponse({'errors': {'global': 'Invalid JSON data'}}, status=400)

		except IntegrityError as e:
			errors = {}
			if 'username' in str(e):
				errors['username'] = 'Username is already in use.'
			if 'email' in str(e):
				errors['email'] = 'Email is already in use.'
			
			return JsonResponse({'errors': errors}, status=400)

		except Exception as e:
			logger.error(f'error: {e}')
			return JsonResponse({'errors': {'global': 'An error occurred while creating the user.'}}, status=400)
	