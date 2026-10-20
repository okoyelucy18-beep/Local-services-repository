
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Category, ServiceProvider
from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import render
from .forms import ServiceProviderRegistrationForm



def register_provider(request):
    if request.method == "POST":
        form = ServiceProviderRegistrationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            provider = form.save(commit=False)

            # New listings must await administrator verification.
            provider.is_verified = False
            provider.save()

            messages.success(
                request,
                "Your business listing was submitted successfully "
                "and is awaiting administrator approval.",
            )
            return redirect("provider_register")
    else:
        form = ServiceProviderRegistrationForm()

    return render(
        request,
        "Handyman/provider_register.html",
        {"form": form},
    )

def home(request):
    providers = ServiceProvider.objects.filter(is_verified=True)

    search_query = request.GET.get("q", "").strip()
    state = request.GET.get("state", "").strip()
    city = request.GET.get("city", "").strip()
    neighborhood = request.GET.get("neighborhood", "").strip()
    category_id = request.GET.get("category", "").strip()

    # Search by service or business details
    if search_query:
        providers = providers.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # Filter by location
    if state:
        providers = providers.filter(state__icontains=state)

    if city:
        providers = providers.filter(city__icontains=city)

    if neighborhood:
        providers = providers.filter(
            neighborhood__icontains=neighborhood
        )

    # Filter by selected category
    if category_id.isdigit():
        providers = providers.filter(category_id=int(category_id))

    categories = Category.objects.all()

    context = {
        "providers": providers,
        "categories": categories,
        "search_query": search_query,
        "selected_state": state,
        "selected_city": city,
        "selected_neighborhood": neighborhood,
        "selected_category": category_id,
    }

    return render(request, "Handyman/home.html", context)

def provider_detail(request, pk):
    provider = get_object_or_404(
        ServiceProvider.objects.select_related("category"),
        pk=pk,
    )
    return render(
        request,
        "Handyman/provider_detail.html",
        {"provider": provider},
    )


