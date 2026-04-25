from rest_framework import serializers
from .models import Product, Cart, Order,OrderItem,CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
####################################### Cart #######################################
class CartItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'
class CartSerializer(serializers.ModelSerializer):
    # This allows us to see all items inside the cart JSON
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_price', 'updated_at', 'items']



############################## Order #######################################


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
        