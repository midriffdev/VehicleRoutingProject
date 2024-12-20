from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, FileResponse, JsonResponse
# from huggingface_hub import login
# from transformers import AutoModelForCausalLM, AutoTokenizer
from google.maps import routeoptimization_v1 as ro
from geopy.geocoders import Nominatim, GoogleV3
from google.protobuf.json_format import MessageToDict, MessageToJson
from django.core.files.base import ContentFile
from django.contrib import messages
import datetime, requests, json, subprocess
from home.models import Order, Truck
from .models import GenRoutes, HeadQuarter, Truckdata, routedata

# Get the access token
# def get_access_token():
#     result = subprocess.run(
#         ['gcloud', 'auth', 'application-default', 'print-access-token'], 
#         stdout=subprocess.PIPE
#     )
#     return result.stdout.decode('utf-8').strip()

def headquarter(request):
    
    if request.method == 'POST':
        print("Request.POST__________ ",request.POST)
        if request.POST.get('action') == 'edit':
            hq = HeadQuarter.objects.filter(id=request.POST.get('hqid')).update(name = request.POST.get('hname'),product_name = request.POST.get('product_name'),total_stock = request.POST.get('total_stock'), lat = request.POST.get('latitude'), long = request.POST.get('longitude'))
        else:
            hq = HeadQuarter.objects.create(name = request.POST.get('hname'),product_name = request.POST.get('product_name'), lat = request.POST.get('latitude'),total_stock = request.POST.get('total_stock'), long = request.POST.get('longitude'))
        return redirect('headquarter')
    else:
        hq = HeadQuarter.objects.all()
        return render(request, 'home/headquarters.html',{'hq':hq})

def delete_hq(request,pk):
    hq=HeadQuarter.objects.filter(id=pk).delete()
    return redirect('headquarter')

def set_hq(request,pk):
    hq=HeadQuarter.objects.filter().update(primary=False)
    hq=HeadQuarter.objects.filter(id=pk).update(primary=True)
    return redirect('headquarter')

def get_lat_long(location_name):
    geolocator = GoogleV3(api_key=settings.GOOGLEMAPSKEY)
    # geolocator = Nominatim(user_agent="geoapiExercises12")
    location = geolocator.geocode(location_name)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return {"latitude": latitude,"longitude": longitude}
    else:
        print(f"\n\n__________location not found for {location_name}\n\n")
        return None

def download_json(request, route_id):
    gen_route = GenRoutes.objects.get(id=route_id)
    response = FileResponse(gen_route.ijson, as_attachment=True, filename='request.json')
    return response

def assign_routes_to_trucks(request, route_id):
    """assign trucks and set availabilty"""
    Truck.objects.filter(warehouse__primary= True).update(available=True, routedata=None) 
    genroute = GenRoutes.objects.get(id=route_id)
    for tdata in genroute.truckdata.all():
        tdata.truck.routedata = tdata.routedata
        tdata.truck.available = False
        tdata.truck.save()
        for ordr in tdata.routedata.orders.all():
            ordr.assigned_truck = tdata.truck
            ordr.save()
            ordr.warehouse.total_stock -= ordr.quantity
            ordr.warehouse.save()
    messages.success(request, 'Trucks has been assinged with respective orders.')
    return redirect('vehicles')

def fetchorders(request):
    # print("request.POST___________", request.POST)
    orders = []
    for wh in request.POST.getlist('wids[]'):
        temp = [{'text':f'{order.id} | {order.cname}', 'value':order.id} for order in Order.objects.filter(warehouse_id=wh, order_status='pending', assigned_truck=None)]
        orders.append( [HeadQuarter.objects.get(id=wh).name, temp] )
    return JsonResponse({'orders':orders, 'status':'SENT'}, status = 200)

