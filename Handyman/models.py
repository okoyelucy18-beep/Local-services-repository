
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="providers",
    )
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to="providers/",
        blank=True,
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "provider_detail",
            kwargs={"pk": self.pk},
        )

