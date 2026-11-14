from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm, ServiceProviderRegistrationForm, VendorSubmissionForm
from .models import Category, Review, ServiceProvider


def superuser_only(user):
	return user.is_active and user.is_superuser


def home(request):
	return render(
		request,
		"Handyman/home.html",
	)


def explore_services(request):
	providers = ServiceProvider.objects.filter(status="approved")

	search_query = request.GET.get("q", "").strip()
	state = request.GET.get("state", "").strip()
	city = request.GET.get("city", "").strip()
	neighborhood = request.GET.get("neighborhood", "").strip()
	category_id = request.GET.get("category", "").strip()

	if search_query:
		providers = providers.filter(
			Q(name__icontains=search_query)
			| Q(description__icontains=search_query)
			| Q(category__name__icontains=search_query)
		)

	if state:
		providers = providers.filter(state__icontains=state)

	if city:
		providers = providers.filter(city__icontains=city)

	if neighborhood:
		providers = providers.filter(neighborhood__icontains=neighborhood)

	if category_id.isdigit():
		providers = providers.filter(category_id=int(category_id))

	context = {
		"providers": providers,
		"categories": Category.objects.all(),
		"search_query": search_query,
		"selected_state": state,
		"selected_city": city,
		"selected_neighborhood": neighborhood,
		"selected_category": category_id,
	}

	return render(request, "Handyman/explore_services.html", context)


def find_nearby(request):
	providers = ServiceProvider.objects.filter(status="approved").select_related("category")
	service_query = request.GET.get("service", "").strip()
	location_query = request.GET.get("location", "").strip()

	if service_query:
		providers = providers.filter(
			Q(name__icontains=service_query)
			| Q(description__icontains=service_query)
			| Q(category__name__icontains=service_query)
		)

	location_terms = [term.strip() for term in location_query.split(",") if term.strip()]
	for term in location_terms:
		if term.lower().startswith(("near ", "in ")):
			term = term.split(" ", 1)[1].strip()
		if term:
			providers = providers.filter(
				Q(address__icontains=term)
				| Q(neighborhood__icontains=term)
				| Q(city__icontains=term)
				| Q(state__icontains=term)
			)

	return render(
		request,
		"Handyman/find_nearby.html",
		{
			"providers": providers.distinct(),
			"service_query": service_query,
			"location_query": location_query,
		},
	)


def provider_detail(request, pk):
	provider = get_object_or_404(
		ServiceProvider.objects.select_related("category"),
		pk=pk,
		status="approved",
	)
	reviews = provider.reviews.filter(is_hidden=False).select_related("user").order_by("-created_at")

	return render(
		request,
		"Handyman/provider_detail.html",
		{
			"provider": provider,
			"reviews": reviews,
			"average_rating": provider.average_rating(),
			"review_count": provider.review_count(),
			"review_form": ReviewForm(),
		},
	)


@login_required(login_url="login")
def add_review(request, pk):
	provider = get_object_or_404(
		ServiceProvider.objects.select_related("category"),
		pk=pk,
		status="approved",
	)

	if request.method == "POST":
		form = ReviewForm(request.POST)
		if form.is_valid():
			review, created = Review.objects.get_or_create(
				provider=provider,
				user=request.user,
				defaults={
					"rating": form.cleaned_data["rating"],
					"comment": form.cleaned_data["comment"],
				},
			)
			if not created:
				review.rating = form.cleaned_data["rating"]
				review.comment = form.cleaned_data["comment"]
				review.save()
			messages.success(request, "Thanks for your review.")
			return redirect("provider_detail", pk=provider.pk)
	else:
		form = ReviewForm()

	return render(
		request,
		"Handyman/provider_detail.html",
		{
			"provider": provider,
			"reviews": provider.reviews.filter(is_hidden=False).select_related("user").order_by("-created_at"),
			"average_rating": provider.average_rating(),
			"review_count": provider.review_count(),
			"review_form": form,
		},
	)


@login_required(login_url="login")
def register_provider(request):
	if request.method == "POST":
		form = ServiceProviderRegistrationForm(request.POST, request.FILES)

		if form.is_valid():
			provider = form.save(commit=False)
			provider.owner = request.user
			provider.status = "pending"
			provider.is_verified = False
			provider.save()
			messages.success(
				request,
				"Your business listing has been submitted for review.",
			)
			return redirect("dashboard")
	else:
		form = ServiceProviderRegistrationForm()

	return render(
		request,
		"Handyman/provider_register.html",
		{"form": form},
	)


@login_required(login_url="login")
def dashboard(request):
	providers = ServiceProvider.objects.filter(owner=request.user).order_by("-created_at")
	return render(
		request,
		"Handyman/dashboard.html",
		{"providers": providers},
	)


@user_passes_test(superuser_only, login_url="login")
def admin_review_queue(request):
	providers = ServiceProvider.objects.filter(status="pending").order_by("-created_at")
	return render(
		request,
		"Handyman/admin_review_queue.html",
		{"providers": providers},
	)


@user_passes_test(superuser_only, login_url="login")
@require_POST
def approve_provider(request, pk):
	provider = get_object_or_404(ServiceProvider, pk=pk)
	provider.status = "approved"
	provider.is_verified = True
	provider.save()
	messages.success(request, f"{provider.name} has been approved and is now live.")
	return redirect("admin_review_queue")


@user_passes_test(superuser_only, login_url="login")
@require_POST
def reject_provider(request, pk):
	provider = get_object_or_404(ServiceProvider, pk=pk)
	provider.status = "rejected"
	provider.is_verified = False
	provider.save()
	messages.success(request, f"{provider.name} has been marked as rejected.")
	return redirect("admin_review_queue")


def signup(request):
	if request.user.is_authenticated:
		return redirect("provider_register")

	next_url = request.GET.get("next") or "provider_register"

	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(
				request,
				"Your account was created successfully.",
			)
			return redirect(next_url)
	else:
		form = UserCreationForm()

	return render(
		request,
		"registration/signup.html",
		{"form": form, "next": next_url},
	)


def dynamic_login_view(request):
	"""Handles smart redirection to admin or home depending on user authority."""
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
				if user.is_superuser:
					return redirect("directory_admin_dashboard")
				return redirect("handyman_home")
	else:
		form = AuthenticationForm()

	return render(request, "registration/login.html", {"form": form})


def public_directory(request):
	"""Public directory view for browsing approved providers."""
	categories = Category.objects.all().order_by("name")
	approved_listings = ServiceProvider.objects.filter(status="approved").order_by("-created_at")

	category_slug = request.GET.get("category")
	if category_slug:
		approved_listings = approved_listings.filter(category__slug=category_slug)

	context = {
		"categories": categories,
		"providers": approved_listings,
		"selected_category": category_slug,
	}
	return render(request, "Handyman/explore_services.html", context)


@login_required(login_url="/login/")
def submit_handyman_business(request):
	"""Public business registration entry point."""
	if request.method == "POST":
		form = VendorSubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			business = form.save(commit=False)
			business.owner = request.user
			business.status = "pending"
			business.is_verified = False
			business.save()
			messages.success(request, "Your business listing has been submitted for review.")
			return redirect("dashboard")
	else:
		form = VendorSubmissionForm()

	return render(request, "Handyman/provider_register.html", {"form": form})
