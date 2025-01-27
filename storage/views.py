from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Min, Max, Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
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

            return redirect("success_rent")
    else:
        rent_form = RentForm()

    storages = Storage.objects.all()
    for storage in storages:
        storage.total_boxes = storage.boxes.count()
        storage.occupied_boxes = (
            storage.boxes.filter(rents__status="active").distinct().count()
        )
        storage.available_boxes = storage.total_boxes - storage.occupied_boxes
        storage.min_price = storage.boxes.aggregate(Min("price"))["price__min"]
        storage.max_height = storage.boxes.aggregate(Max("height"))["height__max"]

    context = {
        "storages": storages,
        "rent_form": rent_form,
    }
    return render(request, "boxes.html", context)


def get_boxes(request: HttpRequest, storage_id: int) -> JsonResponse:
    free_boxes = Box.objects.filter(storage_id=storage_id, is_occupied=False)
    box_data = [
        {
            "id": box.id,
            "number": box.number,
            "area": box.area,
            "price": box.price,
            "level": box.level,
            "length": box.length,
            "width": box.width,
            "height": box.height,
        }
        for box in free_boxes
    ]

    return JsonResponse({"boxes": box_data}, safe=False)


def faq(request: HttpRequest) -> HttpResponse:
    return render(request, "faq.html")


def success_rent(request: HttpRequest) -> HttpResponse:
    return render(request, "success_rent.html")


def my_rent(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=user_id)
    rents = user.rents.select_related("box", "box__storage").all()

    # Группируем аренды по складам
    grouped_rents = defaultdict(list)
    for rent in rents:
        storage = rent.box.storage
        rent.is_near_end = (rent.end_date - timezone.now()) <= timedelta(days=7)
        grouped_rents[storage].append(rent)

    context = {"grouped_rents": dict(grouped_rents), "user": user}

    return render(request, "my-rent.html", context)
