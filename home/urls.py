from django.urls import path
from .views import *

from home import views

urlpatterns = [
    path('', views.upload_orders, name='upload_orders'),
    path('signup', views.signuppage, name='signup'),
    path('customers', views.customers, name='customers'),
    path('payments', views.payments, name='payments'),

    
    path('search_customers', views.search_customers, name='search_customers'),


    
    path('single_customer/<int:pk>', views.single_customer, name='single_customer'),
    path('single_order/<int:pk>', views.single_order, name='single_order'),

    

    



]