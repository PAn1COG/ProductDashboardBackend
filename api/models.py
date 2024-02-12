from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)

    def __str__(self):
        return self.name


# SKU, name, category, tags, stock status, and available stock 
class Item(models.Model):
    SKU = models.CharField(max_length=100, unique  = True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # category = models.CharField(max_length=255) 
    tags = models.CharField(max_length=255, blank=True, null=True)
    stock_status = models.CharField(max_length=20, choices=[
        ('In Stock', 'In Stock'),
        ('Out of Stock', 'Out of Stock'),
        ('Backordered', 'Backordered'),
    ])
    available_stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name