from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from Handyman.models import Category, Review, ServiceProvider

from .forms import AdminCategoryForm, AdminProviderForm


def superuser_only(user):
    return user.is_active and user.is_superuser


@user_passes_test(superuser_only, login_url="/login/")
def directory_dashboard(request):
    pending_listings = ServiceProvider.objects.filter(status="pending").order_by("-created_at")
    approved_listings = ServiceProvider.objects.filter(status="approved").order_by("name")
    recent_reviews = Review.objects.all().order_by("-created_at")[:15]
    categories = Category.objects.all().order_by("name")

    context = {
        "pending_listings": pending_listings,
        "approved_listings": approved_listings,
        "recent_reviews": recent_reviews,
        "categories": categories,
    }
    return render(request, "custom_admin/directory_dashboard.html", context)


@user_passes_test(superuser_only, login_url="/login/")
@require_POST
def approve_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.status = "approved"
    provider.is_verified = True
    provider.save()
    messages.success(request, f"{provider.name} has been approved and is now live.")
    return redirect("directory_admin_dashboard")


@user_passes_test(superuser_only, login_url="/login/")
@require_POST
def toggle_review_visibility(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_hidden = not review.is_hidden
    review.save(update_fields=["is_hidden"])
    visibility = "hidden" if review.is_hidden else "visible"
    messages.success(request, f"Review is now {visibility}.")
    return redirect("directory_admin_dashboard")


@user_passes_test(superuser_only, login_url="/login/")
def add_category(request):
    if request.method == "POST":
        form = AdminCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("directory_admin_dashboard")
    else:
        form = AdminCategoryForm()
    return render(
        request,
        "custom_admin/manage_form.html",
        {"form": form, "title": "Create New Category"},
    )


@user_passes_test(superuser_only, login_url="/login/")
def edit_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    if request.method == "POST":
        form = AdminProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return redirect("directory_admin_dashboard")
    else:
        form = AdminProviderForm(instance=provider)
    return render(
        request,
        "custom_admin/manage_form.html",
        {"form": form, "title": f"Edit: {provider.name}"},
    )


@user_passes_test(superuser_only, login_url="/login/")
@require_POST
def delete_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.delete()
    return redirect("directory_admin_dashboard")


@user_passes_test(superuser_only, login_url="/login/")
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = AdminCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("directory_admin_dashboard")
    else:
        form = AdminCategoryForm(instance=category)
    return render(
        request,
        "custom_admin/manage_form.html",
        {"form": form, "title": f"Edit Category: {category.name}"},
    )


@user_passes_test(superuser_only, login_url="/login/")
@require_POST
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect("directory_admin_dashboard")
