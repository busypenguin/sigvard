from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm, UserLoginForm


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """

    form_class = UserRegisterForm
    success_url = reverse_lazy("main_page")
    template_name = "index.html"

    def form_valid(self, form):
        # Если username не заполнен, устанавливаем его равным части email до "@"
        if not form.cleaned_data.get("username"):
            form.instance.username = form.cleaned_data.get("email").split("@")[0]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация на сайте"
        if "register_form" not in context:
            context["register_form"] = self.get_form()
        return context

    def get_success_url(self):
        referer = self.request.META.get("HTTP_REFERER")
        return referer if referer else self.success_url


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация на сайте
    """

    form_class = UserLoginForm
    template_name = "index.html"
    success_url = reverse_lazy("main_page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Авторизация на сайте"
        if "login_form" not in context:
            context["login_form"] = self.get_form()
        return context

    def get_success_url(self):
        referer = self.request.META.get("HTTP_REFERER")
        return referer if referer else self.success_url


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """

    next_page = reverse_lazy("main_page")


def main_page(request: HttpRequest) -> HttpResponse:
    context = {"register_form": UserRegisterForm(), "login_form": UserLoginForm()}
    return render(request, "index.html", context)


def boxes(request: HttpRequest) -> HttpResponse:
    return render(request, "boxes.html")


def faq(request: HttpRequest) -> HttpResponse:
    context = {"register_form": UserRegisterForm(), "login_form": UserLoginForm()}
    return render(request, "faq.html", context)


def my_rent(request: HttpRequest) -> HttpResponse:
    return render(request, "my-rent.html")
