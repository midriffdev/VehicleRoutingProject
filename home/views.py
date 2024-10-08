from django.shortcuts import render,redirect
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import *  # Ensure you import your Order model

from django.urls import reverse
from datetime import timedelta
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage  #for email send
from django.template.loader import render_to_string #for email send
from django.utils.html import strip_tags #for email send
from django.conf import settings #for email send host name
from decouple import config
from django.conf import settings
import google.generativeai as genai
from .models import *  # Ensure you import your Order model
import requests, os, csv

genai.configure(api_key="AIzaSyBIRV_ORrLlXPkxkOlNMeJ-wlkROCarVYI")
GEMINI_API_KEY="AIzaSyBIRV_ORrLlXPkxkOlNMeJ-wlkROCarVYI"

@csrf_exempt
def signuppage(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page

    return render(request, 'home/orders.html')

@csrf_exempt
def payments(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/payments.html',context)

@csrf_exempt
def vehicles(request):
    if request.method == 'POST':

        print("vehicles ",request.POST)
        truck_name=request.POST.get('truck_name')
        driver_name=request.POST.get('driver_name')
        truck_number=request.POST.get('truck_number')
        capacity=request.POST.get('capacity_volume')
        cost_per_km=request.POST.get('cost_per_km')
        contact_number=request.POST.get('contact_number')

        try:
            truck=Truck.objects.get(truck_number=truck_number)
        except:

            truck = Truck.objects.create(
                truck_name=truck_name,
                driver_name=driver_name,
                truck_number=truck_number,
                capacity=capacity,
                cost_per_km=cost_per_km,
            )
        return redirect('vehicles')

    else:
        vehicles=Truck.objects.all()

        context={
            'vehicles':vehicles,
        }
        return render(request, 'home/vehicles.html',context)

@csrf_exempt
def edit_vehicle(request,pk):
    if request.method == 'POST':
        vechcle=request.POST.get('truck_id')
        vv=Truck.objects.get(id=vechcle)

        print("vehicles ",request.POST)
        vv.truck_name=request.POST.get('truck_name')
        vv.driver_name=request.POST.get('driver_name')
        vv.truck_number=request.POST.get('truck_number')
        vv.capacity=request.POST.get('capacity_volume')
        vv.cost_per_km=request.POST.get('cost_per_km')
        vv.contact_number=request.POST.get('contact_number')
        vv.save()
        return redirect('vehicles')
 
@csrf_exempt
def delete_vehicle(request,pk):
    print(request.POST,"defres")
    if request.method == 'POST':
        vechcle=request.POST.get('truck_id')
        vv=Truck.objects.filter(id=vechcle).delete()
        return redirect('vehicles')
    
@csrf_exempt
def analyseRoutesAI(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/ai-routes.html',context)
    
@csrf_exempt
def escalationteam(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered",payment_status="escalation_pending").order_by("-id")
        all_orders=Order.objects.filter(order_status="delivered").order_by("-id")
        context={
            'orders':all_orders,
            'all_orders':all_orders,
        }
        return render(request, 'home/escalation-team.html',context)
    
@csrf_exempt
def customer_single_order(request,pk):
    if request.method == 'POST':
        payment_status=request.POST.get('payment_status')
        order=Order.objects.get(id=pk)
        order.payment_status=payment_status
        order.order_status=order.payment_status
        order.save()  # Redirect to home or any other page
        return redirect(reverse('customer_single_order', kwargs={'pk': pk}))
    
    else:
        order=Order.objects.get(id=pk)

        order.delivered_payment_date = order.due_payment_date - timedelta(days=2)
        order.order_due_payment = order.due_payment_date
        order.past_due_payment = order.due_payment_date + timedelta(days=1)
        order.final_due_payment = order.due_payment_date + timedelta(days=5)

        context={
            'order':order,
        }
        return render(request, 'home/single-order-team.html',context)
    
@csrf_exempt
def switchAccounts(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/switch-accounts.html',context)

@csrf_exempt
def customers(request):
    if request.method == 'POST':
        print("welcome ji")
        email_id=request.POST.get('email_id')
        orders=Order.objects.filter(email=email_id).order_by('-id')

        context={
            'orders':orders,
        }
        return render(request, 'home/customers.html',context)

    else:
        orders=Order.objects.all()
        context={
            'orders':orders,
        }
        return render(request, 'home/customers.html',context)

@csrf_exempt
def single_customer(request,pk):
    if request.method == 'POST':
        print("single_customer request")

        payment_status=request.POST.get('payment_status')
        order=Order.objects.get(id=pk)
        order.payment_status=payment_status
        order.order_status=order.payment_status
        order.save()

        html_message = render_to_string('home/orderemail.html', {'user': order.cname})
        try:
            send_mail(
                'Your payment was successful!',
                strip_tags(html_message),
                settings.EMAIL_HOST_USER,
                [order.email],
                html_message=html_message
            )
        except Exception as e:
            print("\n\n______________________unable to send mail", e)

        Notifications.objects.create(
            content="Your payment has been successfully completed. Thank you for your order!",
            title='Payment Successful',
            receiver=order
        )
        if 'by_team_member' in request.POST:

            return redirect(reverse('customer_single_order', kwargs={'pk': pk}))  
        else:
            return redirect(reverse('single_customer', kwargs={'pk': pk}))  

    
    else:
        order=Order.objects.get(id=pk)
        notifications=Notifications.objects.filter(receiver=order)
        context={
            'order':order,
            'notifications':notifications,
        }
        return render(request, 'home/single_customer.html',context)

@csrf_exempt
def single_order(request,pk):
    if request.method == 'POST':

        if 'send_reminder' in request.POST:
            print("order_status ")
            send_reminder=request.POST.get('send_reminder')

            if send_reminder == 'due_reminder':

                order=Order.objects.get(id=pk)
                
                content=f"Your payment for Order {order.product_name} is due today. Please settle it by the end of the day to avoid any interruptions in service. Thank you!"

                html_message = render_to_string('home/orderemail.html', {'user': order.cname,'content':content})
                try: send_mail('Payment Due Today for Your Order', strip_tags(html_message), settings.EMAIL_HOST_USER, [order.email,], html_message=html_message)
                except Exception as e: print("\n\n______________________unable to send mail", e)

                Notifications.objects.create(
                    content=f"Your payment for Order {order.product_name} is due today. Please settle it by the end of the day to avoid any interruptions in service. Thank you!",
                    title=f'Payment Due Today for Your Order {order.product_name}',
                    count=2,
                    receiver=order
                )

                order.payment_status = "past_due"
                order.send_email_count=2
                order.due_reminder_sent_date = timezone.now()
                order.save()

                return redirect(reverse('single_order', kwargs={'pk': pk}))
            
            if send_reminder == 'past_due_reminder':

                i=Order.objects.get(id=pk)
                
                content=f"Your payment for Order {i.product_name} is overdue; please settle it as soon as possible to avoid service interruptions. Thank you!"

                html_message = render_to_string('home/orderemail.html', {'user': i.cname,'content':content})
                try: send_mail(f'Urgent: Payment Pending for Your Order {i.product_name}.', strip_tags(html_message), settings.EMAIL_HOST_USER, [i.email,], html_message=html_message)
                except Exception as e: print("\n\n______________________unable to send mail", e)

                Notifications.objects.create(content=f"Your payment for Order {i.product_name} is overdue; please settle it as soon as possible to avoid service interruptions. Thank you!", title=f'Payment Due for Your Order {i.product_name}.', receiver=i, count=3)

                i.payment_status="past_due"
                i.send_email_count=3
                i.past_due_reminder_sent_date = timezone.now()
                i.save()

                return redirect(reverse('single_order', kwargs={'pk': pk}))
            
            if send_reminder == 'last_reminder':

                i=Order.objects.get(id=pk)
                
                content=f"Dear Customer, your payment for Order {i.product_name} has been pending for more than 5 days. Please settle it immediately to avoid escalation to our collections department. We value your prompt action in this matter. Thank you!"
                html_message = render_to_string('home/orderemail.html', {'user': i.cname,'content':content})
                try: send_mail('Urgent: Payment Pending for Your Order.', strip_tags(html_message), settings.EMAIL_HOST_USER, [i.email,], html_message=html_message)
                except Exception as e: print("\n\n______________________unable to send mail", e)

                Notifications.objects.create(
                    content=f"Dear Customer, your payment for Order {i.product_name} has been pending for more than 5 days. Please settle it immediately to avoid escalation to our collections department. We value your prompt action in this matter. Thank you!",
                    title=f"Urgent: Payment Pending for Your Order {i.product_name}",
                    count=4,
                    receiver=i
                )
                # Optionally, you can escalate the order's payment status
                i.send_email_count=4
                i.payment_status = "escalation_pending"
                i.final_reminder_sent_date = timezone.now()
                i.save()
                return redirect(reverse('single_order', kwargs={'pk': pk}))
            
        else:
            print("order_status ")
            order_status=request.POST.get('order_status')
            order=Order.objects.get(id=pk)
            order.order_status=order_status
            order.due_payment_date = order.created_at + timedelta(days=2)
            order.payment_status = "due"
            order.send_email_count=1
            order.delivered_date = timezone.now()
            order.save()

            content=f"Your order has been delivered successfully! We hope everything arrived just as you expected.Kindly complete your payment by {order.due_payment_date}, or earlier.Thank you for choosing us!"

            html_message = render_to_string('home/orderemail.html', {'user': order.cname,'content':content})
            try: send_mail('Order delivered to you successfully.', strip_tags(html_message), settings.EMAIL_HOST_USER, [order.email,], html_message=html_message)
            except Exception as e: print("\n\n______________________unable to send mail", e)

            Notifications.objects.create(content=f"Your order has been successfully delivered. Kindly complete your payment by {order.due_payment_date}, or earlier.", title='Order delivered', receiver=order,count=1)

            return redirect(reverse('single_order', kwargs={'pk': pk}))
    
    else:
        order=Order.objects.get(id=pk)
        context={
            'order':order,
        }
        return render(request, 'home/single_order.html',context)

@csrf_exempt
def upload_orders(request):
    if request.method == 'POST':
        
        csv_file = request.FILES.get('file')
        if csv_file:
            csv_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            next(csv_reader) 

            for row in csv_reader:
                print(row, "row....................")  
                cname = row[0]  
                email = row[1]  
                product_name = row[2]  
                quantity = int(row[3]) 
                from_location = row[4]  
                destination = row[5]  
                payment_amount = float(row[6]) 

                order = Order.objects.create(
                    product_name=product_name,
                    quantity=quantity,
                    destination=destination,
                    from_location=from_location,
                    email=email,
                    cname=cname,
                    payment_amount=payment_amount,
                    order_status='pending',  
                )
                   
        return redirect('upload_orders') 
    
    else:
        orders=Order.objects.all()
        context={
            'orders':orders,
        }
        return render(request, 'home/orders.html',context) 

def delete_all_orders(request):
    if request.method == 'POST':
        Notifications.objects.all().delete()
        Order.objects.all().delete()  
        messages.success(request, "All orders have been successfully deleted.")
        return redirect('upload_orders')
    else:
        messages.warning(request, "Invalid request. Please confirm the action.")
        return redirect('upload_orders')

@csrf_exempt
def check_orders(orders, s_keyword):

    # Assuming orders is a list of dictionaries representing orders
    order_list = [order for order in orders]  # Ensuring we have a list of orders

    # Constructing a prompt for the generative model
    prompt = f"""
    Given the following orders: {order_list}, find the orders whose payment_status is '{s_keyword}'.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")  # Initialize the model
    response = model.generate_content(prompt)  # Generate content based on the prompt

    print(response.text, "response............................................")
    return response.text.strip()

@csrf_exempt
def search_customers(request):
    if request.method == 'POST':
        print("ENTER ji")

        # Fetch orders with the required fields, including payment_status
        orders = Order.objects.filter(order_status="delivered").values('id', 'order_status', 'payment_status', 'quantity')

        # Retrieve the search keyword from the form (payment status)
        search_keywords = request.POST.get('search_status')

        # Pass the orders and search keyword to the check_orders function
        response_text = check_orders(orders, search_keywords)

        print(response_text, "check_response.............")
        return redirect(payments)

    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/payments.html',context)

@csrf_exempt
def get_delivered_orders():
    delivered_orders = Order.objects.filter(order_status="delivered")
    return delivered_orders

@csrf_exempt
def generate_email_content(order):
    url = "https://gemini.api.endpoint/your_endpoint"  # Replace with actual endpoint
    headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "prompt": f"Write a polite email asking for payment for order {order.order_id}.",
        "other_params": "value"
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("generated_content")
    else:
        # Handle error
        return "Error generating content"
