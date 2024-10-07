from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, FileResponse
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer
from google.maps import routeoptimization_v1 as ro
from geopy.geocoders import Nominatim, GoogleV3
from google.protobuf.json_format import MessageToDict, MessageToJson
from django.core.files.base import ContentFile
import datetime, requests, json, subprocess
from home.models import Order, Truck
from .models import GenRoutes

# Get the access token
# def get_access_token():
#     result = subprocess.run(
#         ['gcloud', 'auth', 'application-default', 'print-access-token'], 
#         stdout=subprocess.PIPE
#     )
#     return result.stdout.decode('utf-8').strip()


def get_lat_long(location_name):
    geolocator = GoogleV3(api_key=settings.GOOGLEMAPSKEY)
    # geolocator = Nominatim(user_agent="geoapiExercises12")
    location = geolocator.geocode(location_name)
    if location:

        latitude = location.latitude
        longitude = location.longitude
        print(f'{latitude}, {longitude}')
        return {"latitude": latitude,"longitude": longitude}
    else:
        print(f"\n\n__________location not found for {location_name}\n\n")
        return None

def download_json(request, route_id):
    gen_route = GenRoutes.objects.get(id=route_id)
    response = FileResponse(gen_route.ijson, as_attachment=True, filename='request.json')
    return response

# GMPRO DOCUMENTATION API hit trial
def getroute(request):
    # if request.method == 'POST':
    #     print("welcome ji")
    #     return redirect('home')  # Redirect to home or any other page
    
    





    reqjson = {"shipments": [], "vehicles": [], "global_start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"), "global_end_time": datetime.datetime.strptime("2024-10-06T06:59:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")}

    # a, b = get_lat_long('una, hp')
    # return HttpResponse(f'{a}, {b}')

    for i in Truck.objects.filter(available=True):
        temp = {}
        temp["start_location"] = {"latitude": settings.FROMLATITUDE,"longitude": settings.FROMLONGITUDE}
        temp["load_limits"] = {"weight": {"max_load": i.capacity}}
        temp["start_time_windows"] = [{"start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")}]
        temp["end_time_windows"] = [{"end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")}]
        temp["label"] = f'{i.truck_name}--{i.truck_number}--{i.driver_name}'
        temp["cost_per_kilometer"] = int(i.cost_per_km)
        reqjson["vehicles"].append(temp)    


    for i in Order.objects.filter(order_status='pending'):
        temp = {}
        temp['deliveries'] = [{
                "arrival_location": get_lat_long(i.destination),
                "time_windows": [{
                    "start_time": datetime.datetime.strptime("2024-10-05T09:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "end_time": datetime.datetime.strptime("2024-10-05T23:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
                }]
            }]
        temp["load_demands"] = {"weight": {"amount": i.quantity}}
        temp["label"] = f'{i.destination}_{i.id}'
        reqjson["shipments"].append(temp) 

    print("reqjson______", reqjson)


    newreqjson = reqjson

    # newreqjson['global_start_time'] = newreqjson['global_start_time'].isoformat()
    # newreqjson['global_end_tim'] = newreqjson['global_end_time'].isoformat()
    del newreqjson['global_start_time']
    del newreqjson['global_end_time']
    for i in newreqjson['vehicles']:
        # del i['start_time_windows']
        # del i['end_time_windows']
        del i['start_time_windows'][0]['start_time']
        del i['end_time_windows'][0]['end_time']
    for i in newreqjson['shipments']:
        # del i['start_time_windows']
        # del i['end_time_windows']  
        del i['deliveries'][0]['time_windows'][0]['start_time']
        del i['deliveries'][0]['time_windows'][0]['end_time']

    print("ooops", reqjson)
    print("ooops",  newreqjson)

    json_file = ContentFile(json.dumps({"model": newreqjson, "populatePolylines": True}).encode('utf-8'), name='request.json')
    gen_route = GenRoutes.objects.create(ijson=json_file)
    
    project_id="gmprotrial"
    client = ro.RouteOptimizationClient()
    grequest = ro.OptimizeToursRequest(
        parent=f'projects/{project_id}',
        model=reqjson,
        # populate_polylines=True

    )
    response = client.optimize_tours(request=grequest)

    # json_output = MessageToJson(response._pb) ## RESPONSE JSON
    dict_output = MessageToDict(response._pb)

    iroutes = []
    for data in dict_output['routes']:
        temp = {
        'truck'     : Truck.objects.get(truck_number=data['vehicleLabel'].split('--')[1]),
        'order'     : [ Order.objects.get(id=i['shipmentLabel'].split('_')[1]) for i in data.get('visits', [])],
        'fstop'     : None,
        'lstop'     : None,
        'stime'     :data.get('vehicleStartTime', None) 
        }
        if data.get('visits', []): 
            i = Order.objects.get(id=data.get('visits', [])[-1]['shipmentLabel'].split('_')[1])
            temp['fstop'], temp['lstop'] = i.from_location, i.destination
            
        iroutes.append(temp)

    print("iroute______________s", iroutes)
    # return HttpResponse(json_output['routes'])
    context={'iroutes':iroutes, 'gen_route_id' : gen_route.id}
    return render(request, 'home/ai-routes.html',context)
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

def transform(request):
    # Load the model and tokenizer
    model_name = "gemma-model-name"  # Replace with the actual model name from Hugging Face
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return HttpResponse('Done')