import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Product


class Command(BaseCommand):
    help = "Import products from CSV file"

    VALID_CATEGORIES = {
        "Smartphones",
        "Chargers",
        "Back Covers",
    }

    def handle(self, *args, **options):
        csv_path = settings.BASE_DIR / "data" / "products.csv"

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        created = 0
        updated = 0
        skipped = 0

        with transaction.atomic():
            with open(csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        product_id = int(row["id"].strip())
                        product_name = row["product_name"].strip()
                        description = row["product_description"].strip()
                        category = row["category"].strip()
                        tags = row["tags"].strip()

                        if not product_name or not description or not category:
                            self.stderr.write(
                                f"Row {row_num}: Missing required fields"
                            )
                            skipped += 1
                            continue

                        if category not in self.VALID_CATEGORIES:
                            self.stderr.write(
                                f"Row {row_num}: Invalid category '{category}'"
                            )
                            skipped += 1
                            continue

                        normalized_tags = [
                            tag.strip().lower()
                            for tag in tags.split(",")
                            if tag.strip()
                        ]

                        _, is_created = Product.objects.update_or_create(
                            id=product_id,
                            defaults={
                                "product_name": product_name,
                                "description": description,
                                "category": category,
                                "tags": normalized_tags,
                            },
                        )

                        if is_created:
                            created += 1
                        else:
                            updated += 1

                    except Exception as exc:
                        self.stderr.write(
                            f"Row {row_num}: {exc}"
                        )
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: "
                f"Created {created} | "
                f"Updated {updated} | "
                f"Skipped {skipped}"
            )
        )