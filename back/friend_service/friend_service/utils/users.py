import redis
import requests
import json
import logging

from .jwt import create_jwt

logger = logging.getLogger(__name__)

def get_user_by_id(user_id):
    try:
        url = f'http://user-service:8000/api/users/{user_id}/'
        token = create_jwt()
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            user = data.get('user')
            return user

        else:
            return None
    except Exception as e:
        logger.error(f'error: {str(e)}')
        return None