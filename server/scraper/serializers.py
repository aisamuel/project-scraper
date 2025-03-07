from rest_framework import serializers
from .models import Product, Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'asin', 'sku', 'image', 'brand_name']