def optimizeroute(olist, action='realtime'):
    # print("olist, realtime____________", olist, realtime)
    today = datetime.datetime.now()
    reqjson = {"shipments": [], "vehicles": [], 
    "global_start_time": datetime.datetime.combine(today, datetime.time(00,00,00)), 
    "global_end_time": datetime.datetime.combine(today+datetime.timedelta(days=7), datetime.time(23,59,59)) }

    # a, b = get_lat_long('una, hp')
    # return HttpResponse(f'{a}, {b}')
    if action == 'realtime':
        avl_trucks = Truck.objects.filter(available=True, warehouse__primary= True, on_service=False)
        avl_orders = Order.objects.filter(order_status='pending', assigned_truck=None, id__in=olist)
        whstock, less_stock = {}, []
        for i in avl_orders:
            if i.warehouse in whstock: whstock[i.warehouse] = int(whstock[i.warehouse]) + i.quantity
            else: whstock[i.warehouse] = i.quantity
        for k, v in whstock.items():
            if k.total_stock < v: less_stock.append([k.name, v-k.total_stock, k.product_name])
        print("\n\nStocks__________________",whstock, less_stock)
        if less_stock:
            return less_stock, {}, 'less_stock'
    elif action == 'review':
        avl_trucks = Truck.objects.filter(id__in=olist[0])
        avl_orders = Order.objects.filter(id__in=olist[1])
    elif action == 'upload':
        avl_trucks = Truck.objects.filter()
        avl_orders = Order.objects.filter(id__in=olist).exclude(order_status='pending')
    # print("alv______________", avl_orders, avl_trucks)
    if (not avl_trucks) : return [], {}, "no_trucks"
    if (not avl_orders) : return [], {}, "no_orders"
    for i in avl_trucks:
        temp = {}
        # temp["start_location"] = {"latitude": float(hq.lat),"longitude": float(hq.long)}
        temp["start_location"] = {"latitude": 30.718236,"longitude": 76.696300} # start location and (optional) end location of your drivers.
        temp["load_limits"] = {"weight": {"max_load": i.capacity}}
        temp["start_time_windows"] = [{"start_time": datetime.datetime.combine(today, i.start_time)}] 
        if i.end_time: temp["end_time_windows"] = [{"end_time": datetime.datetime.combine(today, i.end_time)}]
        # temp["start_time_windows"] = [{"start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")}] # means that the driver will leave his startLocation at exactly 08:00 and arrive at his endLocation by 12:00.
        # temp["end_time_windows"] = [{"end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")}]
        temp["label"] = f'{i.truck_name}--{i.truck_number}--{i.driver_name}'
        temp["cost_per_kilometer"] = int(i.cost_per_km) # "costPerKilometer": sets a baseline for your driving distance costs. GMPRO or any delivery route optimization package is going to try to route as many deliveries as possible for the smallest cost, so you need to tell GMPRO what these costs are in order for it to calculate an efficient route.
        reqjson["vehicles"].append(temp)

    for i in avl_orders:
        temp = {}
        temp['pickups'] = [{"arrival_location": {"latitude": float(i.warehouse.lat),"longitude": float(i.warehouse.long)}}]
        temp['deliveries'] = [{
                "arrival_location": {"latitude": float(i.lat),"longitude": float(i.long)} if i.lat else get_lat_long(i.destination),
                "duration": datetime.timedelta(seconds=900), # when the driver arrives, he will spend 10 minutes making the delivery.
                "time_windows": [{ # to make sure your driver only arrives there during business hours
                    "start_time": datetime.datetime.combine(today, i.opening_time),
                    "end_time": datetime.datetime.combine(today, i.closing_time)
                    # "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                    # "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
                }]
            }]
        temp["load_demands"] = {"weight": {"amount": i.quantity}}
        temp["label"] = f'DELIVERY_{i.destination}__{i.id}'
        reqjson["shipments"].append(temp) 

    print("\n\n____punching for response json")
    project_id="gmprotrial"
    client = ro.RouteOptimizationClient()
    grequest = ro.OptimizeToursRequest(
        parent=f'projects/{project_id}',
        model=reqjson,
        # populate_polylines=True
    )
    response = client.optimize_tours(request=grequest)
    # json_output = MessageToJson(response._pb) ## RESPONSE JSON
    return MessageToDict(response._pb), reqjson, 'done' # dict_output

    """for non real time, assign trucks and other parameters in orders record"""

