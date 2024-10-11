from django.db import models
# from ai_vehicle.models import routedata

class Truck(models.Model):
    truck_name                          = models.CharField(max_length=255)
    driver_name                         = models.CharField(max_length=255)
    driver_email                        = models.EmailField(max_length=100)
    truck_image                         = models.ImageField(upload_to='trucks', null=True, blank=True)
    contact_number                      = models.CharField(max_length=100, null=True, blank=True, default=9876543213)
    truck_number                        = models.CharField(max_length=100, unique=True)
    capacity                            = models.PositiveIntegerField()  # Assuming capacity is in kilograms or liters
    cost_per_km                         = models.DecimalField(max_digits=10, decimal_places=2)
    available                           = models.BooleanField(default=True)
    routedata                           = models.ForeignKey('ai_vehicle.routedata', null=True, blank=True, on_delete=models.PROTECT)
    warehouse                           = models.ForeignKey('ai_vehicle.HeadQuarter', on_delete=models.PROTECT)

    def __str__(self): return f"{self.truck_name} ({self.truck_number}) | avl-{self.available} | onreoute-{bool(self.routedata)} | warehouse - {self.warehouse.name}"










class Order(models.Model):
    PRODUCT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('shipped', 'Shipped'),
        ('delivered', 'delivered'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('due', 'due'),
        ('past_due', 'past_due'),
        ('escalation_pending', 'escalation_pending'),
    ]

    email                               = models.EmailField()
    cname                               = models.CharField(max_length=75,default='Alex')
    product_name                        = models.CharField(max_length=255)
    quantity                            = models.PositiveIntegerField(default=0)
    from_location                       = models.CharField(max_length=255, blank=True, null=True)
    destination                         = models.CharField(max_length=255)
    payment_amount                      = models.DecimalField(max_digits=10, decimal_places=2)# Adjust max_digits and decimal_places as needed
    order_status                        = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='pending')
    payment_status                      = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    send_email_count                    = models.PositiveIntegerField(default=0)
    created_at                          = models.DateTimeField(auto_now_add=True)  # Automatically set when the order is created
    updated_at                          = models.DateTimeField(auto_now=True) 
    delivered_date                      = models.DateTimeField(null=True, blank=True)
    due_reminder_sent_date              = models.DateTimeField(null=True, blank=True)
    past_due_reminder_sent_date         = models.DateTimeField(null=True, blank=True)
    final_reminder_sent_date            = models.DateTimeField(null=True, blank=True)
    payment_date                        = models.DateField(null=True, blank=True)  # Date when payment is sucessfully donee
    due_payment_date                    = models.DateField(null=True, blank=True)  # Date by which payment should be made
    past_due_payment_date               = models.DateField(null=True, blank=True)  # Date by which payment is late
    lat                                 = models.CharField(max_length=15, blank=True, null=True)
    long                                = models.CharField(max_length=15, blank=True, null=True)
    late_payment_status                 = models.BooleanField(default=False)  # To indicate if the payment is late
    due_days                            = models.PositiveIntegerField(default=0)
    warehouse                           = models.ForeignKey('ai_vehicle.HeadQuarter', on_delete=models.PROTECT)
    assigned_truck                      = models.ForeignKey('Truck', blank=True, null=True, on_delete=models.PROTECT)
  
    def __str__(self):
        return f'{self.product_name} {self.payment_status} (Quantity: {self.quantity}) - {self.order_status}{" | assigned to " + self.assigned_truck.truck_name if self.assigned_truck else ""}'



class Report_order(models.Model):
    truck             		            = models.ForeignKey(to=Truck, on_delete=models.PROTECT, related_name='truck')
    order             		            = models.ForeignKey(to=Order, on_delete=models.PROTECT, related_name='order')
    issue                               = models.CharField(max_length=255)
    created_at                          = models.DateTimeField(auto_now_add=True)
    updated_at                          = models.DateTimeField(auto_now=True) 
   
    def __str__(self): return f"{self.truck.truck_name} ({self.order})"



class Notifications(models.Model):
    STATUS=(('Active','Active'),('Inactive','Inactive'),)
    content                             = models.TextField()
    title 	                            = models.TextField()
    receiver             		        = models.ForeignKey(to=Order, on_delete=models.PROTECT, related_name='customer')     
    created_at                          = models.DateTimeField(auto_now_add=True)
    is_read                             = models.BooleanField(default=False)
    link                                = models.TextField(null=True, blank=True)
    count                               = models.PositiveIntegerField(default=0)
    status                              = models.CharField(choices=STATUS, max_length=10, default="Active")

    def __str__(self):
        return f"{self.id} || {self.content} || {self.receiver}"