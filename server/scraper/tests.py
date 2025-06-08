import os
from typing import Any, Dict

from django.urls import reverse
from rest_framework import status  # type: ignore
from rest_framework.test import APITestCase  # type: ignore
from rest_framework.response import Response  # type: ignore

from .models import Brand, Product

BRAND_NAME: str = os.getenv("BRAND_NAME", "iPhone")


class ProductListAPIViewTest(APITestCase):
    brand: Brand

    @classmethod
    def setUpTestData(cls) -> None:
        cls.brand = Brand.objects.create(name=BRAND_NAME)

        for i in range(15):
            Product.objects.create(
                name=f"iPhone Product {i+1}",
                asin=f"ASIN{i+1:03d}",
                sku=f"SKU{i+1:03d}",
                image=f"http://example.com/image{i+1}.jpg",
                brand=cls.brand,
            )

    def test_pagination(self) -> None:
        url: str = reverse("product_list")
        response: Response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        response = self.client.get(url, {"page": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    def test_filter_by_brand(self) -> None:
        url: str = reverse("product_list")
        response: Response = self.client.get(url, {"brand__name": BRAND_NAME})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["results"][0]["brand_name"], self.brand.name)

    def test_search_by_name(self) -> None:
        url: str = reverse("product_list")
        response: Response = self.client.get(url, {"search": "Product 1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertIn("Product 1", item["name"])

    def test_search_by_asin(self) -> None:
        url: str = reverse("product_list")
        response: Response = self.client.get(url, {"search": "ASIN008"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["asin"], "ASIN008")


class BrandListViewTest(APITestCase):
    url: str
    brand1: Brand
    brand2: Brand
    brand3: Brand

    def setUp(self) -> None:
        self.url = reverse("brand-list")
        self.brand1 = Brand.objects.create(name="Apple")
        self.brand2 = Brand.objects.create(name="Samsung")
        self.brand3 = Brand.objects.create(name="Sony")

    def test_list_brands(self) -> None:
        response: Response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Dict[str, Any] = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 3)

    def test_brand_pagination(self) -> None:
        for i in range(10):
            Brand.objects.create(name=f"Brand {i}")

        response: Response = self.client.get(f"{self.url}?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Dict[str, Any] = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 10)

    def test_search_brands(self) -> None:
        response: Response = self.client.get(f"{self.url}?search=Sony")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Dict[str, Any] = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "Sony")

    def test_search_no_results(self) -> None:
        response: Response = self.client.get(f"{self.url}?search=NonExistentBrand")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Dict[str, Any] = response.json()
        self.assertEqual(len(data["results"]), 0)
