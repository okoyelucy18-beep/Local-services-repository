
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, ServiceProvider


def home(request):
    providers = ServiceProvider.objects.select_related(
        "category"
    ).all()
    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()

    if query:
        providers = providers.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id.isdigit():
        providers = providers.filter(category_id=int(category_id))

    if city:
        providers = providers.filter(city__icontains=city)

    context = {
        "providers": providers,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "city": city,
    }
    return render(request, "services/home.html", context)


def provider_detail(request, pk):
    provider = get_object_or_404(
        ServiceProvider.objects.select_related("category"),
        pk=pk,
    )
    return render(
        request,
        "services/provider_detail.html",
        {"provider": provider},
    )
