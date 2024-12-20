from django.db import models
from home.models import Truck, Order


class routedata(models.Model):
    orders      = models.ManyToManyField(Order, null=True, blank=True)
    fstop       = models.CharField(max_length=30, null=True, blank=True)
    lstop       = models.CharField(max_length=30, null=True, blank=True)
    timetaken   = models.DurationField(null=True, blank=True, help_text="Initial estimated time for delivery")
    tot_orders  = models.IntegerField(null=True, blank=True, help_text="Total Orders")
    last_order  = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name = 'last_order', blank=True, null=True)
    distance    = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, help_text="Distance in Kilometers")
    def __str__(self): return str(self.id)
    
class Truckdata(models.Model):
    truck       = models.ForeignKey(Truck, on_delete=models.CASCADE)
    routedata   = models.ForeignKey(routedata, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self): return f'{self.id} || {self.truck.truck_name} || route-{self.routedata.id}'

class GenRoutes(models.Model):
    # truck     = models.ForeignKey("Truck", on_delete=models.CASCADE)
    # orders    = models.ManyToManyField("Order", blank=True, null=True)
    ijson       = models.FileField(upload_to='genjson', max_length=100)
    created     = models.DateTimeField(auto_now_add=True)
    truckdata   = models.ManyToManyField(Truckdata, null=True, blank=True)
    pendorders  = models.ManyToManyField(Order, null=True, blank=True)
    warehouse   = models.ForeignKey('HeadQuarter', on_delete=models.PROTECT)
    tot_delv    = models.IntegerField(null=True, blank=True, help_text="Number of deliveries")

class HeadQuarter(models.Model):
    name            = models.CharField(max_length=30)
    primary         = models.BooleanField(default=False)
    lat             = models.CharField(max_length=15)
    long            = models.CharField(max_length=15)
    product_name    = models.CharField(max_length=15,null=True, blank=True,)
    total_stock     = models.PositiveIntegerField(null=True, blank=True,default=0)
    available_stock = models.PositiveIntegerField(null=True, blank=True,default=0)
    left_stock      = models.PositiveIntegerField(null=True, blank=True,default=0)


    def __str__(self): return f'{self.id} || {self.name}{" || MAIN" if self.primary else ""}'
