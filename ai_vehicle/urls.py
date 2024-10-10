from django.urls import path
from .views import *

urlpatterns = [
    # path('', ChatbotView.as_view(), name='chat'),  # Define the chat endpoint
    # path('chatt', ChatbotView3.as_view(), name='chatt'),  # Define the chat endpoint
    path('getroute', getroute, name='getroute'),
    path('headquarter', headquarter, name='headquarter'),
    # path('transform', transform, name='transform'),
    path('download/<int:route_id>/', download_json, name='download_json'),
    path('assign_routes/<int:route_id>/', assign_routes_to_trucks, name='assign_routes_to_trucks'),
    path('delete_hq/<int:pk>/', delete_hq, name='delete_hq'),
    path('set_hq/<int:pk>/', set_hq, name='set_hq'),
 
]