from rest_framework import serializers

from catalog.models import Product
from catalog.services import create_product, normalize_tags, update_product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "product_name",
            "description",
            "category",
            "tags",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_tags(self, value):
        return normalize_tags(value)

    def create(self, validated_data):
        return create_product(**validated_data)

    def update(self, instance, validated_data):
        return update_product(instance, partial=self.partial, **validated_data)
