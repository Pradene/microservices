import jwt
from datetime import datetime
from django.conf import settings

def create_jwt(user_id, timedelta):
	payload = {
		"user_id": user_id,
		"exp": datetime.utcnow() + timedelta,
		"iat": datetime.utcnow(),
	}
	
	token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
	return token