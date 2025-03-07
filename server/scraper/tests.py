import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product, Brand
from .serializers import ProductSerializer

BRAND_NAME = os.getenv('BRAND_NAME', 'iPhone')

class ProductListAPIViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a brand
        cls.brand = Brand.objects.create(name=BRAND_NAME)

        # Create 15 products for testing pagination
        for i in range(15):
            Product.objects.create(
                name=f"iPhone Product {i+1}",
                asin=f"ASIN{i+1:03d}",
                sku=f"SKU{i+1:03d}",
                image=f"http://example.com/image{i+1}.jpg",
                brand=cls.brand
            )

    def test_pagination(self):
        url = reverse('product_list')
        
        # Request the first page
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Check page size
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        # Request the second page
        response = self.client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Remaining items on the second page

    def test_filter_by_brand(self):
        url = reverse('product_list')
        
        # Filter by brand name
        response = self.client.get(url, {'brand__name': BRAND_NAME})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Page size
        self.assertEqual(response.data['results'][0]['brand_name'], self.brand.name)

    def test_search_by_name(self):
        url = reverse('product_list')
        
        # Search by name containing "Product 1"
        response = self.client.get(url, {'search': 'Product 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the search returned relevant results
        for item in response.data['results']:
            self.assertIn('Product 1', item['name'])

    def test_search_by_asin(self):
        url = reverse('product_list')
        
        # Search by ASIN
        response = self.client.get(url, {'search': 'ASIN008'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the result has the specific ASIN
        self.assertEqual(response.data['results'][0]['asin'], 'ASIN008')


class BrandListViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("brand-list") 

        # Create sample brands
        self.brand1 = Brand.objects.create(name="Apple")
        self.brand2 = Brand.objects.create(name="Samsung")
        self.brand3 = Brand.objects.create(name="Sony")

    def test_list_brands(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)  # Ensure paginated response
        self.assertGreaterEqual(len(data["results"]), 3)  # At least 3 brands

    def test_brand_pagination(self):
        for i in range(10):  # Add more brands
            Brand.objects.create(name=f"Brand {i}")

        response = self.client.get(f"{self.url}?page=1&page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 10)  # Should return 10 per page

    def test_search_brands(self):
        response = self.client.get(f"{self.url}?search=Sony")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 1)  # Should return Sony brand only
        self.assertEqual(data["results"][0]["name"], "Sony")

    def test_search_no_results(self):
        response = self.client.get(f"{self.url}?search=NonExistentBrand")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 0)  # Should return no results
