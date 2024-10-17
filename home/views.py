from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, JsonResponse
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage  #for email send
from django.template.loader import render_to_string #for email send
from django.utils.html import strip_tags #for email send
from decouple import config
from django.conf import settings
import google.generativeai as genai
from .models import *  # Ensure you import your Order model
from ai_vehicle.models import HeadQuarter
import requests, os, csv, random
from django.utils.dateparse import parse_date
from django.db.models import Q
from datetime import datetime

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
        orders=Order.objects.filter(order_status="delivered", warehouse__primary= True)
        context={
            'orders':orders,
        }
        return render(request, 'home/payments.html',context)

@csrf_exempt
def vehicles(request):
    if request.method == 'POST':

        print("vehicles ",request.POST)
        print("vehicles Files ", request.FILES)
        truck_name=request.POST.get('truck_name')
        driver_name=request.POST.get('driver_name')
        driver_email=request.POST.get('driver_email')
        truck_number=request.POST.get('truck_number')
        capacity=request.POST.get('capacity_volume')
        cost_per_km=request.POST.get('cost_per_km')
        contact_number=request.POST.get('contact_number')

        truck_type=request.POST.get('truck_type')
        truck_image = request.FILES.get('truck_image')
        make=request.POST.get('make')
        model=request.POST.get('model')
        year=request.POST.get('year')
        mileage=request.POST.get('mileage')
        license_type=request.POST.get('license_type')
        purchase_date=request.POST.get('purchase_date')
        
        try:
            truck=Truck.objects.get(truck_number=truck_number)
        except:

            truck = Truck.objects.create(
                truck_name=truck_name,
                driver_name=driver_name,
                driver_email=driver_email,
                truck_number=truck_number,
                capacity=capacity,
                cost_per_km=cost_per_km,
                contact_number=contact_number,

                truck_type=truck_type,
                truck_image=truck_image,
                make=make,
                model=model,
                year=year,
                mileage=mileage,
                license_type=license_type,
                purchase_date=purchase_date,
                warehouse=HeadQuarter.objects.get(primary=True)
                
            )
        return redirect('vehicles')

    else:
        # vehicles=Truck.objects.all()
        vehicles=Truck.objects.filter(warehouse__primary= True)

        context={
            'vehicles':vehicles,
        }
        return render(request, 'home/vehicles.html',context)

@csrf_exempt
def edit_vehicle(request, pk):
    try:
        vehicle = Truck.objects.get(id=pk)
    except Truck.DoesNotExist:
        return redirect('vehicles')

    if request.method == 'POST':

        print(request.POST,"POSTTTTTTTTT")

        if request.method == 'POST':
            error_messages = []  # List to hold any error messages

            
            vehicle.truck_name = request.POST.get('truck_name')
            if not vehicle.truck_name:error_messages.append('Truck name is required.')

            
            vehicle.driver_name = request.POST.get('driver_name')
            if not vehicle.driver_name:error_messages.append('Driver name is required.')

            
            vehicle.driver_email = request.POST.get('driver_email')
            if not vehicle.driver_email:
                error_messages.append('Driver email is required.')
            elif '@' not in vehicle.driver_email:  # Basic email validation
                error_messages.append('Invalid email format.')


            vehicle.make = request.POST.get('make')
            if not vehicle.make:error_messages.append('Truck number is required.')
            
            vehicle.truck_number = request.POST.get('truck_number')
            if not vehicle.truck_number:error_messages.append('Truck number is required.')

            vehicle.model = request.POST.get('model')
            if not vehicle.model:error_messages.append('Truck number is required.')

           
            vehicle.capacity = request.POST.get('capacity_volume')
            if not vehicle.capacity:error_messages.append('Capacity is required.')
            else:
                try:
                    vehicle.capacity = float(vehicle.capacity)  # Assuming capacity is a float
                except ValueError:
                    error_messages.append('Capacity must be a valid number.')

            
            vehicle.cost_per_km = request.POST.get('cost_per_km')
            if not vehicle.cost_per_km:error_messages.append('Cost per km is required.')
            else:
                try:
                    vehicle.cost_per_km = float(vehicle.cost_per_km)
                except ValueError:
                    error_messages.append('Cost per km must be a valid number.')

            
            vehicle.contact_number = request.POST.get('contact_number')
            if not vehicle.contact_number:error_messages.append('Contact number is required.')

            
            vehicle.truck_type = request.POST.get('truck_type')
            if not vehicle.truck_type:error_messages.append('Truck type is required.')

            

            vehicle.license_type = request.POST.get('license_type')
            if not vehicle.license_type:error_messages.append('license_type type is required.')

            
            year_str = request.POST.get('year')
            if year_str:
                try:
                    vehicle.year = int(year_str)  # Convert to integer
                except ValueError:
                    return render(request, 'home/edit_vehicle.html', {
                        'vehicle': vehicle,
                        'error': 'Year must be a valid number.'
                    })
            else: vehicle.year = None 


            vehicle.status = request.POST.get('status')
            if not vehicle.status:
                error_messages.append('Vehicle status is required.')

            mileage_str = request.POST.get('mileage')
            if mileage_str:
                try:
                    vehicle.mileage = float(mileage_str)  # Convert to float
                except ValueError:
                    error_messages.append('Mileage must be a valid number.')
            else:
                error_messages.append('Truck mileage is required.')

        
            purchase_date_str = request.POST.get('purchase_date')
            if purchase_date_str:
                try:
                    purchase_date = timezone.datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
                vehicle.purchase_date = purchase_date  
            else:
                vehicle.purchase_date = None

            vehicle.save()
            return redirect('vehicles')

    context = {
        'vehicle': vehicle,
    }
    return render(request, 'home/edit_vehicle.html', context)

