def create_confirm_rent_message(rent) -> tuple[str, str]:
    """
    Создает тему письма (subject) и текст сообщения (message) подтверждения аренды бокса

    """
    subject = f"Ваш заказ аренды бокса {rent.box} принят"
    message = (
        f"Аренда бокса {rent.box} с {rent.start_date.date()} по {rent.end_date.date()}. "
        f"Адрес самовывоза груза: {rent.pickup_address}"
    )

    return subject, message


def create_end_rent_message(rent) -> tuple[str, str]:
    """
    Создает тему письма (subject) и текст сообщения (message) окончания аренды бокса

    """
    subject = f"Окончание аренды №{rent.pk}"
    message = (
        f"Напоминаем, что срок аренды вашего бокса на складе "
        f"{rent.box.storage.city}, {rent.box.storage.address} "
        f"истекает сегодня {rent.end_date.date()}.\n\n"
        f"Пожалуйста, свяжитесь с нами для продления аренды или освобождения бокса."
    )

    return subject, message


def create_notif_end_rent_message(rent, time_insert: str) -> tuple[str, str]:
    """
    Создает тему письма (subject) и текст сообщения (message) напоминание об окончании аренды

    """
    subject = f"Напоминание: окончание аренды №{rent.pk} бокса"
    message = (
        f"Напоминаем, что срок аренды вашего бокса на складе "
        f"{rent.box.storage.city}, {rent.box.storage.address} "
        f"истекает через {time_insert} {rent.end_date.date()}.\n\n"
    )

    return subject, message


def create_reminder_for_overdue_rent_message(rent) -> tuple[str, str]:
    """
    Создает тему письма (subject) и текст сообщения (message) напоминание об просроченной аренде

    """
    subject = f"Напоминание: просрочен срок аренды №{rent.pk} бокса"
    message = (
        f"Напоминаем, что срок аренды вашего бокса на складе "
        f"{rent.box.storage.city}, {rent.box.storage.address} "
        f"истек {rent.end_date.date()}.\n\n"
        "Ваши будут храниться 6 месяцев по повышенному тарифу. "
        "В случае, если вы не заберете в течении этого срока то можете потерять их."
    )

    return subject, message
