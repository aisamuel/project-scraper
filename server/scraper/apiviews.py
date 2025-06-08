from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework import filters, generics  # type: ignore

from .models import Brand, Product
from .pagination import CustomPageNumberPagination
from .serializers import BrandSerializer, ProductSerializer


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name"]
    search_fields = [
        "name",
    ]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Enable filtering and search
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["brand__name"]
    search_fields = ["name", "asin"]

    # Custom pagination
    pagination_class = CustomPageNumberPagination
