from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import os
import requests
from django.core.mail import send_mail
from django.contrib import messages
from .models import ContactSubmission

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
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save to DB
        ContactSubmission.objects.create(
            name=name,
            email=email,
            message=message
        )

        # Email to Admin (you)
        subject = f"New Contact Form Submission from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            email,  # from user's email
            [os.getenv("EMAIL_HOST_USER")],  # your admin email
            fail_silently=False,
        )
        
        # Email to User (confirmation)
        user_subject = "Thank you for contacting Luxe Stays India!"
        user_message = (
            f"Dear {name},\n\n"
            "Thank you for reaching out to Luxe Stays India! ✨\n"
            "We have received your message and will get back to you shortly.\n\n"
            "Warm regards,\n"
            "The Luxe Stays India Team"
        )

        send_mail(
            user_subject,
            user_message,
            os.getenv("EMAIL_HOST_USER"),  # from your admin email
            [email],  # to the user's email
            fail_silently=False,
        )
        return redirect('thank_you')

    return render(request, 'website/contact.html')


def thank_you(request):
    return render(request, 'website/thank_you.html')


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

    # print(f"Followers for luxestaysindia: {followers_count}")

    return JsonResponse({"followers": followers_count})

def get_instagram_highlights(request):
    url = "https://instagram120.p.rapidapi.com/api/instagram/highlights"

    payload = {"username": "luxestaysindia"}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    try:
        highlights = []
        for item in data.get("result", []):    # <-- result is a LIST directly
            title = item.get("title", "Unnamed Highlight")
            if title.lower() != "about us":    # skip "About Us" highlight
                highlights.append({
                    "name": title,
                    "image_url": item.get("cover_media", {}).get("cropped_image_version", {}).get("url", "")
                })
    except (KeyError, TypeError, IndexError) as e:
        highlights = []

    return JsonResponse({"highlights": highlights})


from django.http import JsonResponse, HttpResponse
import base64

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse(status=400)

    try:
        resp = requests.get(image_url, stream=True, timeout=5)
        resp.raise_for_status()  # Properly raise exceptions if failed
        return HttpResponse(resp.content, content_type=resp.headers.get('Content-Type', 'image/jpeg'))
    except requests.exceptions.RequestException:
        # Instead of crashing, quietly return a 1x1 transparent GIF
        pixel_base64 = (
            'R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=='  # Transparent pixel
        )
        pixel = base64.b64decode(pixel_base64)
        return HttpResponse(pixel, content_type='image/gif')