@csrf_exempt
def add_service(request,pk):
    if request.method == 'POST':
        service_date=request.POST.get('service_date')
        service_description=request.POST.get('service_description')
        parts_changed=request.POST.get('parts_changed')
        warranty_period=request.POST.get('warranty_period')
        cost=request.POST.get('cost')

        truck=Truck.objects.get(id=pk)

        # parts_changed

        service=ServiceRecord.objects.create(truck=truck,
                                             service_date=service_date,
                                             service_description=service_description,
                                             cost=cost,
                                             parts_changed=parts_changed
                                             )

        return redirect('vehicles')
    
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
def delete_vehicle(request,pk):
    print(request.POST,"defres")
    if request.method == 'POST':
        vechcle=request.POST.get('truck_id')
        vv=Truck.objects.filter(id=vechcle).delete()
        return redirect('vehicles')
    
@csrf_exempt
def reset_assinged_trucks(request):
    Truck.objects.filter().update(available=True, routedata=None)
    Order.objects.filter(warehouse__primary= True).update(assigned_truck=None)
    return redirect('vehicles')
    
@csrf_exempt
def escalationteam(request):
    if request.method == 'POST':
        print("welcome ji")
        return redirect('home')  # Redirect to home or any other page
    
    else:
        orders=Order.objects.filter(order_status="delivered",payment_status="escalation_pending").order_by("-id")
        all_orders=Order.objects.filter(order_status="delivered").order_by("-id")
        context={
            'orders':orders,
            'all_orders':all_orders,
        }
        return render(request, 'home/escalation-team.html',context)

from django.http import HttpResponse, FileResponse, JsonResponse  
from django.utils.dateparse import parse_date
from django.db.models import Q
from datetime import datetime




