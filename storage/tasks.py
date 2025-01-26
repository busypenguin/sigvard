from datetime import datetime, timedelta

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


@shared_task
def send_monthly_email_reminder(subject, message, user_email):
    """
    Задача для отправки писем с напоминаниями раз в месяц.
    """
    next_run_time = datetime.now() + timedelta(minutes=1)
    send_monthly_email_reminder.apply_async(
        (subject, message, user_email), eta=next_run_time
    )

    return send_email_message(subject, message, user_email)
