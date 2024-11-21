import jwt
import datetime
from django.conf import settings

def create_jwt(user_id, timedelta):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + timedelta,
        "iat": datetime.datetime.utcnow(),
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        return payload['user_id']

    except jwt.ExpiredSignatureError:
        return None
    
    except jwt.InvalidTokenError:
        return None