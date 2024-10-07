from django.db import models

# Create your models here.
class GenRoutes(models.Model):
    # truck   = models.ForeignKey("Truck", on_delete=models.CASCADE)
    # orders  = models.ManyToManyField("Order", blank=True, null=True)
    ijson   = models.FileField(upload_to='genjson', max_length=100)
    created = models.DateTimeField(auto_now_add=True)
