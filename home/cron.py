
from .models import *
import datetime
from django.utils import timezone
from django.conf import settings #for email send host name


def due_payments_emails(): #  completed first payment

    orders=Order.objects.filter(order_status="delivered", due_payment_date__date__lt=datetime.datetime.now().date())
    for i in orders: 
        Notifications.objects.create(content=f"Your payment for Order {i.product_name} is overdue; please settle it as soon as possible to avoid service interruptions. Thank you!", title=f'Payment Due for Your Order {i.product_name}.', receiver=i,)








