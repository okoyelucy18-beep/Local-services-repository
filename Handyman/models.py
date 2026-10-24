
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} --> {self.name}"
        return self.name


class ServiceProvider(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="providers",
    )
    description = models.TextField()
    address = models.CharField(max_length=255)
    state = models.CharField(
        max_length=100,
        default="Anambra",
        db_index=True,
    )
    city = models.CharField(max_length=100, db_index=True)
    neighborhood = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to="providers/",
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    is_verified = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_providers',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.status == 'approved':
            self.is_verified = True
        elif self.status != 'approved':
            self.is_verified = False
        super().save(*args, **kwargs)

    def average_rating(self):
        result = self.reviews.aggregate(avg_rating=Avg('rating'))
        value = result.get('avg_rating')
        return value if value is not None else 0.0

    def review_count(self):
        return self.reviews.count()

    def get_absolute_url(self):
        return reverse(
            "provider_detail",
            kwargs={"pk": self.pk},
        )


class Review(models.Model):
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'user'],
                name='unique_provider_review_per_user',
            )
        ]

    def __str__(self):
        return f'{self.user} rated {self.provider} {self.rating}/5'