# GMPRO DOCUMENTATION API hit trial
def getroute(request):
    if request.method == 'GET':
        return redirect('upload_orders')

    # REQUEST.POST
    print("\n\nrequest.POST____________", request.POST)    
    hq = HeadQuarter.objects.get(primary=True)

    dict_output, reqjson, status = optimizeroute(request.POST.getlist('orderslist'), action='realtime')

    if status != 'done':
        if status == "no_trucks":
            messages.success(request, 'No available trucks at the moment.')
            return redirect('upload_orders')
        if status == "no_orders":
            messages.success(request, 'No available orders.')
            return redirect('upload_orders')
        elif status == "less_stock":
            lstock = " & ".join([f' {a[1]} {a[2]} at {a[0]}' for a in dict_output])
            messages.success(request, f'Less Stocks: You need to add these stocks: { lstock } to process route analysis for the given orders.')
            return redirect('upload_orders')

    # print("\n\nresponse or routes____", dict_output)

    iroutes = []
    obtained_orders = []
    for data in dict_output['routes']:
        temp = {
        'truck'     : Truck.objects.get(truck_number=data['vehicleLabel'].split('--')[1]),
        'fstop'     : None,
        'lstop'     : None,
        'lorder'    : None,
        'stime'     : data.get('vehicleStartTime', None),
        # 'type'      : 'delivery',
        'order'     : [],
        'distance'  : 0,
        'tot_orders': 0,
        'timetaken' : 0,
        'fruits'    : [],
        }
        for i in data.get('visits', []):
            # if 'isPickup' in i:
            #     # temp['order'].append(0)
            #     temp['type']  = 'pickup'
            # else: 
            temp['order'].append( {"ord": Order.objects.get(id=i['shipmentLabel'].split('__')[1]), "is_pickup":'isPickup' in i, "etime":datetime.datetime.strptime(i['startTime'], "%Y-%m-%dT%H:%M:%SZ")} )
            
            temp['distance']    = data['metrics']['travelDistanceMeters']/1000.0
            temp['tot_orders']  = int(data['metrics']['performedShipmentCount'])
            temp['timetaken']   = datetime.timedelta(seconds=int(data['metrics']['totalDuration'].replace('s', '')))

        for od in range(0,len(temp['order'])):
            if od == 0: apple = [temp['order'][od]['is_pickup'], [temp['order'][od]['ord']], temp['order'][od]['etime']]
            else:
                prev = temp['order'][od-1]
                curr = temp['order'][od]
                if (curr['is_pickup'] and prev['is_pickup'] and (prev['ord'].warehouse == curr['ord'].warehouse)) or ((not curr['is_pickup']) and (not prev['is_pickup']) and (prev['ord'].cname == curr['ord'].cname)): 
                    apple[1].append(temp['order'][od]['ord'])
                else:
                    temp['fruits'].append(apple)
                    apple = [temp['order'][od]['is_pickup'], [temp['order'][od]['ord']], temp['order'][od]['etime']]
            if od == len(temp['order'])-1: temp['fruits'].append(apple)
        print("fruits_______________",temp['truck'].truck_name, temp['fruits'])
                
        obtained_orders.extend([i['ord'].id for i in temp['order']])
        if data.get('visits', []):
            # if data.get('visits', [])[-1]['shipmentLabel']:
            i = Order.objects.get(id=data.get('visits', [])[-1]['shipmentLabel'].split('__')[1])
            temp['lorder'] = i.id
            temp['fstop'], temp['lstop'] = int(len(data.get('visits', []))/2), i.destination
        iroutes.append(temp)
    pendingorders = Order.objects.filter(order_status='pending', warehouse__primary= True, assigned_truck=None).exclude(id__in=obtained_orders)
    pendingorders.quantity = sum([i.quantity for i in Order.objects.filter(order_status='pending').exclude(id__in=obtained_orders)])


    print("\n\n____making json downloadable__request.json ")
    newreqjson = reqjson
    newreqjson['global_start_time'] = newreqjson['global_start_time'].isoformat()
    newreqjson['global_end_time'] = newreqjson['global_end_time'].isoformat()
    for i in newreqjson['vehicles']:
        i['start_time_windows'][0]['start_time'] = i['start_time_windows'][0]['start_time'].isoformat()
        if 'end_time_windows' in i: i['end_time_windows'][0]['end_time']=i['end_time_windows'][0]['end_time'].isoformat()
    for i in newreqjson['shipments']:
        if 'deliveries' in i:
            # i['deliveries'][0]['duration'] = (datetime.datetime(1970, 1, 1) + i['deliveries'][0]['duration']).isoformat()
            i['deliveries'][0]['duration'] = '900s'
            if 'start_time' in i['deliveries'][0]['time_windows'][0]:
                i['deliveries'][0]['time_windows'][0]['start_time'] = i['deliveries'][0]['time_windows'][0]['start_time'].isoformat()
            i['deliveries'][0]['time_windows'][0]['end_time'] = i['deliveries'][0]['time_windows'][0]['end_time'].isoformat()
    json_file = ContentFile(json.dumps({"model": newreqjson, "populatePolylines": True}).encode('utf-8'), name='request.json')


    gen_route = GenRoutes.objects.create(ijson=json_file, warehouse=hq)
    gen_route.pendorders.set(pendingorders)
    for i in iroutes:
        if i['order']:
            b = routedata.objects.create(fstop=i['fstop'], lstop=i['lstop'], timetaken=i['timetaken'], tot_orders=i['tot_orders'], distance=i['distance'], last_order_id=i['lorder'])
            [b.orders.add(ord['ord']) for ord in i['order']]
            a = gen_route.truckdata.create(truck=i['truck'], routedata = b)
    gen_route.save()

    # print("\n\niroute______________s", iroutes, obtained_orders, pendingorders)
    # return HttpResponse(json_output['routes'])
    context={'iroutes':iroutes, 'gen_route_id':gen_route.id, 'pendingorders':pendingorders, 'notassignedyet':True}
    return render(request, 'home/ai-routes.html',context)

