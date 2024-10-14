from django.db import models
# from ai_vehicle.models import routedata

class Truck(models.Model):
    TRUCK_TYPE_CHOICES = [
        ('Flatbed', 'Flatbed'),
        ('Box', 'Box'),
        ('Tanker', 'Tanker'),
        ('Refrigerated', 'Refrigerated'),
        ('Car Carrier', 'Car Carrier'),
    ]
    STATUS_CHOICES = [
        ('available', 'available'),
        ('not_available', 'not_available'),
        ('in_service', 'In Service'),
        ('maintenance', 'Under Maintenance'),
    ]
    LICENSE_TYPE_CHOICES = [
        ('C', 'Class C - Light Truck'),
        ('B', 'Class B - Medium Truck'),
        ('A', 'Class A - Heavy Truck'),
    ]

    truck_name                          = models.CharField(max_length=255)
    truck_type = models.CharField(max_length=50, choices=TRUCK_TYPE_CHOICES,default='Tanker')
    truck_image                         = models.ImageField(upload_to='trucks', null=True, blank=True)
    truck_number                        = models.CharField(max_length=100, unique=True)
    capacity                            = models.PositiveIntegerField()  # Assuming capacity is in kilograms or liters
    make = models.CharField(max_length=100,null=True, blank=True)
    model = models.CharField(max_length=100,null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    mileage = models.PositiveIntegerField(verbose_name="Mileage (in km)",null=True, blank=True)
    license_type = models.CharField(max_length=2, choices=LICENSE_TYPE_CHOICES, verbose_name="Required License Type",null=True, blank=True,default='B')
    truck_order = models.PositiveIntegerField(null=True, blank=True)
    cost_per_km                         = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available',null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)

    driver_name                         = models.CharField(max_length=255)
    driver_email                        = models.EmailField(max_length=100)
    contact_number                      = models.CharField(max_length=100, null=True, blank=True, default=9876543213)
    driver_order = models.PositiveIntegerField(null=True, blank=True,default=0)
    on_time_deliveries = models.PositiveIntegerField(null=True, blank=True,default=0)
    late_deliveries = models.PositiveIntegerField(null=True, blank=True,default=0)

    driver_travel = models.PositiveIntegerField(null=True, blank=True,default=0)
    languages = models.CharField(max_length=100,null=True, blank=True,default='English')

    




    
    available                           = models.BooleanField(default=True)
    routedata                           = models.ForeignKey('ai_vehicle.routedata', null=True, blank=True, on_delete=models.PROTECT)
    warehouse                           = models.ForeignKey('ai_vehicle.HeadQuarter', on_delete=models.PROTECT, null=True, blank=True,default=1)

    def __str__(self): return f"{self.truck_name} ({self.truck_number}) | avl-{self.available} | onreoute-{bool(self.routedata)} | warehouse - {self.warehouse.name}"

    def get_license_type_display(self):
        license_mapping = {
            'C': 'Class C - Light Truck',
            'B': 'Class B - Medium Truck',
            'A': 'Class A - Heavy Truck',
        }
        return license_mapping.get(self.license_type, 'Unknown License Type')



class Part(models.Model):
    part_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost (in USD)")
    purchased_date = models.DateField()
    warranty_period = models.IntegerField(verbose_name="Warranty Period (in months)", null=True, blank=True)

    def __str__(self):
        return f"{self.part_name} by {self.manufacturer}"

class ServiceRecord(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='services')
    service_date = models.DateField()
    service_description = models.TextField()
    parts_changed = models.ManyToManyField(Part, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Service Cost (in USD)")
    
    def __str__(self):
        return f"Service for {self.truck} on {self.service_date}"







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
    warehouse                           = models.ForeignKey('ai_vehicle.HeadQuarter', on_delete=models.PROTECT, blank=True, null=True)
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
    

# class Notifications(models.Model):
#     STATUS=(('Active','Active'),('Inactive','Inactive'),)
#     content                             = models.TextField()
#     title 	                            = models.TextField()
#     receiver             		        = models.ForeignKey(to=Order, on_delete=models.PROTECT, related_name='customer')     
#     created_at                          = models.DateTimeField(auto_now_add=True)
#     is_read                             = models.BooleanField(default=False)
#     link                                = models.TextField(null=True, blank=True)
#     count                               = models.PositiveIntegerField(default=0)
#     status                              = models.CharField(choices=STATUS, max_length=10, default="Active")

#     def __str__(self):
#         return f"{self.id} || {self.content} || {self.receiver}"