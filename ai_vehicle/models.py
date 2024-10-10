from django.db import models
from home.models import Truck, Order

class truckdata(models.Model):
    truck   = models.ForeignKey(Truck, on_delete=models.CASCADE)
    orders  = models.ManyToManyField(Order)
    fstop   = models.CharField(max_length=30)
    lstop   = models.CharField(max_length=30)
class GenRoutes(models.Model):
    # truck   = models.ForeignKey("Truck", on_delete=models.CASCADE)
    # orders  = models.ManyToManyField("Order", blank=True, null=True)
    ijson   = models.FileField(upload_to='genjson', max_length=100)
    created = models.DateTimeField(auto_now_add=True)

class HeadQuarter(models.Model):
    name    = models.CharField(max_length=30)
    primary = models.BooleanField(default=False)
    lat     = models.CharField(max_length=15)
    long    = models.CharField(max_length=15)
