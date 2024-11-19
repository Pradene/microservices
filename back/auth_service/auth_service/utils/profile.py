import requests
import logging

from datetime import timedelta

from auth_service.utils import create_jwt

logger = logging.getLogger(__name__)

def create_profile(user_id, username, email):
	try:
		url = f'http://user-service:8000/api/users/{user_id}/profile/'
		
		access_token = create_jwt(user_id, timedelta(minutes=2))
		headers = { 'Authorization': f'Bearer {access_token}' }
		data = {
			'username': username,
			'email': email
		}

		response = requests.post(
			url,
			headers=headers,
			json=data
		)
		
		logger.info(f'response status: {response.status_code}')
		if response.status_code != 200:
			logger.error(f'Error creating profile for user {user_id}: {response.text}')
			# You may want to raise an exception here or handle it accordingly
		else:
			logger.info(f'Profile created successfully for user {user_id}')
	
	except requests.RequestException as e:
		# Handle any request errors (e.g., network issues)
		logger.error(f'Error creating profile for user {user_id}: {e}')