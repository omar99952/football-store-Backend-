from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import product_list,register ,product_detail,cart_view,order_list,google_login

urlpatterns = [
    # Authentication
    path('login/', obtain_auth_token), 
    path('google-login/',google_login, name='google_login'),
    path('register/', register),
    
    # Features
    path('products/', product_list), 
    path('products/<int:pk>/', product_detail),  
    path('cart/', cart_view),                    
    path('orders/', order_list),
]