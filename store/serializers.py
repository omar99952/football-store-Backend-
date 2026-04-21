from rest_framework import serializers
from .models import Product, Cart, Order,OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
        
        


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerilizer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = '__all__'
    
    
    
class OrderSerializer(serializers.ModelSerializer):
    orderItem = OrderItemSerilizer()
    class Meta:
        model = Order
        fields = '__all__'
        