import redis
import requests
import json

def get_user(user_id):
    headers = {
        'Host': 'user-service',
    }

    response = requests.get(f'http://user-service:8000/users/{user_id}/', headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data

    else:
        return None