from django.urls import path

from storage import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("boxes/", views.boxes, name="boxes"),
    path("faq/", views.faq, name="faq"),
    path("my-rent/", views.my_rent, name="my_rent"),
]
