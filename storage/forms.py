from datetime import date

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from .messages import create_end_rent_message
from .models import Rent, Box
from .tasks import send_email_message_task


class RentForm(forms.ModelForm):
    """
    Форма аренды бокса.
    """

    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "placeholder": "E-mail",
            }
        ),
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "type": "date",
            }
        ),
        label="Дата начала аренды",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "type": "date",
            }
        ),
        label="Дата окончания аренды",
    )
    pickup_address = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "placeholder": "Введите адрес, откуда нужно забрать груз",
                "rows": 3,
            }
        ),
    )
    box = forms.ModelChoiceField(
        label="",
        queryset=Box.objects.filter(is_occupied=False),
        widget=forms.Select(
            attrs={
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
            }
        ),
    )

    class Meta:
        model = Rent
        fields = ["email", "start_date", "end_date", "pickup_address", "box"]

    def clean(self):
        """
        Проверка корректности дат и их логики.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date < date.today():
                raise forms.ValidationError(
                    "Дата начала аренды не может быть в прошлом."
                )
            if end_date <= start_date:
                raise forms.ValidationError(
                    "Дата окончания аренды должна быть позже даты начала."
                )

        return cleaned_data

    def save(self, commit=True):
        rent = super().save(commit)
        if commit:
            # Запланировать задачу отправки письма в конце срока аренды
            subject, message = create_end_rent_message(rent)
            delay = (rent.end_date - now()).total_seconds()
            send_email_message_task.apply_async(
                (subject, message, rent.email), countdown=delay
            )

        return rent


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        """
        Проверка email на уникальность
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такой email уже используется в системе")
        return email

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "E-mail",
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "autocomplete": "off",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Пароль",
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "autocomplete": "off",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Подтверждение пароля",
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "autocomplete": "off",
            }
        )


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации на сайте через email
    """

    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "E-mail",
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "autocomplete": "off",
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Пароль",
                "class": "form-control border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey",
                "autocomplete": "off",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Введен некорректный email или пароль.",
        "inactive": "Этот аккаунт неактивен.",
    }

    def clean(self):
        """
        Проверяем данные и аутентифицируем пользователя через email
        """
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
