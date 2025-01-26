from django.conf import settings
from django.core.mail import EmailMessage


def send_email_message(subject, message, user_email):
    """
    Функция отправки письма
    """

    email_message = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[user_email],
    )
    email_message.send(fail_silently=False)
