from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def main_page(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def boxes(request: HttpRequest) -> HttpResponse:
    return render(request, "boxes.html")


def faq(request: HttpRequest) -> HttpResponse:
    return render(request, "faq.html")


def my_rent(request: HttpRequest) -> HttpResponse:
    return render(request, "my-rent.html")
