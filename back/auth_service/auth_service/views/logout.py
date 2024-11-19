import logging
import json
import jwt

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils.decorators import method_decorator

from auth_service.models import CustomUser
from auth_service.decorators import jwt_required
from auth_service.utils import decode_jwt

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class LogoutView(View):
	def post(self, request, *args, **kwargs):
		try:
			refresh_token = request.COOKIES.get('refresh_token')
	
			user_id = decode_jwt(refresh_token)
			user = CustomUser.objects.get(id=user_id)
			user.is_online = False
			user.save()

			logout(request)

			response = JsonResponse({'message': 'logout successfully'}, status=200)
			response.delete_cookie('access_token')
			response.delete_cookie('refresh_token')

			return response

		except Exception as e:
			logger.info(f'error: {str(e)}')
			return JsonResponse({'error': 'Invalid token'}, status=400)
