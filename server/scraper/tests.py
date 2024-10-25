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
        self.assertEqual(response.data['results'][0]['brand'], self.brand.id)

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

