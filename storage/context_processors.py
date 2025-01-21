from django.http import HttpRequest

from storage.forms import UserRegisterForm, UserLoginForm


def auth_forms(request: HttpRequest) -> dict:
    """
    Добавляет формы регистрации и авторизации в контекст всех шаблонов
    """
    return {
        "register_form": UserRegisterForm(),
        "login_form": UserLoginForm(),
    }
