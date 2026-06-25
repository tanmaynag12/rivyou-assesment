from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        SMARTPHONES = "Smartphones", "Smartphones"
        CHARGERS = "Chargers", "Chargers"
        BACK_COVERS = "Back Covers", "Back Covers"

    product_name = models.CharField(max_length=255)
    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        db_index=True,
    )

    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Products"
        indexes = [
            GinIndex(fields=["tags"]),
        ]

    def __str__(self):
        return self.product_name