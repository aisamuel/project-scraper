from django.urls import path

from .apiviews import BrandListView, ProductListView

urlpatterns = [
    path("api/products/", ProductListView.as_view(), name="product_list"),
    path("api/brands/", BrandListView.as_view(), name="brand-list"),
]
