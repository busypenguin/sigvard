from .models import Rent


def create_confirm_rent_message(rent: Rent) -> tuple[str, str]:
    """
    Создает тему письма (subject) и текст сообщения (message) подтверждения аренды бокса

    """
    subject = f"Ваш заказ аренды №{rent.pk} принят"
    message = (
        f"Аренда бокса {rent.box} с {rent.start_date.date()} по {rent.end_date.date()}. "
        f"Адрес самовывоза груза: {rent.pickup_address}"
    )

    return subject, message
