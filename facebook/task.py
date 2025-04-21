from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_seller_status_email(email, status):
    subject = f"Your seller account has been {status}"
    message = f"Hello,\n\nYour seller account has been {status} by the admin.\n\nThank you!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, from_email,recipient_list)