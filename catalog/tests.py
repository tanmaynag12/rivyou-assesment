from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Product

User = get_user_model()


class ProductCRUDTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="cataloguser",
            email="catalog@example.com",
            password="testpass123",
        )
        cls.product = Product.objects.create(
            product_name="Pixel 8 Pro",
            description="High-performance flagship device",
            category=Product.Category.SMARTPHONES,
            tags=["camera", "5g"],
        )

    def setUp(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "cataloguser", "password": "testpass123"},
            format="json",
        )
        self.token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_list_products(self):
        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_name"], "Pixel 8 Pro")

    def test_create_product(self):
        response = self.client.post(
            reverse("product-list"),
            {
                "product_name": "Fast USB-C Charger",
                "description": "Reliable fast charging adapter",
                "category": Product.Category.CHARGERS,
                "tags": [" Fast-Charging ", "USB-C"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tags"], ["fast-charging", "usb-c"])
        self.assertTrue(
            Product.objects.filter(product_name="Fast USB-C Charger").exists()
        )

    def test_create_product_validation_error(self):
        response = self.client.post(
            reverse("product-list"),
            {
                "product_name": "",
                "description": "Missing name",
                "category": Product.Category.CHARGERS,
                "tags": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_product(self):
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.product.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.product.pk)
        self.assertEqual(response.data["category"], Product.Category.SMARTPHONES)

    def test_update_product(self):
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.product.pk}),
            {
                "product_name": "Pixel 8 Pro Max",
                "description": "Updated flagship device",
                "category": Product.Category.SMARTPHONES,
                "tags": ["Camera", "5G"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["product_name"], "Pixel 8 Pro Max")
        self.assertEqual(response.data["tags"], ["camera", "5g"])

        self.product.refresh_from_db()
        self.assertEqual(self.product.product_name, "Pixel 8 Pro Max")

    def test_partial_update_product(self):
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.product.pk}),
            {"product_name": "Pixel 8"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["product_name"], "Pixel 8")
        self.assertEqual(response.data["description"], self.product.description)

    def test_delete_product(self):
        response = self.client.delete(
            reverse("product-detail", kwargs={"pk": self.product.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_retrieve_missing_product_returns_404(self):
        response = self.client.get(reverse("product-detail", kwargs={"pk": 99999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(
            reverse("product-list"),
            {
                "product_name": "Unauthorized Product",
                "description": "Should not be created",
                "category": Product.Category.CHARGERS,
                "tags": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
