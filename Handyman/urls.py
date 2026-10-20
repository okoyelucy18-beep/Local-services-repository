
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "provider/<int:pk>/",
        views.provider_detail,
        name="provider_detail",
    ),
    path(
        "register/",
        views.register_provider,
        name="provider_register",),
]
