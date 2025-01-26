from datetime import datetime, timedelta

from celery import shared_task
from django.apps import apps

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
def send_monthly_email_reminder(rent_id, subject, message):
    """
    Задача для отправки писем с напоминаниями раз в месяц.
    """
    Rent = apps.get_model("storage", "Rent")
    rent = Rent.objects.get(pk=rent_id)

    next_run_time = datetime.now() + timedelta(minutes=1)
    task = send_monthly_email_reminder.apply_async(
        (rent_id, subject, message), eta=next_run_time
    )

    rent.task_ids.append(task.id)
    rent.save()

    return send_email_message(subject, message, rent.email)
