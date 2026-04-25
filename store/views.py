from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import Product, Cart, Order,OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer,OrderItemSerilizer
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import jwt
from django.db import transaction

from store.models import CartItem
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def product_list(request):
    brand = request.query_params.get('brand')
    if brand:
        products = Product.objects.filter(brand__iexact=brand)
    else:    
        products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

 
    
@api_view(['GET'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        for item in cart_items:
            Order.objects.create(user=request.user, product=item.product, quantity=item.quantity)
        cart_items.delete()
        return Response({'message': 'Order placed'})
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])    
def create_order(request):
    user = request.user
    orderItems = request.data.get('items')
    totalPrice = request.data.get('total_price')
    cart = Cart.objects.get(user=user)
    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total_price=totalPrice,
                status='processing'
            )
            
            for item_id, details in orderItems.items():
                product = Product.objects.select_for_update().get(id=item_id)
                quantity = details['quantity']
                
                if product.stock < quantity:
                    raise Exception(f"low stock for {product.name}")
                product.stock-=quantity
                product.save()
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                    
                )
            cart.delete()
            return Response({"message": "Order successful!", "order_id": order.id}, status=201)
                
    except Exception as e:
        return Response({"error": str(e)}, status=400)        
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_cart(request):
    # 1. Get or create the 'Header' record for this user
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    if request.method == 'POST':
        # Logic to add/update items
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = Product.objects.get(id=product_id)
        
        # 2. Create or update the 'Line Item'
        item, item_created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'price': product.price}
        )
        
        if not item_created:
            item.quantity += quantity
        else:
            item.quantity = quantity
            
        item.save()

        # 3. Update the Cart Header total_price
        # (You can also use a Django signal or property for this)
        cart.total_price = sum(i.quantity * i.price for i in cart.items.all())
        cart.save()

        return Response({"message": "Cart updated successfully"}, status=200) 
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cartItem(request, product_id):
    CartItem.objects.filter(cart__user=request.user, product_id=product_id).delete()
    # Recalculate total after delete
    cart = Cart.objects.get(user=request.user)
    cart.total_price = sum(i.quantity * i.product.price for i in cart.items.all())
    cart.save()
    return Response({"status": "deleted", "total": cart.total_price})    
 
 
 
 
 
           
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    google_token = request.data.get('token') 
    try:
        # Decode without verification as requested to bypass time/clock sync issues
        idinfo = jwt.decode(google_token, verify=False) 
        
        # Manual Security Check for Audience
        expected_client_id = "739486864972-v3lm8mhs4p96ss6euassum5t7qfgqek9.apps.googleusercontent.com"
        if idinfo.get('aud') != expected_client_id:
            return Response({'error': 'Invalid Audience'}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo.get('email')
        username = email.split('@')[0]
        
        # Efficient Get or Create
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', '')
            }
        )
        
        if created:
            user.set_unusable_password()
            user.save()

        # Generate JWT tokens (Access & Refresh)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Google Login Error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide both'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if User.objects.filter(username=username).exists():
             return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        
        # Generate tokens so they don't have to login again immediately
        refresh = RefreshToken.for_user(user)
        print('username created')
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    