# GMPRO DOCUMENTATION API hit trial
def reload_getroute(request, rid):
    # hq = HeadQuarter.objects.get(primary=True)

    tlist = []
    olist = []
    for trk in GenRoutes.objects.get(id=rid).truckdata.all():
        tlist.append(trk.truck.id)
        olist.extend([ordr.id for ordr in trk.routedata.orders.all()])
    print("tlist, olist__________", tlist, olist)


    dict_output, reqjson, status = optimizeroute( (tlist, olist), action='review')
    print("\n\nresponse or routes____", dict_output)
    if status != 'done':
        messages.success(request, 'No available trucks at the moment.' if status=="no_trucks" else 'No available orders.')
        return redirect('upload_orders')

    iroutes = []
    obtained_orders = []
    for data in dict_output['routes']:
        temp = {
        'truck'     : Truck.objects.get(truck_number=data['vehicleLabel'].split('--')[1]),
        'fstop'     : None,
        'lstop'     : None,
        'lorder'    : None,
        'stime'     : data.get('vehicleStartTime', None),
        # 'type'      : 'delivery',
        'order'     : [],
        'distance'  : 0,
        'tot_orders': 0,
        'timetaken' : 0,
        }
        for i in data.get('visits', []):
            temp['order'].append( {"ord": Order.objects.get(id=i['shipmentLabel'].split('__')[1]), "is_pickup":'isPickup' in i, "etime":datetime.datetime.strptime(i['startTime'], "%Y-%m-%dT%H:%M:%SZ")} )
            
            temp['distance']    = data['metrics']['travelDistanceMeters']/1000.0
            temp['tot_orders']  = int(data['metrics']['performedShipmentCount'])
            temp['timetaken']   = datetime.timedelta(seconds=int(data['metrics']['totalDuration'].replace('s', '')))
            
        obtained_orders.extend([i['ord'].id for i in temp['order']])
        if data.get('visits', []):
            # if data.get('visits', [])[-1]['shipmentLabel']:
            i = Order.objects.get(id=data.get('visits', [])[-1]['shipmentLabel'].split('__')[1])
            temp['lorder'] = i.id
            temp['fstop'], temp['lstop'] = int(len(data.get('visits', []))/2), i.destination
        iroutes.append(temp)
    pendingorders = Order.objects.filter(order_status='pending', warehouse__primary= True, assigned_truck=None).exclude(id__in=obtained_orders)
    pendingorders.quantity = sum([i.quantity for i in Order.objects.filter(order_status='pending').exclude(id__in=obtained_orders)])

    print("\n\niroute______________s", iroutes, obtained_orders, pendingorders)
    return render(request, 'home/ai-routes.html',{'iroutes':iroutes, 'gen_route_id':rid, 'pendingorders':pendingorders, 'notassignedyet':False})

