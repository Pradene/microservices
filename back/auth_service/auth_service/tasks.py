import redis

from celery import Celery
from auth_service.celery import app
from auth_service.models import CustomUser

@app.task(bind=True, max_retries=3, queue='auth_queue')
def update_user(self, user_id, username, email, is_2fa_enabled):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return {'status': 'failure', 'error': 'User not found'}
    except Exception as e:
        self.retry(countdown=10, exc=e)
    
    user.username = username
    user.email = email
    user.is_2fa_enabled = is_2fa_enabled
    user.save()

    return {'status': 'success', 'message': f'User {user_id} updated successfully'}