
from django.contrib import admin
from .models import Category, ServiceProvider


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "city",
        "is_verified",
        "created_at",
    )
    list_filter = ("category", "city", "is_verified")
    search_fields = ("name", "city", "address")
    list_editable = ("is_verified",)

