from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import product_list ,product_detail,order_list,delete_cartItem
from .views import manage_cart,google_login,create_order,register
from rest_framework_simplejwt.views import ( TokenObtainPairView,TokenRefreshView,)
 


urlpatterns = [
    # Authentication
        #for users 
        path('google-login/',google_login, name='google_login'),
        path('register/', register),
        
        # for Tokens
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
    # Features
    path('products/', product_list), 
    path('products/<int:pk>/', product_detail),  
    path('delete-cart/<int:product_id>/', delete_cartItem),  
    path('cart/', manage_cart),                    
    path('create_order/', create_order),
]