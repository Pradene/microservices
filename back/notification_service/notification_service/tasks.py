from celery import shared_task

@shared_task
def send_notification(user_id):
    # Logic to send a welcome email
    print(f"Welcome email sent to user {user_id}")