import logging

from django.conf import settings
from django.core.mail import send_mail

from mail_service.celery import app

logger = logging.getLogger(__name__)

# Problem connecting to the email
@app.task(queue='mail_queue')
def send_welcome_email(email, username):
	logger.info(f'sending welcome email')

	from_email = settings.EMAIL
	subject = 'Welcome to Pong.'
	message = "Thank you for registering with us {username}. \
			We're excited to have you on board."

	send_mail(subject, message, from_email, [email], fail_silently=False)

	return f'Email sent to {username} successfully'


@app.task(queue='mail_queue')
def send_otp_email(email, username, code):
	logger.info(f'sending otp email')

	from_email = settings.EMAIL
	subject = "Your One Time Password"
	message = f"Dear {username}, \
			\n\nYour OTP code is {code}. \
			It is valid for the next 10 minutes. \
			\n\nThank you!"
	
	send_mail(subject, message, from_email, [email], fail_silently=False)