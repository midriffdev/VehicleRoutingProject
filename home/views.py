from django.shortcuts import render,redirect

import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *  # Ensure you import your Order model


from django.urls import reverse
from datetime import timedelta


from django.core.mail import send_mail, EmailMessage  #for email send
from django.template.loader import render_to_string #for email send
from django.utils.html import strip_tags #for email send
from django.conf import settings #for email send host name



import os


import google.generativeai as genai


genai.configure(api_key="AIzaSyBIRV_ORrLlXPkxkOlNMeJ-wlkROCarVYI"
)


from decouple import config

GEMINI_API_KEY="AIzaSyBIRV_ORrLlXPkxkOlNMeJ-wlkROCarVYI"


import requests
from django.conf import settings




def signuppage(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page

    return render(request, 'home/orders.html')

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
    

def escalationteam(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/escalation-team.html',context)
    

def ordersingleteam(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered")
        context={
            'orders':orders,
        }
        return render(request, 'home/single-order-team.html',context)
    


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


    


def customers(request):
    if request.method == 'POST':
        print("welcome ji")
       
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.all()
        context={
            'orders':orders,
        }
        return render(request, 'home/customers.html',context)

def single_customer(request,pk):
    if request.method == 'POST':
        print("single_customer request")

        payment_status=request.POST.get('payment_status')
        order=Order.objects.get(id=pk)
        order.payment_status=payment_status
        order.order_status=order.payment_status
        order.save()

        html_message = render_to_string('home/orderemail.html', {'user': order.email})
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
        return redirect(reverse('single_customer', kwargs={'pk': pk}))  
    
    else:
        order=Order.objects.get(id=pk)
        notifications=Notifications.objects.filter(receiver=order)
        context={
            'order':order,
            'notifications':notifications,
        }
        return render(request, 'home/single_customer.html',context)





def single_order(request,pk):
    if request.method == 'POST':
        print("order_status ")
        order_status=request.POST.get('order_status')
        order=Order.objects.get(id=pk)
        order.order_status=order_status
        order.due_payment_date = order.created_at + timedelta(days=2)
        order.payment_status = "due"
        order.save()

        html_message = render_to_string('home/orderemail.html', {'user': order.email})
        try: send_mail('Order delivered to you successfully.', strip_tags(html_message), settings.EMAIL_HOST_USER, [order.email,], html_message=html_message)
        except Exception as e: print("\n\n______________________unable to send mail", e)

        Notifications.objects.create(content="Order delivered to you successfully.", title='Order delivered', receiver=order)

        return redirect(reverse('single_order', kwargs={'pk': pk}))
    
    else:
        order=Order.objects.get(id=pk)
        context={
            'order':order,
        }
        return render(request, 'home/single_order.html',context)


def upload_orders(request):
    if request.method == 'POST':
        
        csv_file = request.FILES.get('file')
        if csv_file:
            csv_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            next(csv_reader) 

            for row in csv_reader:
                print(row, "row....................")  
                email = row[0]  
                product_name = row[1]  
                quantity = int(row[2]) 
                from_location = row[3]  
                destination = row[4]  
                payment_amount = float(row[5]) 

                order = Order.objects.create(
                    product_name=product_name,
                    quantity=quantity,
                    destination=destination,
                    from_location=from_location,
                    email=email,
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





def check_orders(orders, s_keyword):
    print(orders, "question >>>>>>>>>>>>>>>>>>>>>>>")
    print(s_keyword, "answer >>>>>>>>>>>>>>>>>>>>>>>")

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



def get_delivered_orders():
    delivered_orders = Order.objects.filter(order_status="delivered")
    return delivered_orders

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
