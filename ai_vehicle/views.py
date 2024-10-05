from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer
from google.maps import routeoptimization_v1 as ro
from geopy.geocoders import Nominatim, GoogleV3
import datetime, requests, json, subprocess
from home.models import Order, Truck

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

# GMPRO DOCUMENTATION API hit trial
def getroute(request):
    reqjson = {"shipments": [], "vehicles": [], "global_start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"), "global_end_time": datetime.datetime.fromisoformat("2024-10-06T06:59:00.000Z")}

    # a, b = get_lat_long('una, hp')
    # return HttpResponse(f'{a}, {b}')

    for i in Truck.objects.filter(available=True):
        temp = {}
        temp["start_location"] = {"latitude": settings.FROMLATITUDE,"longitude": settings.FROMLONGITUDE}
        temp["load_limits"] = {"weight": {"max_load": i.capacity}}
        temp["start_time_windows"] = [{"start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z")}]
        temp["end_time_windows"] = [{"end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")}]
        temp["label"] = f'{i.truck_name}--{i.truck_number}--{i.driver_name}'
        temp["cost_per_kilometer"] = int(i.cost_per_km)
        reqjson["vehicles"].append(temp)    


    for i in Order.objects.filter(order_status='pending'):
        temp = {}
        temp['deliveries'] = [{
                "arrival_location": get_lat_long(i.destination),
                "time_windows": [{
                    "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
                    "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
                }]
            }]
        temp["load_demands"] = {"weight": {"amount": i.quantity}}
        temp["label"] = f'{i.destination}_{i.id}'
        reqjson["shipments"].append(temp) 

    print("reqjson______", reqjson)
    # return HttpResponse(str(reqjson))

    project_id="gmprotrial"
    client = ro.RouteOptimizationClient()
    request = ro.OptimizeToursRequest(
        parent=f'projects/{project_id}',
        model=reqjson,
        # populate_polylines=True

    )
    response = client.batch_optimize_tours(request=request)
    print("response________", response)
    return HttpResponse(response)

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
#                                 "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#                                 "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                                 "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#                                 "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                                 "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#                                 "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                                 "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#                                 "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                                 "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#                                 "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                         "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z")
#                     }
#                 ],
#                 "end_time_windows": [
#                     {
#                         "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                         "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z")
#                     }
#                 ],
#                 "end_time_windows": [
#                     {
#                         "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                         "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z")
#                     }
#                 ],
#                 "end_time_windows": [
#                     {
#                         "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
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
#                         "start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z")
#                     }
#                 ],
#                 "end_time_windows": [
#                     {
#                         "end_time": datetime.datetime.fromisoformat("2024-10-05T23:00:00.000Z")
#                     }
#                 ],
#                 "label": "D_Truck",
#                 "cost_per_kilometer": 1
#             },
#         ],
#         "global_start_time": datetime.datetime.fromisoformat("2024-10-05T09:00:00.000Z"),
#         "global_end_time": datetime.datetime.fromisoformat("2024-10-06T06:59:00.000Z")
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