@csrf_exempt
def reports(request):
    if request.method == 'POST':
        print(request.POST,"dataaaaaaaaaaaaaaaaaaaaaa")
        wids = request.POST.get('wids')
        strat_date = request.POST.get('strat_date')
        end_date = request.POST.get('end_date')

        orderstrat_date = request.POST.get('selectorderstart')
        orderend_date = request.POST.get('selectorderend')
        orderstatus = request.POST.get('selectedValueo')

        

        try:
            trucks_list=[]
            if wids == 'All Warehouse':
                print("all")

                if orderstatus == 'All':
                    print("all")
                    orders=Order.objects.all().order_by('-id')
                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))
                else:
                    orders=Order.objects.filter(order_status=orderstatus).order_by('-id')
                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))


                feedback=Feedback.objects.all().order_by('-id')
                feedback_list = list(feedback.values(
                'id', 'order__product_name', 'rating_text', 'description', 'order__cname',
                ))

                warehouses=HeadQuarter.objects.all().order_by('-id')
                warehouse_list = list(warehouses.values(
                'id', 'name', 'total_stock', 'available_stock', 'left_stock',
                ))

                trucks = Truck.objects.all().order_by('-id')
                trucks_list = list(trucks.values(
                'id', 'truck_name', 'truck_type', 'truck_image', 'truck_number',
                'capacity', 'make', 'model', 'year', 'mileage', 'license_type',
                'truck_order', 'cost_per_km', 'status', 'purchase_date', 
                'last_service_date', 'driver_name', 'driver_email', 'contact_number',
                'driver_order', 'on_time_deliveries', 'late_deliveries', 'driver_travel',
                'languages', 'available', 
                'warehouse__name',  # Include warehouse name
                ))


                 # Parse dates to ensure proper format

                warehouse_total_order = Order.objects.all().count()
                warehouse_pending_order = 0
                warehouse_complete_order = 0

                if strat_date or end_date:

                    if strat_date:
                        # Convert to datetime object
                        strat_date = datetime.strptime(strat_date, "%d %b, %Y").date()

                    if end_date:
                        # Convert to datetime object
                        end_date = datetime.strptime(end_date, "%d %b, %Y").date()


                    # If date range is provided, filter orders
                    if strat_date or end_date:
                        if strat_date and not end_date:
                            print("strat_date and not end_date")
                            warehouse_pending_order = Order.objects.filter(
                                order_status='pending',
                                created_at__date=strat_date
                            ).count()
                            warehouse_complete_order = Order.objects.filter(
                                order_status='delivered',
                                created_at__date=strat_date
                            ).count()

                        elif strat_date and end_date:
                            print("strat_date and end_date")
                            warehouse_pending_order = Order.objects.filter(
                                order_status='pending',
                                created_at__date__range=[strat_date, end_date]
                            ).count()
                            warehouse_complete_order = Order.objects.filter(
                                order_status='delivered',
                                created_at__date__range=[strat_date, end_date]
                            ).count()

                        elif end_date and not strat_date:
                            print("end_date only")
                            warehouse_pending_order = Order.objects.filter(
                                order_status='pending',
                                created_at__date__lte=end_date
                            ).count()
                            warehouse_complete_order = Order.objects.filter(
                                order_status='delivered',
                                created_at__date__lte=end_date
                            ).count()

                    # Calculate within_time and out_of_time based on truck deliveries
                    within_time = sum(truck['on_time_deliveries'] for truck in trucks_list)
                    out_of_time = sum(truck['late_deliveries'] for truck in trucks_list)

                    return JsonResponse({
                        'trucks': trucks_list,
                        'warehouse_total_order': warehouse_total_order,
                        'warehouse_pending_order': warehouse_pending_order,
                        'warehouse_complete_order': warehouse_complete_order,
                        'within_time': within_time,
                        'out_of_time': out_of_time,
                        'status': 'SENT'
                    }, status=200)
                    

                within_time = sum(truck['on_time_deliveries'] for truck in trucks_list)
                out_of_time = sum(truck['late_deliveries'] for truck in trucks_list)
                warehouse_total_order = Order.objects.all().count()
                warehouse_pending_order = Order.objects.filter(order_status='pending').count()
                warehouse_complete_order = Order.objects.filter(order_status='delivered').count()

                return JsonResponse({
                                'trucks': trucks_list,
                                'warehouse_total_order': warehouse_total_order,
                                'warehouse_pending_order': warehouse_pending_order,
                                'warehouse_complete_order': warehouse_complete_order,
                                'within_time': within_time,
                                'out_of_time': out_of_time,
                                'order_list':order_list,
                                'warehouse_list':warehouse_list,
                                'feedback_list':feedback_list,
                                'status': 'SENT'
                                }, 
                                status=200)

            else:
                
                warehouse = HeadQuarter.objects.get(id=wids)

                print(warehouse,"warehouse,,,,,,,,,,,,")

                if orderstrat_date and orderend_date:
                    orderstrat_date = datetime.strptime(strat_date, "%d %b, %Y").date()
                    orderend_date = datetime.strptime(end_date, "%d %b, %Y").date()

                   

                if orderstatus == 'All':
                    orders=Order.objects.filter(warehouse=warehouse).order_by('-id')

                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))

                else:
                    orders=Order.objects.filter(order_status=orderstatus,warehouse=warehouse).order_by('-id')
                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))


                feedback=Feedback.objects.filter(order__warehouse=warehouse).order_by('-id')
                feedback_list = list(feedback.values(
                'id', 'order__product_name', 'rating_text', 'description', 'order__cname',
                ))

                warehouse_list = [
                    {
                        'id': warehouse.id,
                        'name': warehouse.name,
                        'total_stock': warehouse.total_stock,
                        'available_stock': warehouse.available_stock,
                        'left_stock': warehouse.left_stock,
                    }
                ]


                trucks = Truck.objects.filter(warehouse=warehouse).order_by('-id')
                trucks_list = list(trucks.values(
                    'id', 'truck_name', 'truck_type', 'truck_image', 'truck_number',
                    'capacity', 'make', 'model', 'year', 'mileage', 'license_type',
                    'truck_order', 'cost_per_km', 'status', 'purchase_date', 
                    'last_service_date', 'driver_name', 'driver_email', 'contact_number',
                    'driver_order', 'on_time_deliveries', 'late_deliveries', 'driver_travel',
                    'languages', 'available', 
                    'warehouse__name',               
                ))


                if strat_date or end_date:
                    if strat_date:
                        # Convert to datetime object
                        strat_date = datetime.strptime(strat_date, "%d %b, %Y").date()

                    if end_date:
                        # Convert to datetime object
                        end_date = datetime.strptime(end_date, "%d %b, %Y").date()

                    # Initialize order counters
                    warehouse_total_order = Order.objects.filter(warehouse=warehouse).count()
                    warehouse_pending_order = 0
                    warehouse_complete_order = 0

                    # Filter orders based on the dates
                    if strat_date and not end_date:
                        print("Orders created on the start date")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date=strat_date
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date
                        ).count()
                        # Count orders delivered on time on the start date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date,
                            delivery_time__lte=strat_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date,
                            delivery_time__gt=strat_date # assuming you have delivery_time field
                        ).count()

                    elif strat_date and end_date:
                        print("Orders created between start date and end date (inclusive)")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date__range=[strat_date, end_date]
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date]
                        ).count()
                        # Count orders delivered within time between start date and end date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date],
                            delivery_time__lte=end_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date],
                            delivery_time__gt=end_date # assuming you have delivery_time field
                        ).count()

                    elif end_date and not strat_date:
                        print("Orders created before end date")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date__lte=end_date
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date
                        ).count()
                        # Count orders delivered on time before end date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date,
                            delivery_time__lte=end_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date,
                            delivery_time__gt=end_date # assuming you have delivery_time field
                        ).count()

                    print(within_time,"within_time")

                    return JsonResponse({
                        'trucks': trucks_list,
                        'warehouse_total_order': warehouse_total_order,
                        'warehouse_pending_order': warehouse_pending_order,
                        'warehouse_complete_order': warehouse_complete_order,
                        'within_time': within_time,
                        'out_of_time': out_of_time,
                        'status': 'SENT'
                    }, status=200)
                    
                warehouse_pending_order = Order.objects.filter(
                    warehouse=warehouse, 
                    order_status='pending'
                ).count()

                # Count delivered or completed orders for the specific warehouse
                warehouse_complete_order = Order.objects.filter(
                    warehouse=warehouse, 
                    order_status__in=['delivered', 'completed']
                ).count()

                # Calculate the total orders
                warehouse_total_order = warehouse_pending_order + warehouse_complete_order

                within_time = sum(truck['on_time_deliveries'] for truck in trucks_list)
                out_of_time = sum(truck['late_deliveries'] for truck in trucks_list)


                print(feedback_list,"feedback_listfeedback_list")

                return JsonResponse({
                                'trucks': trucks_list,
                                'warehouse_total_order': warehouse_total_order,
                                'warehouse_pending_order': warehouse_pending_order,
                                'warehouse_complete_order': warehouse_complete_order,
                                'within_time': within_time,
                                'out_of_time': out_of_time,
                                'warehouse_list':warehouse_list,
                                'feedback_list':feedback_list,
                                'order_list':order_list,


                                'status': 'SENT'
                                }, 
                                status=200)
        
        except HeadQuarter.DoesNotExist:
            return JsonResponse({'status': 'NOT FOUND'}, status=404)
    else:
        warehouse = HeadQuarter.objects.all()
        trucks = Truck.objects.all().order_by('-id')

        orders=Order.objects.all()

        all_co2_emission_reduction = 0  # Use 0 instead of an empty string
        for truck in orders:
            if truck.co2_emission_reduction:
                truck.co2_emission_reduction=truck.co2_emission_reduction
            else:
                truck.co2_emission_reduction = 0

            all_co2_emission_reduction += truck.co2_emission_reduction

        all_fuel_consumption = 0  # Use 0 instead of an empty string
        for truck in orders:
            if truck.fuel_consumption:
                truck.fuel_consumption=truck.fuel_consumption
            else:
                truck.fuel_consumption = 0

            all_fuel_consumption += truck.fuel_consumption

        all_fuel_savings = 0  # Use 0 instead of an empty string
        for truck in orders:
            if truck.fuel_savings:
                truck.fuel_savings=truck.fuel_savings
            else:
                truck.fuel_savings = 0

            all_fuel_savings += truck.fuel_savings



        context = {
            'warehouses': warehouse,
            'all_co2_emission_reduction':all_co2_emission_reduction,
            'all_fuel_savings':all_fuel_savings,
            'all_fuel_consumption':all_fuel_consumption,
            'trucks':trucks,
        }
        return render(request, 'home/reports.html', context)