if True:
    # model={
    #     # "model": {
    #         "shipments": [
    #             {
    #                 "deliveries": [
    #                     {
    #                         "arrival_location": {
    #                             "latitude": 30.6983149,
    #                             "longitude": 76.6561808
    #                         },
    #                         # "duration": "600s",
    #                         "time_windows": [
    #                             {
    #                                 "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #                                 "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "load_demands": {
    #                     "weight": {
    #                         "amount": "100"
    #                     }
    #                 },
    #                 "label": "sas_wala"
    #             },
    #             {
    #                 "deliveries": [
    #                     {
    #                         "arrival_location": {
    #                             "latitude": 31.6335177,
    #                             "longitude": 74.7877192
    #                         },
    #                         # "duration": "600s",
    #                         "time_windows": [
    #                             {
    #                                 "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #                                 "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "load_demands": {
    #                     "weight": {
    #                         "amount": "100"
    #                     }
    #                 },
    #                 "label": "amrit_wala"
    #             },
    #             {
    #                 "deliveries": [
    #                     {
    #                         "arrival_location": {
    #                             "latitude": 26.8839819,
    #                             "longitude": 75.1996884
    #                         },
    #                         # "duration": "600s",
    #                         "time_windows": [
    #                             {
    #                                 "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #                                 "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "load_demands": {
    #                     "weight": {
    #                         "amount": "200"
    #                     }
    #                 },
    #                 "label": "jp_wala"
    #             },
    #             {
    #                 "deliveries": [
    #                     {
    #                         "arrival_location": {
    #                             "latitude": 31.4707267,
    #                             "longitude": 76.2482434
    #                         },
    #                         # "duration": "600s",
    #                         "time_windows": [
    #                             {
    #                                 "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #                                 "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "load_demands": {
    #                     "weight": {
    #                         "amount": "150"
    #                     }
    #                 },
    #                 "label": "una_wala"
    #             },
    #             {
    #                 "deliveries": [
    #                     {
    #                         "arrival_location": {
    #                             "latitude": 30.7322544,
    #                             "longitude": 76.6883125
    #                         },
    #                         # "duration": "600s",
    #                         "time_windows": [
    #                             {
    #                                 "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #                                 "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "load_demands": {
    #                     "weight": {
    #                         "amount": "50"
    #                     }
    #                 },
    #                 "label": "chd_wala"
    #             },
    #             # Add other shipments as in the original data
    #         ],
    #         "vehicles": [
    #             {
    #                 "start_location": {
    #                     "latitude": 28.6440836,
    #                     "longitude": 77.0932313
    #                 },
    #                 "load_limits": {
    #                     "weight": {
    #                         "max_load": 200
    #                     }
    #                 },
    #                 "start_time_windows": [
    #                     {
    #                         "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "end_time_windows": [
    #                     {
    #                         "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "label": "A_Truck",
    #                 "cost_per_kilometer": 1
    #             },
    #             {
    #                 "start_location": {
    #                     "latitude": 28.6440836,
    #                     "longitude": 77.0932313
    #                 },
    #                 "load_limits": {
    #                     "weight": {
    #                         "max_load": 150
    #                     }
    #                 },
    #                 "start_time_windows": [
    #                     {
    #                         "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "end_time_windows": [
    #                     {
    #                         "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "label": "B_Truck",
    #                 "cost_per_kilometer": 1
    #             },
    #             {
    #                 "start_location": {
    #                     "latitude": 28.6440836,
    #                     "longitude": 77.0932313
    #                 },
    #                 "load_limits": {
    #                     "weight": {
    #                         "max_load": 50
    #                     }
    #                 },
    #                 "start_time_windows": [
    #                     {
    #                         "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "end_time_windows": [
    #                     {
    #                         "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "label": "C_Truck",
    #                 "cost_per_kilometer": 1
    #             },
    #             {
    #                 "start_location": {
    #                     "latitude": 28.6440836,
    #                     "longitude": 77.0932313
    #                 },
    #                 "load_limits": {
    #                     "weight": {
    #                         "max_load": 300
    #                     }
    #                 },
    #                 "start_time_windows": [
    #                     {
    #                         "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "end_time_windows": [
    #                     {
    #                         "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #                     }
    #                 ],
    #                 "label": "D_Truck",
    #                 "cost_per_kilometer": 1
    #             },
    #         ],
    #         "global_start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
    #         "global_end_time": datetime.datetime.strptime("2024-10-06T06:59:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    #     }
    # "populatePolylines": True
    # }

    # GMPRO API trial
    # def index(request):
    #     # Set up the API URL and headers
    #     # project_id="gmprotrial"
    #     project_id="gmprotrial"
    #     # get_access_token()
    #     at = settings.GOOGLEMAPSKEY
    #     url = f'https://routeoptimization.googleapis.com/v1/{project_id}'
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': f'Bearer {at}'
    #     }
    #     # Request payload
        # data = {
        #     "model": {
        #         "shipments": [
        #             {
        #                 "deliveries": [
        #                     {
        #                         "arrivalLocation": {
        #                             "latitude": 30.6983149,
        #                             "longitude": 76.6561808
        #                         },
        #                         "duration": "600s",
        #                         "timeWindows": [
        #                             {
        #                                 "startTime": "2024-10-05T09:00:00Z",
        #                                 "endTime": "2024-10-05T23:00:00Z"
        #                             }
        #                         ]
        #                     }
        #                 ],
        #                 "loadDemands": {
        #                     "weight": {
        #                         "amount": "100"
        #                     }
        #                 },
        #                 "label": "sas_wala"
        #             },
        #             {
        #                 "deliveries": [
        #                     {
        #                         "arrivalLocation": {
        #                             "latitude": 31.6335177,
        #                             "longitude": 74.7877192
        #                         },
        #                         "duration": "600s",
        #                         "timeWindows": [
        #                             {
        #                                 "startTime": "2024-10-05T09:00:00Z",
        #                                 "endTime": "2024-10-05T23:00:00Z"
        #                             }
        #                         ]
        #                     }
        #                 ],
        #                 "loadDemands": {
        #                     "weight": {
        #                         "amount": "100"
        #                     }
        #                 },
        #                 "label": "amrit_wala"
        #             },
        #             {
        #                 "deliveries": [
        #                     {
        #                         "arrivalLocation": {
        #                             "latitude": 26.8839819,
        #                             "longitude": 75.1996884
        #                         },
        #                         "duration": "600s",
        #                         "timeWindows": [
        #                             {
        #                                 "startTime": "2024-10-05T09:00:00Z",
        #                                 "endTime": "2024-10-05T23:00:00Z"
        #                             }
        #                         ]
        #                     }
        #                 ],
        #                 "loadDemands": {
        #                     "weight": {
        #                         "amount": "200"
        #                     }
        #                 },
        #                 "label": "jp_wala"
        #             },
        #             {
        #                 "deliveries": [
        #                     {
        #                         "arrivalLocation": {
        #                             "latitude": 31.4707267,
        #                             "longitude": 76.2482434
        #                         },
        #                         "duration": "600s",
        #                         "timeWindows": [
        #                             {
        #                                 "startTime": "2024-10-05T09:00:00Z",
        #                                 "endTime": "2024-10-05T23:00:00Z"
        #                             }
        #                         ]
        #                     }
        #                 ],
        #                 "loadDemands": {
        #                     "weight": {
        #                         "amount": "150"
        #                     }
        #                 },
        #                 "label": "una_wala"
        #             },
        #             {
        #                 "deliveries": [
        #                     {
        #                         "arrivalLocation": {
        #                             "latitude": 30.7322544,
        #                             "longitude": 76.6883125
        #                         },
        #                         "duration": "600s",
        #                         "timeWindows": [
        #                             {
        #                                 "startTime": "2024-10-05T09:00:00Z",
        #                                 "endTime": "2024-10-05T23:00:00Z"
        #                             }
        #                         ]
        #                     }
        #                 ],
        #                 "loadDemands": {
        #                     "weight": {
        #                         "amount": "50"
        #                     }
        #                 },
        #                 "label": "chd_wala"
        #             },
        #             # Add other shipments as in the original data
        #         ],
        #         "vehicles": [
        #             {
        #                 "startLocation": {
        #                     "latitude": 28.6440836,
        #                     "longitude": 77.0932313
        #                 },
        #                 "loadLimits": {
        #                     "weight": {
        #                         "maxLoad": 200
        #                     }
        #                 },
        #                 "startTimeWindows": [
        #                     {
        #                         "startTime": "2024-10-05T09:00:00Z"
        #                     }
        #                 ],
        #                 "endTimeWindows": [
        #                     {
        #                         "endTime": "2024-10-05T23:00:00Z"
        #                     }
        #                 ],
        #                 "label": "A_Truck",
        #                 "costPerKilometer": 1
        #             },
        #             {
        #                 "startLocation": {
        #                     "latitude": 28.6440836,
        #                     "longitude": 77.0932313
        #                 },
        #                 "loadLimits": {
        #                     "weight": {
        #                         "maxLoad": 150
        #                     }
        #                 },
        #                 "startTimeWindows": [
        #                     {
        #                         "startTime": "2024-10-05T09:00:00Z"
        #                     }
        #                 ],
        #                 "endTimeWindows": [
        #                     {
        #                         "endTime": "2024-10-05T23:00:00Z"
        #                     }
        #                 ],
        #                 "label": "B_Truck",
        #                 "costPerKilometer": 1
        #             },
        #             {
        #                 "startLocation": {
        #                     "latitude": 28.6440836,
        #                     "longitude": 77.0932313
        #                 },
        #                 "loadLimits": {
        #                     "weight": {
        #                         "maxLoad": 50
        #                     }
        #                 },
        #                 "startTimeWindows": [
        #                     {
        #                         "startTime": "2024-10-05T09:00:00Z"
        #                     }
        #                 ],
        #                 "endTimeWindows": [
        #                     {
        #                         "endTime": "2024-10-05T23:00:00Z"
        #                     }
        #                 ],
        #                 "label": "C_Truck",
        #                 "costPerKilometer": 1
        #             },
        #             {
        #                 "startLocation": {
        #                     "latitude": 28.6440836,
        #                     "longitude": 77.0932313
        #                 },
        #                 "loadLimits": {
        #                     "weight": {
        #                         "maxLoad": 300
        #                     }
        #                 },
        #                 "startTimeWindows": [
        #                     {
        #                         "startTime": "2024-10-05T09:00:00Z"
        #                     }
        #                 ],
        #                 "endTimeWindows": [
        #                     {
        #                         "endTime": "2024-10-05T23:00:00Z"
        #                     }
        #                 ],
        #                 "label": "D_Truck",
        #                 "costPerKilometer": 1
        #             },
        #         ],
        #         "globalStartTime": "2024-10-05T09:00:00Z",
        #         "globalEndTime": "2024-10-06T06:59:00Z"
        #     },
        #     "populatePolylines": True
        # }

    #     # Send the POST request
    #     response = requests.post(url, headers=headers, json=data)

    #     # Output the response
    #     print(response.status_code)
    #     print(response.json())
    #     return HttpResponse('Done')

    # practised with gemma model
    # def index(request):
    #     # Encode the input question
    #     # login("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")
    #     # model_name = "microsoft/Phi-3.5-mini-instruct"  # Replace with the actual model name from Hugging Face
    #     model_name = "google/gemma-2-2b-it"  # Replace with the actual model name from Hugging Face
    #     a = datetime.datetime.now()
    #     print("level1", model_name, datetime.datetime.now())
    #     model = AutoModelForCausalLM.from_pretrained(model_name)
    #     print("level2")
    #     tokenizer = AutoTokenizer.from_pretrained(model_name)
    #     print("level3")


    #     input_question = """I have three trucks named A, B, and C, and I have three orders for Noida (50 bottles), Delhi (50 bottles), and Jammu (50 bottles). Truck A has a capacity to load 100 bottles, Truck B has a capacity to load 1,000 bottles, and Truck C has a capacity to load 50 bottles. Please explain what my delivery route will be for these orders starting from Chandigarh, which truck should go where, and how many trucks to send at the same time."""  # Replace with your question
    #     inputs = tokenizer(input_question, return_tensors="pt")
    #     print("level4", input_question)
    #     # Generate the model's response
    #     output = model.generate(**inputs, num_return_sequences=1, max_length=150)
    #     print("level5", output)
    #     # Decode and print the response
    #     response = tokenizer.decode(output[0], skip_special_tokens=True)
    #     print("level6")
    #     print(response)
    #     print("timed______________", datetime.datetime.now() - a)
    #     return HttpResponse(response)

    # def transform(request):
    #     # Load the model and tokenizer
    #     model_name = "gemma-model-name"  # Replace with the actual model name from Hugging Face
    #     model = AutoModelForCausalLM.from_pretrained(model_name)
    #     tokenizer = AutoTokenizer.from_pretrained(model_name)
    #     return HttpResponse('Done')
    pass