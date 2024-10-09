from django.contrib import admin

# Register your models here.
from .models import GenRoutes, HeadQuarter

admin.site.register(GenRoutes)
admin.site.register(HeadQuarter)