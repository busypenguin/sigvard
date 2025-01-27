from django.urls import path

from storage import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("boxes/", views.boxes, name="boxes"),
    path("faq/", views.faq, name="faq"),
    path("success_rent/", views.success_rent, name="success_rent"),
    path("my-rent/<int:user_id>/", views.my_rent, name="my_rent"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("get_boxes/<int:storage_id>/", views.get_boxes, name="get_boxes"),
]
