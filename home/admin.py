from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


admin.site.register(Order, ImportExportModelAdmin)
admin.site.register(Notifications)
admin.site.register(Truck, ImportExportModelAdmin)
admin.site.register(Report_order)
admin.site.register(ServiceRecord)