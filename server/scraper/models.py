from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    asin = models.CharField(max_length=10, unique=True)
    sku = models.CharField(max_length=50)
    image = models.URLField(max_length=500)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