from django.db.models import Sum

@csrf_exempt
def post_reports(request):
    if request.method == 'POST':
        print(request.POST,"dataaaaaaaaaaaaaaaaaaaaaa here")


        wids = request.POST.get('wids')
        orderstatus = request.POST.get('selectedValueo')
        strat_date = request.POST.get('strat_date')
        end_date = request.POST.get('end_date')

        orderstrat_date = request.POST.get('selectorderstart')
        orderend_date = request.POST.get('selectorderend')
        
       

        try:
            trucks_list=[]
            if wids == 'All_Warehouse':
                print("all ware house")

                trucks_list = Truck.objects.all().order_by('-id')
                for i in  trucks_list:
                    i.on_time_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True).count()
                    i.late_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True).count()

                    total_distance = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('route_distance'))['total']
                    i.driver_travel = total_distance if total_distance is not None else 0

                    total_fuel_consumption = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('fuel_consumption'))['total']
                    i.fuel = total_fuel_consumption if total_fuel_consumption is not None else 0 

                    total_load = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('quantity'))['total']
                    i.deleverd_load = total_load if total_load is not None else 0


                if orderstatus == 'All_orders':
                    order_list=Order.objects.all()
                else:
                    order_list=Order.objects.filter(order_status=orderstatus).order_by('-id')

                within_time = order_list.filter(
                    Q(on_time_delivery=True) & (Q(order_status='delivered') | Q(order_status='completed'))
                ).count()

                out_of_time = order_list.filter(
                    Q(on_time_delivery=False) & (Q(order_status='delivered') | Q(order_status='completed'))
                ).count()

                warehouses = HeadQuarter.objects.all()
                trucks = Truck.objects.all().order_by('-id')
                orders=Order.objects.all()
                warehouse_total_order = Order.objects.all().count()
                warehouse_cancel_order = Order.objects.filter(order_status='canceled').count()
                warehouse_pending_order = Order.objects.filter(order_status='pending').count()
                warehouse_complete_order = Order.objects.filter(Q(order_status='delivered') or Q(order_status='completed')).count()


                if strat_date or end_date:
                    if strat_date:strat_date = datetime.strptime(strat_date, "%d %b, %Y").date()
                    if end_date:end_date = datetime.strptime(end_date, "%d %b, %Y").date()

                    if strat_date or end_date:
                        if strat_date and end_date:

                            for i in  trucks_list:
                                i.on_time_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True,created_at__date__range=[strat_date, end_date]).count()
                                i.late_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True,created_at__date__range=[strat_date, end_date]).count()

                                total_distance = Order.objects.filter(assigned_truck=i,created_at__date__range=[strat_date, end_date]).aggregate(total=Sum('route_distance'))['total']
                                i.driver_travel = total_distance if total_distance is not None else 0

                                total_fuel_consumption = Order.objects.filter(assigned_truck=i,created_at__date__range=[strat_date, end_date]).aggregate(total=Sum('fuel_consumption'))['total']
                                i.fuel = total_fuel_consumption if total_fuel_consumption is not None else 0 

                                total_load = Order.objects.filter(assigned_truck=i,created_at__date__range=[strat_date, end_date]).aggregate(total=Sum('quantity'))['total']
                                i.deleverd_load = total_load if total_load is not None else 0

                                print(i.on_time_deliveries,"i.on_time_deliveriesi.on_time_deliveries")


                            order_list=order_list.filter(
                                Q(on_time_delivery=True) & (Q(order_status='delivered') | Q(order_status='completed'))
                            ).count()

                            if orderstatus == 'All_orders':
                                order_list=Order.objects.filter(created_at__date__range=[strat_date, end_date])
                            else:
                                order_list=Order.objects.filter(order_status=orderstatus,created_at__date__range=[strat_date, end_date]).order_by('-id')

                            warehouse_total_order = Order.objects.filter(created_at__date__range=[strat_date, end_date]).count()
                            warehouse_cancel_order = Order.objects.filter(order_status='canceled',created_at__date__range=[strat_date, end_date]).count()
                            warehouse_pending_order = Order.objects.filter(order_status='pending',created_at__date__range=[strat_date, end_date]).count()
                            warehouse_complete_order = Order.objects.filter(Q(order_status='delivered',created_at__date__range=[strat_date, end_date]) or Q(order_status='completed',created_at__date__range=[strat_date, end_date])).count()

                            within_time = order_list.filter(
                                Q(on_time_delivery=True) & (Q(order_status='delivered',created_at__date__range=[strat_date, end_date]) | Q(order_status='completed',created_at__date__range=[strat_date, end_date]))
                            ).count()

                            out_of_time = order_list.filter(
                                Q(on_time_delivery=False) & (Q(order_status='delivered',created_at__date__range=[strat_date, end_date]) | Q(order_status='completed',created_at__date__range=[strat_date, end_date]))
                            ).count()

                           

                            

                context={
                    'warehouses':warehouses,
                    'warehouse_list':warehouses,
                    'warehouse_total_order': warehouse_total_order,
                    'warehouse_cancel_order': warehouse_cancel_order,
                    'warehouse_pending_order': warehouse_pending_order,
                    'warehouse_complete_order': warehouse_complete_order,
                    'within_time': within_time,
                    'out_of_time': out_of_time,
                     'trucks': trucks_list,
                    'order_list':order_list,
                               
                                'feedback_list':'',
                                'status': 'SENT'
                }
                return render(request, 'home/post_reports.html', context)


            else:
                print("else part")
                warehouse = HeadQuarter.objects.get(id=wids)
                print(warehouse,"warehouse,,,,,,,,,,,,")
                if orderstrat_date and orderend_date:
                    orderstrat_date = datetime.strptime(strat_date, "%d %b, %Y").date()
                    orderend_date = datetime.strptime(end_date, "%d %b, %Y").date()

                if orderstatus == 'All':
                    orders=Order.objects.filter(warehouse=warehouse).order_by('-id')

                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))

                else:
                    orders=Order.objects.filter(order_status=orderstatus,warehouse=warehouse).order_by('-id')
                    order_list = list(orders.values(
                    'id', 'product_name', 'quantity', 'destination', 'cname','order_status'
                    ))


                feedback=Feedback.objects.filter(order__warehouse=warehouse).order_by('-id')
                feedback_list = list(feedback.values(
                'id', 'order__product_name', 'rating_text', 'description', 'order__cname',
                ))

                warehouse_list = [
                    {
                        'id': warehouse.id,
                        'name': warehouse.name,
                        'total_stock': warehouse.total_stock,
                        'available_stock': warehouse.available_stock,
                        'left_stock': warehouse.left_stock,
                    }
                ]


                trucks = Truck.objects.filter(warehouse=warehouse).order_by('-id')
                trucks_list = list(trucks.values(
                    'id', 'truck_name', 'truck_type', 'truck_image', 'truck_number',
                    'capacity', 'make', 'model', 'year', 'mileage', 'license_type',
                    'truck_order', 'cost_per_km', 'status', 'purchase_date', 
                    'last_service_date', 'driver_name', 'driver_email', 'contact_number',
                    'driver_order', 'on_time_deliveries', 'late_deliveries', 'driver_travel',
                    'languages', 'available', 
                    'warehouse__name',               
                ))


                if strat_date or end_date:
                    if strat_date:
                        # Convert to datetime object
                        strat_date = datetime.strptime(strat_date, "%d %b, %Y").date()

                    if end_date:
                        # Convert to datetime object
                        end_date = datetime.strptime(end_date, "%d %b, %Y").date()

                    # Initialize order counters
                    warehouse_total_order = Order.objects.filter(warehouse=warehouse).count()
                    warehouse_pending_order = 0
                    warehouse_complete_order = 0

                    # Filter orders based on the dates
                    if strat_date and not end_date:
                        print("Orders created on the start date")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date=strat_date
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date
                        ).count()
                        # Count orders delivered on time on the start date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date,
                            delivery_time__lte=strat_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date=strat_date,
                            delivery_time__gt=strat_date # assuming you have delivery_time field
                        ).count()

                    elif strat_date and end_date:
                        print("Orders created between start date and end date (inclusive)")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date__range=[strat_date, end_date]
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date]
                        ).count()
                        # Count orders delivered within time between start date and end date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date],
                            delivery_time__lte=end_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__range=[strat_date, end_date],
                            delivery_time__gt=end_date # assuming you have delivery_time field
                        ).count()

                    elif end_date and not strat_date:
                        print("Orders created before end date")
                        warehouse_pending_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='pending',
                            created_at__date__lte=end_date
                        ).count()
                        warehouse_complete_order = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date
                        ).count()
                        # Count orders delivered on time before end date
                        within_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date,
                            delivery_time__lte=end_date # assuming you have delivery_time field
                        ).count()
                        out_of_time = Order.objects.filter(
                            warehouse=warehouse,
                            order_status='delivered',
                            created_at__date__lte=end_date,
                            delivery_time__gt=end_date # assuming you have delivery_time field
                        ).count()

                    print(within_time,"within_time")

                    return JsonResponse({
                        'trucks': trucks_list,
                        'warehouse_total_order': warehouse_total_order,
                        'warehouse_pending_order': warehouse_pending_order,
                        'warehouse_complete_order': warehouse_complete_order,
                        'within_time': within_time,
                        'out_of_time': out_of_time,
                        'status': 'SENT'
                    }, status=200)
                    
                warehouse_pending_order = Order.objects.filter(
                    warehouse=warehouse, 
                    order_status='pending'
                ).count()

                # Count delivered or completed orders for the specific warehouse
                warehouse_complete_order = Order.objects.filter(
                    warehouse=warehouse, 
                    order_status__in=['delivered', 'completed']
                ).count()

                # Calculate the total orders
                warehouse_total_order = warehouse_pending_order + warehouse_complete_order

                within_time = sum(truck['on_time_deliveries'] for truck in trucks_list)
                out_of_time = sum(truck['late_deliveries'] for truck in trucks_list)


                print(feedback_list,"feedback_listfeedback_list")

                return JsonResponse({
                                'trucks': trucks_list,
                                'warehouse_total_order': warehouse_total_order,
                                'warehouse_pending_order': warehouse_pending_order,
                                'warehouse_complete_order': warehouse_complete_order,
                                'within_time': within_time,
                                'out_of_time': out_of_time,
                                'warehouse_list':warehouse_list,
                                'feedback_list':feedback_list,
                                'order_list':order_list,


                                'status': 'SENT'
                                }, 
                                status=200)
        
        except HeadQuarter.DoesNotExist:
            return JsonResponse({'status': 'NOT FOUND'}, status=404)
    else:

        warehouse = HeadQuarter.objects.all()



        trucks = Truck.objects.all().order_by('-id')
        for i in trucks:
            i.on_time_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True).count()
            i.late_deliveries=Order.objects.filter(assigned_truck=i,on_time_delivery=True).count()

            total_distance = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('route_distance'))['total']
            i.driver_travel = total_distance if total_distance is not None else 0

            total_fuel_consumption = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('fuel_consumption'))['total']
            i.fuel = total_fuel_consumption if total_fuel_consumption is not None else 0 

            print(i.fuel,"fuelllllllllllllll")



            total_load = Order.objects.filter(assigned_truck=i).aggregate(total=Sum('quantity'))['total']
            i.deleverd_load = total_load if total_load is not None else 0  


        order_list=Order.objects.all()

        warehouse_total_order = Order.objects.all().count()
        warehouse_cancel_order = Order.objects.filter(order_status='canceled').count()
        warehouse_complete_order = Order.objects.filter(Q(order_status='delivered') or Q(order_status='completed')).count()
        warehouse_pending_order = Order.objects.filter(order_status='pending').count()

        within_time = order_list.filter(
            Q(on_time_delivery=True) & (Q(order_status='delivered') | Q(order_status='completed'))
        ).count()

        out_of_time = order_list.filter(
            Q(on_time_delivery=False) & (Q(order_status='delivered') | Q(order_status='completed'))
        ).count()



        all_co2_emission_reduction = 0  
        for truck in order_list:
            if truck.co2_emission_reduction:
                truck.co2_emission_reduction=truck.co2_emission_reduction
            else:
                truck.co2_emission_reduction = 0

            all_co2_emission_reduction += truck.co2_emission_reduction

        all_fuel_consumption = 0  # Use 0 instead of an empty string
        for truck in order_list:
            if truck.fuel_consumption:
                truck.fuel_consumption=truck.fuel_consumption
            else:
                truck.fuel_consumption = 0

            all_fuel_consumption += truck.fuel_consumption

        all_fuel_savings = 0  # Use 0 instead of an empty string
        for truck in order_list:
            if truck.fuel_savings:
                truck.fuel_savings=truck.fuel_savings
            else:
                truck.fuel_savings = 0

            all_fuel_savings += truck.fuel_savings



        context = {
            'warehouses': warehouse,
            'warehouse_total_order': warehouse_total_order,
            'warehouse_cancel_order': warehouse_cancel_order,
            'warehouse_complete_order': warehouse_complete_order,
            "within_time":within_time,
            'out_of_time':out_of_time,
            'warehouse_pending_order':warehouse_pending_order,
            'order_list':order_list,








            'all_co2_emission_reduction':all_co2_emission_reduction,
            'all_fuel_savings':all_fuel_savings,
            'all_fuel_consumption':all_fuel_consumption,
            'trucks':trucks,
        }
        return render(request, 'home/post_reports.html', context)
















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
def drivers(request, pk=None):
    if request.method == 'POST':
        print("welcome ji")
        email_id=request.POST.get('email_id')
        truck=Truck.objects.filter(driver_email=email_id)
        return redirect('driver_single', truck.first().id)
        # context={ 'truck':truck.first() }
        # return render(request, 'home/single_driver.html',context)
    else:
        truck=Truck.objects.filter(id=pk)
        context={ 'truck':truck.first() }
        return render(request, 'home/single_driver.html',context)
    
