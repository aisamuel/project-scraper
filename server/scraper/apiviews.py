from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from .pagination import CustomPageNumberPagination

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Enable filtering and search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['brand__name']  
    search_fields = ['name', 'asin']
    
    # Custom pagination
    pagination_class = CustomPageNumberPagination
