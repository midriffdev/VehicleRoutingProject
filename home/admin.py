from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Order)
admin.site.register(Notifications)
admin.site.register(Truck)
admin.site.register(Report_order)
admin.site.register(ServiceRecord)