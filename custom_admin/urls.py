from django.urls import path

from . import admin, views

urlpatterns = [
    path("dashboard/", views.directory_dashboard, name="directory_admin_dashboard"),
    path("users/", admin.user_list, name="directory_admin_users"),
    path("users/add/", admin.add_user, name="directory_admin_add_user"),
    path("users/<int:pk>/edit/", admin.edit_user, name="directory_admin_edit_user"),
    path("users/<int:pk>/active/", admin.toggle_user_active, name="directory_admin_toggle_user_active"),
    path("users/<int:pk>/delete/", admin.delete_user, name="directory_admin_delete_user"),
    path("approve/<int:pk>/", views.approve_provider, name="custom_admin_approve_provider"),
    path("review/toggle/<int:pk>/", views.toggle_review_visibility, name="toggle_review_visibility"),
    path("category/add/", views.add_category, name="add_category"),
    path("provider/edit/<int:pk>/", views.edit_provider, name="edit_provider"),
    path("provider/delete/<int:pk>/", views.delete_provider, name="delete_provider"),
    path("category/edit/<int:pk>/", views.edit_category, name="edit_category"),
    path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),
]
 