
from .models import *
import datetime
from django.utils import timezone
from django.conf import settings #for email send host name


from django.core.mail import send_mail, EmailMessage  #for email send
from django.template.loader import render_to_string #for email send
from django.utils.html import strip_tags #for email send
from django.conf import settings #for email send host name



def today_due_emails():
    orders = Order.objects.filter(order_status="delivered", payment_status="due", due_payment_date__date=datetime.datetime.now().date())
    for i in orders:

        content=f"Your payment for Order {i.product_name} is due today. Please settle it by the end of the day to avoid any interruptions in service. Thank you!"

        html_message = render_to_string('home/orderemail.html', {'user': i.email,'content':content})
        try: send_mail('Payment Due Today for Your Order', strip_tags(html_message), settings.EMAIL_HOST_USER, [i.email,], html_message=html_message)
        except Exception as e: print("\n\n______________________unable to send mail", e)

        Notifications.objects.create(
            content=f"Your payment for Order {i.product_name} is due today. Please settle it by the end of the day to avoid any interruptions in service. Thank you!",
            title=f'Payment Due Today for Your Order {i.product_name}',
            receiver=i
        )


def due_payments_emails(): #  completed first payment
    orders=Order.objects.filter(order_status="delivered",payment_status="due", due_payment_date__date__lt=datetime.datetime.now().date())

    for i in orders:

        content=f"Your payment for Order {i.product_name} is overdue; please settle it as soon as possible to avoid service interruptions. Thank you!"

        html_message = render_to_string('home/orderemail.html', {'user': i.email,'content':content})
        try: send_mail(f'Urgent: Payment Pending for Your Order {i.product_name}.', strip_tags(html_message), settings.EMAIL_HOST_USER, [i.email,], html_message=html_message)
        except Exception as e: print("\n\n______________________unable to send mail", e)

        Notifications.objects.create(content=f"Your payment for Order {i.product_name} is overdue; please settle it as soon as possible to avoid service interruptions. Thank you!", title=f'Payment Due for Your Order {i.product_name}.', receiver=i)

        i.payment_status="past_due"
        i.save()


def final_warning_emails():
    five_days_ago = datetime.datetime.now().date() - datetime.timedelta(days=5)

    # Get orders that are overdue for more than 5 days, and their payment status is "past_due"
    orders = Order.objects.filter(order_status="delivered", payment_status="past_due", due_payment_date__date__lt=five_days_ago)
    
    for i in orders:
        content=f"Dear Customer, your payment for Order {i.product_name} has been pending for more than 5 days. Please settle it immediately to avoid escalation to our collections department. We value your prompt action in this matter. Thank you!"
        html_message = render_to_string('home/orderemail.html', {'user': i.email,'content':content})
        try: send_mail('Urgent: Payment Pending for Your Order.', strip_tags(html_message), settings.EMAIL_HOST_USER, [i.email,], html_message=html_message)
        except Exception as e: print("\n\n______________________unable to send mail", e)

        Notifications.objects.create(
            content=f"Dear Customer, your payment for Order {i.product_name} has been pending for more than 5 days. Please settle it immediately to avoid escalation to our collections department. We value your prompt action in this matter. Thank you!",
            title=f"Urgent: Payment Pending for Your Order {i.product_name}",
            receiver=i
        )
        # Optionally, you can escalate the order's payment status
        i.payment_status = "escalation_pending"
        i.save()





