# backend/store/admin.py
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'price', 'image')
    list_editable = ('price', 'image', 'brand') # These become text boxes in the list!