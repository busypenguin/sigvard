from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Min, Max, Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm, UserLoginForm, RentForm
from .models import Storage, Rent, Box


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """

    form_class = UserRegisterForm
    success_url = reverse_lazy("main_page")
    template_name = "index.html"

    def form_valid(self, form):
        user = form.instance
        # Если username не заполнен, устанавливаем его равным части email до "@"
        if not form.cleaned_data.get("username"):
            user.username = form.cleaned_data.get("email").split("@")[0]

        # Связывает существующие заказы с указанным пользователем,
        # если они были оформлены на email, использованный при регистрации.
        user.save()
        Rent.objects.filter(Q(email=user.email) & Q(user__isnull=True)).update(
            user=user
        )

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
    random_storage = Storage.objects.order_by("?").first()
    storage_data = None
    if random_storage:
        storage_data = random_storage.boxes.aggregate(
            total_boxes=Count("id"),
            free_boxes=Count("id", filter=Q(is_occupied=False)),
            min_price=Min("price"),
            max_height=Max("height"),
        )
    context = {"storage": random_storage, "storage_data": storage_data}
    return render(request, "index.html", context)


def boxes(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        rent_form = RentForm(request.POST)
        if rent_form.is_valid():
            rent_form.save()
            return redirect("my_rent")
    else:
        rent_form = RentForm()

    boxes_to3 = []
    boxes_to10 = []
    boxes_from10 = []
    storages = Storage.objects.all()
    boxes = Box.objects.all()
    for box in boxes:
        if box.area < 3:
            boxes_to3.append(box)
        elif box.area < 10:
            boxes_to10.append(box)
        elif box.area > 10:
            boxes_from10.append(box)

    context = {
        "storages": storages,
        "rent_form": rent_form,
        "boxes": boxes,
        "boxes_to3": boxes_to3,
        "boxes_to10": boxes_to10,
        "boxes_from10": boxes_from10
        }
    return render(request, "boxes.html", context)


def faq(request: HttpRequest) -> HttpResponse:
    return render(request, "faq.html")


def my_rent(request: HttpRequest) -> HttpResponse:
    return render(request, "my-rent.html")
