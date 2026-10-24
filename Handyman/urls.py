
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.explore_services, name="explore_services"),

    path(
        "provider/<int:pk>/",
        views.provider_detail,
        name="provider_detail",
    ),

    path(
        "provider/<int:pk>/review/",
        views.add_review,
        name="add_review",
    ),

    path(
        "register/",
        views.register_provider,
        name="provider_register",
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "admin/review-queue/",
        views.admin_review_queue,
        name="admin_review_queue",
    ),

    path(
        "admin/approve/<int:pk>/",
        views.approve_provider,
        name="approve_provider",
    ),

    path(
        "admin/reject/<int:pk>/",
        views.reject_provider,
        name="reject_provider",
    ),

    path(
        "signup/",
        views.signup,
        name="signup",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
