
from django.contrib import admin

from .models import Category, Review, ServiceProvider


# 1. Create an inline manager for the child categories
class ChildCategoryInline(admin.TabularInline):
    model = Category
    # 'children' comes from the related_name='children' in your models.py ForeignKey
    fk_name = 'parent' 
    extra = 1  # Shows 1 empty row by default to quickly add a new child
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
      
    # Sidebar filters to easily narrow down categories
    list_filter = ('parent',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug") 
    autocomplete_fields = ("parent",)

   # Inline manager for child categories
    inlines = [ChildCategoryInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('provider', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'provider')
    search_fields = ('comment', 'provider__name', 'user__username')


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