@csrf_exempt
def admin_single_vehicle(request, pk=None):
    if request.method == 'POST':
        print("welcome ji")
        email_id=request.POST.get('email_id')
        truck=Truck.objects.filter(driver_email=email_id)
        return redirect('driver_single', truck.first().id)
        
    else:
        truck=Truck.objects.filter(id=pk)
        services=ServiceRecord.objects.filter(truck=truck.first().id).order_by('-id')

        context={ 'truck':truck.first() ,'services':services}
        return render(request, 'home/admin_single_vehicle.html',context)

@csrf_exempt
def report_issue(request, pk=None):
    if request.method == 'POST':

        try:
            order=Order.objects.get(id=request.POST.get('order_id'))
            order.report_status=True
            order.save()
        except:
            pass


        report=Report_order.objects.create(order_id=request.POST.get('order_id'),issue=request.POST.get('issue_text'), truck_id=request.POST.get('truck_id'))



        return redirect(reverse('driver_single', kwargs={'pk': request.POST.get('truck_id')}))
    else:
        return redirect(reverse('driver_single', kwargs={'pk': pk})) 

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


            due_date_formatted = order.due_payment_date.strftime('%Y-%m-%d')

            content=f"Your order has been delivered successfully! We hope everything arrived just as you expected.Kindly complete your payment by {due_date_formatted}, or earlier.Thank you for choosing us!"

            html_message = render_to_string('home/orderemail.html', {'user': order.cname,'content':content})
            try: send_mail('Order delivered to you successfully.', strip_tags(html_message), settings.EMAIL_HOST_USER, [order.email,], html_message=html_message)
            except Exception as e: print("\n\n______________________unable to send mail", e)

            Notifications.objects.create(content=f"Your order has been successfully delivered. Kindly complete your payment by <strong>{due_date_formatted}</strong>, or earlier.", title='Order delivered', receiver=order,count=1)

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            # return redirect(reverse('single_order', kwargs={'pk': pk}))
    
    else:
        order=Order.objects.get(id=pk)
        context={
            'order':order,
        }
        return render(request, 'home/single_order.html',context)

