from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import product_list,register ,product_detail,cart_view,order_list

urlpatterns = [
    path('products/', product_list),
    path('login/', obtain_auth_token), # This handles everything for you
    path('register/', register),
    path('products/<int:pk>/', product_detail),  # single product page
    path('cart/', cart_view),                    # cart
    path('orders/', order_list),
]