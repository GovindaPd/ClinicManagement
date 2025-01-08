from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(email, otp):
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    from_email = 'prafullagarawal59@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)