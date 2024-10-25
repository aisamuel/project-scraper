from django.contrib import admin
from .models import Product, Brand

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asin', 'sku', 'brand', 'image')
    list_filter = ('brand',)
    search_fields = ('name', 'asin', 'sku')
    ordering = ('name',)
    readonly_fields = ('asin',)
