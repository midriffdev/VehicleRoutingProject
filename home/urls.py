from django.urls import path
from .views import *

from home import views

urlpatterns = [
    path('', views.upload_orders, name='upload_orders'),
    path('signup', views.signuppage, name='signup'),
    path('customers', views.customers, name='customers'),
    path('payments', views.payments, name='payments'),
    path('vehicles', views.vehicles, name='vehicles'),
    path('analyseRoutesAI', views.analyseRoutesAI, name='analyseRoutesAI'),
    path('escalationteam', views.escalationteam, name='escalationteam'),
    path('customer_single_order/<int:pk>', views.customer_single_order, name='customer_single_order'),
    path('switchAccounts', views.switchAccounts, name='switchAccounts'),

    

    
    path('search_customers', views.search_customers, name='search_customers'),


    
    path('delete_vehicle/<int:pk>', views.delete_vehicle, name='delete_vehicle'),
    path('single_customer/<int:pk>', views.single_customer, name='single_customer'),
    path('single_order/<int:pk>', views.single_order, name='single_order'),

    

    



]