from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import GenRoutes, HeadQuarter, Truckdata, routedata

admin.site.register(GenRoutes)
admin.site.register(HeadQuarter, ImportExportModelAdmin)
admin.site.register(Truckdata)
admin.site.register(routedata)

