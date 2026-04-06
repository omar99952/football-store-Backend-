from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import product_list,register

urlpatterns = [
    path('products/', product_list),
    path('login/', obtain_auth_token), # This handles everything for you
    path('register/', register),
]