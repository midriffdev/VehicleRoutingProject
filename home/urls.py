from django.urls import path
from .views import *

from home import views

urlpatterns = [
    path('', views.upload_orders, name='upload_orders'),
    path('delete-all-orders/', delete_all_orders, name='delete_all_orders'),
    path('signup', views.signuppage, name='signup'),
    path('customers', views.customers, name='customers'),
    path('drivers', views.drivers, name='drivers'),
    path('drivers/<int:pk>', views.drivers, name='driver_single'),
    path('payments', views.payments, name='payments'),
    path('vehicles', views.vehicles, name='vehicles'),
    path('reset_assinged_trucks', views.reset_assinged_trucks, name='reset_assinged_trucks'),
    path('escalationteam', views.escalationteam, name='escalationteam'),
    path('customer_single_order/<int:pk>', views.customer_single_order, name='customer_single_order'),
    path('switchAccounts', views.switchAccounts, name='switchAccounts'),
    path('reports', views.reports, name='reports'),
    path('post_reports', views.post_reports, name='post_reports'),

    

    
    path('search_customers', views.search_customers, name='search_customers'),
    
    path('add_service/<int:pk>', views.add_service, name='add_service'),
    path('delete_vehicle/<int:pk>', views.delete_vehicle, name='delete_vehicle'),
    path('edit_vehicle/<int:pk>', views.edit_vehicle, name='edit_vehicle'),
    path('admin_single_vehicle/<int:pk>', views.admin_single_vehicle, name='admin_single_vehicle'),

    
    path('single_customer/<int:pk>', views.single_customer, name='single_customer'),
    path('single_order/<int:pk>', views.single_order, name='single_order'),
    path('report_issue/<int:pk>', views.report_issue, name='report_issue'),

    

    



]