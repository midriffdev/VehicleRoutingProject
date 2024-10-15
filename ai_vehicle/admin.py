from django.contrib import admin
from .models import GenRoutes, HeadQuarter, Truckdata, routedata

admin.site.register(GenRoutes)
admin.site.register(HeadQuarter)
admin.site.register(Truckdata)
admin.site.register(routedata)

