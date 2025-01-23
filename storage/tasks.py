from celery import shared_task

from .emails import send_email_message


@shared_task
def send_email_message_task(subject, message, user_email):
    """
    Асинхронная задача для отправки email-сообщения.

    Эта функция используется для выполнения отправки email в фоновом режиме,
    чтобы избежать задержек в основном потоке приложения.
    """
    return send_email_message(subject, message, user_email)
