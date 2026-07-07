import requests
from textwrap import dedent
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_city_coordinates(city_name):
    # Initialize Nominatim API with a descriptive user agent string
    geolocator = Nominatim(user_agent="my_city_locator_application")
    
    try:
        # Geocode the city name to fetch location details
        location = geolocator.geocode(city_name)
        
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            return "City not found."
            
    except GeocoderTimedOut:
        return "The service timed out. Please try again."

def add(a,b):
    print(f"Running add({a}, {b})")
    return a + b

def search_notes(notes, phrase):
    results = [note for note in notes if phrase.lower() in note.lower()]
    return results

def get_weather(city):
    coordinates = get_city_coordinates(city)
    #print(f"coordinates: {coordinates}")
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
        "timezone": "auto",
        "forecast_days": 1
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")

tools = [
    {
        "type": "function",
        "name": "add",
        "description": "Add two numbers a and b and return the sum.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get weather at the city specified.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    },
    {
        "type": "function",
        "name": "search_notes",
        "description": "Search notes for a specific phrase.",
        "parameters": {
            "type": "object",
            "properties": {
                "phrase": {"type": "string"}
            },
            "required": ["phrase"]
        }
    }
]

# This is chat.completions api

# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "add",
#             "description": "Add two numbers a and b and return the sum.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "a": {"type": "number"},
#                     "b": {"type": "number"}
#                 },
#                 "required": ["a", "b"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_weather",
#             "description": "Get weather at the city specified.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "city": {"type": "string"},
#                 },
#                 "required": ["city"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "search_notes",
#             "description": "Search notes for a specific phrase.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "phrase": {"type": "string"},
#                 },
#                 "required": ["phrase"]
#             }
#         }
#     }
# ]