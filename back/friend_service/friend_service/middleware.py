import jwt
import logging

from channels.auth import BaseMiddleware
from django.conf import settings

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(BaseMiddleware):
	async def __call__(self, scope, receive, send):
		# Retrieve the token from the cookies in the WebSocket request
		cookies = self.get_cookies(scope)
		token = cookies.get('access_token')  # Retrieve the access token from cookies

		if token:
			user_id = await self.authenticate_token(token)
			if user_id:
				scope['user_id'] = user_id

		# Proceed with the WebSocket connection
		await super().__call__(scope, receive, send)

	def get_cookies(self, scope):
		"""
		Utility function to get cookies from the WebSocket handshake.
		The cookies are part of the headers, so we need to parse them.
		"""
		cookies = {}
		headers = dict(scope['headers'])
		cookie_header = headers.get(b'cookie')

		if cookie_header:
			cookie_header = cookie_header.decode('utf-8')
			for cookie in cookie_header.split(';'):
				key, value = cookie.strip().split('=', 1)
				cookies[key] = value

		return cookies

	async def authenticate_token(self, token):
		try:
			# Decode the JWT token and get the user
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
			user_id = payload['user_id']
			return user_id
		except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
			return None