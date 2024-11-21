import jwt
import logging

from django.conf import settings
from channels.db import database_sync_to_async
from functools import wraps

logger = logging.getLogger(__name__)

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            token = None
            
            header = request.headers.get('Authorization')
            if header and header.startswith('Bearer '):
                token = header.split(' ')[1]
            
            else:
                token = request.COOKIES.get('access_token')
            
            if not token:
                return JsonResponse({'error': 'Authorization required'}, status=401)

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload.get('user_id')
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        except Exception as e:
            return JsonResponse({'error': f'Error when verifying the token, {str(e)}'}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def jwt_required_ws(func):
	@wraps(func)
	async def wrapper(self, *args, **kwargs):
		headers = dict((k.decode('utf-8'), v.decode('utf-8')) for k, v in self.scope['headers'])
		token = headers.get('sec-websocket-protocol')

		if token:
			try:
				# Decode the JWT token
				decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
				self.scope['user_id'] = decoded.get('user_id')
			except jwt.ExpiredSignatureError:
				self.scope['user_id'] = None
			except jwt.InvalidTokenError:
				self.scope['user_id'] = None
		else:
			self.scope['user_id'] = None

		# If no user_id found, reject connection
		if not self.scope['user_id']:
			await self.close()
			return

		return await func(self, *args, **kwargs)

	return wrapper