from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Product
from search.services import (
    RANK_REASON_CATEGORY,
    RANK_REASON_DESCRIPTION,
    RANK_REASON_NAME,
    RANK_REASON_TAG,
    search_products,
)

User = get_user_model()


class SearchServiceTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.phone = Product.objects.create(
            product_name="Pixel 8 Pro",
            description="High-performance flagship device",
            category=Product.Category.SMARTPHONES,
            tags=["camera", "5g", "battery"],
        )
        cls.charger = Product.objects.create(
            product_name="Fast USB-C Charger",
            description="Reliable fast charging adapter",
            category=Product.Category.CHARGERS,
            tags=["fast-charging", "usb-c"],
        )
        cls.cover = Product.objects.create(
            product_name="Silicone Back Cover",
            description="Durable protection for smartphones",
            category=Product.Category.BACK_COVERS,
            tags=["protection", "silicone"],
        )

    def test_category_match_is_tier_one(self):
        results = search_products("Smartphones")

        phone_result = next(result for result in results if result["id"] == self.phone.id)
        self.assertEqual(phone_result["rank_reason"], RANK_REASON_CATEGORY)
        self.assertGreaterEqual(phone_result["relevance_score"], 0.70)

    def test_tag_match_is_tier_two(self):
        results = search_products("camera")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.phone.id)
        self.assertEqual(results[0]["rank_reason"], RANK_REASON_TAG)
        self.assertGreaterEqual(results[0]["relevance_score"], 0.40)
        self.assertLess(results[0]["relevance_score"], 0.70)

    def test_name_match_is_tier_three(self):
        results = search_products("Pixel")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.phone.id)
        self.assertEqual(results[0]["rank_reason"], RANK_REASON_NAME)
        self.assertLess(results[0]["relevance_score"], 0.40)

    def test_description_match_is_tier_three(self):
        results = search_products("flagship")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.phone.id)
        self.assertEqual(results[0]["rank_reason"], RANK_REASON_DESCRIPTION)

    def test_product_appears_only_in_highest_tier(self):
        results = search_products("charger")

        result_ids = [result["id"] for result in results]
        self.assertEqual(result_ids.count(self.charger.id), 1)
        self.assertEqual(results[0]["id"], self.charger.id)
        self.assertEqual(results[0]["rank_reason"], RANK_REASON_CATEGORY)

    def test_tier_ordering_is_preserved(self):
        results = search_products("smart")

        reasons = [result["rank_reason"] for result in results]
        category_index = reasons.index(RANK_REASON_CATEGORY)
        description_index = reasons.index(RANK_REASON_DESCRIPTION)

        self.assertLess(category_index, description_index)

    def test_case_insensitive_partial_matching(self):
        results = search_products("PIX")

        self.assertTrue(any(result["id"] == self.phone.id for result in results))

    def test_empty_query_returns_no_results(self):
        self.assertEqual(search_products(""), [])
        self.assertEqual(search_products("   "), [])


class SearchAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="searchuser",
            email="search@example.com",
            password="testpass123",
        )
        Product.objects.create(
            product_name="Pixel 8 Pro",
            description="High-performance flagship device",
            category=Product.Category.SMARTPHONES,
            tags=["camera", "5g"],
        )

    def setUp(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "searchuser", "password": "testpass123"},
            format="json",
        )
        self.token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_search_requires_query_parameter(self):
        response = self.client.get(reverse("search"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(reverse("search"), {"q": "Pixel"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_returns_ranked_results(self):
        response = self.client.get(reverse("search"), {"q": "Pixel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["query"], "Pixel")
        self.assertEqual(response.data["count"], 1)
        self.assertIn("relevance_score", response.data["results"][0])
        self.assertIn("rank_reason", response.data["results"][0])
