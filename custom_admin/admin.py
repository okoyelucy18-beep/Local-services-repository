from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AdminUserCreationForm, AdminUserForm


def superuser_only(user):
	return user.is_active and user.is_superuser


def is_last_active_superuser(user):
	return (
		user.is_active
		and user.is_superuser
		and get_user_model().objects.filter(is_active=True, is_superuser=True).count() <= 1
	)


@user_passes_test(superuser_only, login_url="/login/")
def user_list(request):
	users = get_user_model().objects.all().order_by("username")
	return render(request, "custom_admin/user_list.html", {"users": users})


@user_passes_test(superuser_only, login_url="/login/")
def add_user(request):
	if request.method == "POST":
		form = AdminUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.success(request, f"Account {user.username} has been created.")
			return redirect("directory_admin_users")
	else:
		form = AdminUserCreationForm()
	return render(
		request,
		"custom_admin/manage_form.html",
		{"form": form, "title": "Create User Account"},
	)


@user_passes_test(superuser_only, login_url="/login/")
def edit_user(request, pk):
	user = get_object_or_404(get_user_model(), pk=pk)
	if request.method == "POST":
		form = AdminUserForm(request.POST, instance=user)
		if form.is_valid():
			would_remove_admin_access = not (
				form.cleaned_data["is_active"] and form.cleaned_data["is_superuser"]
			)
			if user.pk == request.user.pk and would_remove_admin_access:
				form.add_error(None, "You cannot remove your own active superuser access.")
			elif is_last_active_superuser(user) and would_remove_admin_access:
				form.add_error(None, "The last active superuser cannot be deactivated or demoted.")
			else:
				form.save()
				messages.success(request, f"Account {user.username} has been updated.")
				return redirect("directory_admin_users")
	else:
		form = AdminUserForm(instance=user)
	return render(
		request,
		"custom_admin/manage_form.html",
		{
			"form": form,
			"title": f"Edit Account: {user.username}",
			"cancel_url": "directory_admin_users",
		},
	)


@user_passes_test(superuser_only, login_url="/login/")
@require_POST
def toggle_user_active(request, pk):
	user = get_object_or_404(get_user_model(), pk=pk)
	if user.pk == request.user.pk:
		messages.error(request, "You cannot deactivate your own account.")
	elif is_last_active_superuser(user):
		messages.error(request, "The last active superuser cannot be deactivated.")
	else:
		user.is_active = not user.is_active
		user.save(update_fields=["is_active"])
		state = "activated" if user.is_active else "deactivated"
		messages.success(request, f"Account {user.username} has been {state}.")
	return redirect("directory_admin_users")


@user_passes_test(superuser_only, login_url="/login/")
def delete_user(request, pk):
	user = get_object_or_404(get_user_model(), pk=pk)
	if request.method == "POST":
		if user.pk == request.user.pk:
			messages.error(request, "You cannot delete your own account.")
		elif is_last_active_superuser(user):
			messages.error(request, "The last active superuser cannot be deleted.")
		else:
			username = user.username
			user.delete()
			messages.success(request, f"Account {username} has been deleted.")
		return redirect("directory_admin_users")
	return render(
		request,
		"custom_admin/confirm_user_delete.html",
		{"user_to_delete": user},
	)
