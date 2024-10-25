from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField(max_length=500)
    brand = models.CharField(max_length=255)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
