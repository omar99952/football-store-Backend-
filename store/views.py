from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from django.contrib.auth import authenticate

@api_view(['GET'])
def product_list(request):
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



from django.contrib.auth.models import User
from django.db import IntegrityError # Add this

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