from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReviewForm, ServiceProviderRegistrationForm
from .models import Category, Review, ServiceProvider


def home(request):
    provider_count = ServiceProvider.objects.filter(status='approved').count()

    return render(
        request,
        "Handyman/home.html",
        {"provider_count": provider_count},
    )


def explore_services(request):
    providers = ServiceProvider.objects.filter(status='approved')

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
        providers = providers.filter(
            neighborhood__icontains=neighborhood
        )

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


def provider_detail(request, pk):
    provider = get_object_or_404(
        ServiceProvider.objects.select_related("category"),
        pk=pk,
        status='approved',
    )
    reviews = provider.reviews.select_related("user").order_by("-created_at")

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
        status='approved',
    )

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(
                provider=provider,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment'],
                },
            )
            if not created:
                review.rating = form.cleaned_data['rating']
                review.comment = form.cleaned_data['comment']
                review.save()
            messages.success(request, 'Thanks for your review.')
            return redirect('provider_detail', pk=provider.pk)
    else:
        form = ReviewForm()

    return render(
        request,
        'Handyman/provider_detail.html',
        {
            'provider': provider,
            'reviews': provider.reviews.select_related('user').order_by('-created_at'),
            'average_rating': provider.average_rating(),
            'review_count': provider.review_count(),
            'review_form': form,
        },
    )

@login_required(login_url="login")
def register_provider(request):
    if request.method == "POST":
        form = ServiceProviderRegistrationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            provider = form.save(commit=False)
            provider.owner = request.user
            provider.status = 'pending'
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
    providers = ServiceProvider.objects.filter(owner=request.user).order_by('-created_at')
    return render(
        request,
        "Handyman/dashboard.html",
        {"providers": providers},
    )


@login_required(login_url="login")
def admin_review_queue(request):
    providers = ServiceProvider.objects.filter(status='pending').order_by('-created_at')
    return render(
        request,
        "Handyman/admin_review_queue.html",
        {"providers": providers},
    )


@login_required(login_url="login")
def approve_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.status = 'approved'
    provider.is_verified = True
    provider.save()
    messages.success(request, f'{provider.name} has been approved and is now live.')
    return redirect('admin_review_queue')


@login_required(login_url="login")
def reject_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.status = 'rejected'
    provider.is_verified = False
    provider.save()
    messages.success(request, f'{provider.name} has been marked as rejected.')
    return redirect('admin_review_queue')


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
