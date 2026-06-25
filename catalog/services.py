from catalog.models import Product


def normalize_tags(tags: list[str]) -> list[str]:
    return [tag.strip().lower() for tag in tags if tag.strip()]


def list_products():
    return Product.objects.all()


def get_product(product_id: int) -> Product:
    return Product.objects.get(pk=product_id)


def create_product(*, product_name: str, description: str, category: str, tags=None) -> Product:
    return Product.objects.create(
        product_name=product_name,
        description=description,
        category=category,
        tags=normalize_tags(tags or []),
    )


def update_product(product: Product, *, partial: bool = False, **fields) -> Product:
    if "tags" in fields:
        fields["tags"] = normalize_tags(fields["tags"])

    for field, value in fields.items():
        setattr(product, field, value)

    product.save()
    return product


def delete_product(product: Product) -> None:
    product.delete()
