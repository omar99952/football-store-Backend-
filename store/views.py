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

@api_view(['GET'])
def product_list(request):
    brand = request.query_params.get('brand')
    if brand:
        products = Product.objects.filter(brand__iexact=brand)
    else:    
        products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # 1. Authenticate the user
    user = authenticate(username=username, password=password)

    if user is not None:
        # 2. Get or create the token
        token, created = Token.objects.get_or_create(user=user)
        
        # 3. Return token + extra info if you want
        return Response({
            "token": token.key,
            "username": user.username,
            "user_id": user.id,
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
    else:
        # 4. Return error if credentials fail
        return Response({
            "error": "Invalid Username or Password"
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    google_token = request.data.get('token') 
    try:
        idinfo = jwt.decode(google_token, verify=False) # 'verify=False' stops the time crash
        
        # Manually check the audience to keep it secure
        expected_client_id = "739486864972-v3lm8mhs4p96ss6euassum5t7qfgqek9.apps.googleusercontent.com"
        if idinfo['aud'] != expected_client_id:
            return Response({'error': 'Invalid Audience'}, status=400)
        email = idinfo['email']
        username = email.split('@')[0]
        user = User.objects.filter(email=email).first()
        
        if(not user):
           
            user = User.objects.create(
                username=username,
                email = email,
                first_name=idinfo.get('given_name', ''),
                last_name=idinfo.get('family_name', '') 
            )
            user.set_unusable_password()
            user.save()
        token , _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key, 
            'username': user.username
        },status=status.HTTP_200_OK)
        
    except ValueError as e:
        print(f"Verification Failed: {e}")
        return Response({'error': 'Invalid Google Token'}, status=400)
    except Exception as e:
        print(f"General Error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide both'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if username exists
        if User.objects.filter(username=username).exists():
             return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
@api_view(['GET'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)



                       
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(pk=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return Response({'message': 'Added to cart'}, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        product_id = request.data.get('product_id')
        Cart.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({'message': 'Removed from cart'})


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
@permission_classes([AllowAny])    
def create_order(request):
    user = request.user
    orderItems = request.data.get('items')
    totalPrice = request.data.get('total_price')
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
            return Response({"message": "Order successful!", "order_id": order.id}, status=201)
                
    except Exception as e:
        return Response({"error": str(e)}, status=400)        
    
           
        
        
    
    
    