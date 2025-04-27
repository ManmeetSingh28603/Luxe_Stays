from django.shortcuts import render
from django.http import JsonResponse
import os
import requests

# Create your views here.
def home(request):
    return render(request, 'website/home.html')

# Services page view
def services(request):
    return render(request, 'website/services.html')

# About page view
def about(request):
    return render(request, 'website/about.html')

# Contact page view
def contact(request):
    return render(request, 'website/contact.html')

def get_instagram_followers(request):
    url = "https://instagram120.p.rapidapi.com/api/instagram/userInfo"

    payload = { "username": "luxestaysindia" }
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    # print("Full API Response:", data)  # for debugging

    try:
        followers_count = data["result"][0]["user"]["follower_count"]
    except (KeyError, IndexError, TypeError) as e:
        print("Error extracting followers count:", e)
        followers_count = 0

    print(f"Followers for luxestaysindia: {followers_count}")

    return JsonResponse({"followers": followers_count})