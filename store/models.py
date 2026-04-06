from django.db import models

# Create your models here.
from django.db import models

class Product(models.Model):
    BRAND_CHOICES = [
        ('Nike', 'Nike'),
        ('Adidas', 'Adidas'),
        ('Puma', 'Puma'),
        ('New Balance', 'New Balance'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.name