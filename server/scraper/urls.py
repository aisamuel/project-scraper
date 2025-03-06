from django.urls import path
from .apiviews import ProductListView, BrandListView

urlpatterns = [
    path('api/products/', ProductListView.as_view(), name='product_list'),
    path('api/brands/', BrandListView.as_view(), name='brand-list'),
]
