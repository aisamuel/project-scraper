from django.urls import path
from .apiviews import ProductListView

urlpatterns = [
    path('api/products/', ProductListView.as_view(), name='product_list'),
]
