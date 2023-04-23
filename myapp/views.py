from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import os

from dotenv import load_dotenv

load_dotenv()

def map_view(request):
    return render(request, 'map.html')

def geojson(request):
    with open(os.getenv('DATA'), encoding='UTF-8') as file:
        geojson_data = json.load(file)

    return JsonResponse(geojson_data)

def home(request):
    return redirect(map_view)

def handler_404(request, exception):
    return redirect(map_view)