def changedurations(duration_str):
    a = duration_str.split(' days ')
    print("a___", a)
    time_part = a[1]
    hours, minutes, seconds = map(float, time_part.split(':'))

    # Create a timedelta object
    return timedelta(days=int(a[0]), hours=int(hours), minutes=int(minutes), seconds=seconds)
    # if len(a) == 2:
    #     time_part = a[1]
    #     hours, minutes, seconds = map(float, time_part.split(':'))

    #     # Create a timedelta object
    #     return timedelta(days=int(a[0]), hours=int(hours), minutes=int(minutes), seconds=seconds)
    # else:
    #     # Create a timedelta object
    #     return timedelta(days=int(1), hours=int(0), minutes=int(0), seconds=0)

@csrf_exempt
def upload_orders(request):
    if request.method == 'POST':
        
        if not HeadQuarter.objects.filter(primary=True):
            messages.success(request, 'Please setup a primary warehouse.')
            return redirect('upload_orders')

        csv_file = request.FILES.get('file')
        if csv_file:
            csv_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            next(csv_reader) 


            truckids = [i.id for i in Truck.objects.all()]
            headqids = [i.id for i in HeadQuarter.objects.all()]
            for row in csv_reader:
                print(row, "row....................")  
                cname = row[0]  
                email = row[1]  
                product_name = row[2]  
                quantity = int(row[3]) 
                # from_location = row[4]  
                destination = row[4]  
                payment_amount = float(row[5]) 
                lat = row[6] if row[6] else None
                long = row[7] if row[7] else None



                # name	email	product_name	quantity	destination	payment_amount	lat	long	



                order = Order.objects.create(
                    product_name=product_name,
                    quantity=quantity,
                    destination=destination,
                    # from_location=from_location,
                    email=email,
                    cname=cname,
                    payment_amount=payment_amount,
                    # order_status='pending',  
                    lat=lat,
                    long=long,
                    # warehouse=HeadQuarter.objects.get(primary=True),
                    # created_at                      =   datetime.now(),
                    # updated_at                      =   datetime.now(),
                    warehouse                       =   HeadQuarter.objects.get(id=random.choice(headqids)),
                    assigned_truck                  =   None if row[14] == 'pending' else Truck.objects.get(id=random.choice(truckids)),
                    # warehouse                       =   HeadQuarter.objects.get(id=int(row[12])+3),
                    # assigned_truck                  =   None if row[14] == 'pending' else Truck.objects.get(id=4),

                    created_at                      =   datetime.fromisoformat(row[8]),
                    updated_at                      =   datetime.fromisoformat(row[8]),
                    delivered_date                  =   datetime.fromisoformat(row[9]),
                    payment_date                    =   datetime.fromisoformat(row[10]),
                    # delivery_time                   =   datetime.fromisoformat(row[17]),
                    # estimated_delivery_time         =   datetime.datetime.fromisoformat(row[26]),

                    # hours_worked                    =   row[22],
                    idle_time                       =   changedurations(row[23]),
                    time_saved                      =   changedurations(row[25]),

                    route_adherence                 =   bool(int(row[24])),
                    late_payment_status             =   bool(int(row[11])),
                    on_time_delivery                =   bool(int(row[19])),
                    rerouted                        =   bool(int(row[30])),

                    payment_status                  =   row[13],
                    order_status                    =   row[14],
                    route_distance                  =   row[16],
                    fuel_consumption                =   row[18],
                    fuel_savings                    =   row[20],
                    vehicle_maintenance_savings     =   row[21],
                    co2_emission_reduction          =   row[27],
                    green_route                     =   row[28],
                    adjusted_stops                  =   row[29],
                    
                )
                   
        return redirect('upload_orders') 
    
    else:
        orders=Order.objects.filter(warehouse__primary=True)
        report_orders=Order.objects.filter(report_status=True)
        context={
            'orders':orders,
            'report_orders':report_orders,
            'warehouses':HeadQuarter.objects.all()
        }
        return render(request, 'home/orders.html',context) 

def delete_all_orders(request):
    if request.method == 'POST':
        Notifications.objects.filter(receiver__warehouse__primary= True).delete()
        Order.objects.filter(warehouse__primary= True).delete()  
        Truck.objects.filter().update(available=True, routedata=None)
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
    delivered_orders = Order.objects.filter(order_status="delivered", warehouse__primary= True)
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




