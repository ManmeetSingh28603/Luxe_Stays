import os
import random
import base64
import requests
import pandas as pd

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from .models import ContactSubmission
from django.core.cache import cache

# Fetch Excel Data
from .models import ExcelData

def read_excel_data():
    latest_excel = ExcelData.objects.last()
    if latest_excel:
        df = pd.read_excel(latest_excel.file.path)
        return df.to_dict(orient='records')
    return []


# -------------------------------
# Basic Page Views
# -------------------------------

def home(request):
    return render(request, 'website/home.html')


def about(request):
    return render(request, 'website/about.html')


def thank_you(request):
    return render(request, 'website/thank_you.html')


# -------------------------------
# Services Page - Load Properties from Excel
# -------------------------------

from .models import ExcelData

def services(request):
    try:
        # Use latest uploaded Excel file
        latest_excel = ExcelData.objects.last()
        if latest_excel:
            df = pd.read_excel(latest_excel.file.path)

            df = df.rename(columns={
                'Property Name ': 'name',
                'Location': 'location',
                'Instagram Reel Link 1': 'reel_url',
                'Direct Website Link ': 'website_url',
            })

            df = df[['name', 'location', 'reel_url', 'website_url']].dropna()
            properties = df.sample(n=min(9, len(df))).to_dict(orient='records')
        else:
            print("⚠️ No Excel file uploaded in admin.")
            properties = []

    except Exception as e:
        print("❌ Error loading Excel from model:", e)
        properties = []

    return render(request, 'website/services.html', {
        'properties': properties
    })



# -------------------------------
# Contact Page - Form Handling
# -------------------------------

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save to DB
        ContactSubmission.objects.create(name=name, email=email, message=message)

        # Email to Admin
        subject = f"New Contact Form Submission from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                email,
                [os.getenv("EMAIL_HOST_USER")],
                fail_silently=False,
            )
        except Exception as e:
            print("Error sending admin email:", e)

        # Confirmation email to user
        user_subject = "Thank you for contacting Luxe Stays India!"
        user_message = (
            f"Dear {name},\n\n"
            "Thank you for reaching out to Luxe Stays India! ✨\n"
            "We have received your message and will get back to you shortly.\n\n"
            "Warm regards,\n"
            "The Luxe Stays India Team"
        )

        try:
            send_mail(
                user_subject,
                user_message,
                os.getenv("EMAIL_HOST_USER"),
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print("Error sending user confirmation email:", e)

        return redirect('thank_you')

    return render(request, 'website/contact.html')


# -------------------------------
# Instagram API Views (via RapidAPI)
# -------------------------------

def get_instagram_followers(request):
    cached_followers = cache.get('instagram_followers_count')

    if cached_followers is not None:
        print("✅ Using cached followers count.")
        return JsonResponse({"followers": cached_followers})

    print("📡 Fetching fresh followers count from API.")
    url = "https://instagram120.p.rapidapi.com/api/instagram/userInfo"
    payload = {"username": "luxestaysindia"}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        followers_count = data["result"][0]["user"]["follower_count"]

        cache.set('instagram_followers_count', followers_count, 60 * 60 * 24 * 5)  # Cache for 3 days
    except Exception as e:
        print("❌ Error extracting followers count:", e)
        followers_count = 0

    return JsonResponse({"followers": followers_count})


def get_instagram_highlights(request):
    cached_highlights = cache.get('instagram_highlights')

    if cached_highlights is not None:
        print("✅ Using cached Instagram highlights.")
        return JsonResponse({"highlights": cached_highlights})

    print("📡 Fetching fresh highlights from API.")
    url = "https://instagram120.p.rapidapi.com/api/instagram/highlights"
    payload = {"username": "luxestaysindia"}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        highlights = []
        for item in data.get("result", []):
            title = item.get("title", "Unnamed Highlight")
            if title.lower() != "about us":
                highlights.append({
                    "name": title,
                    "image_url": item.get("cover_media", {}).get("cropped_image_version", {}).get("url", "")
                })

        cache.set('instagram_highlights', highlights, 60 * 60 * 24 * 5)  # Cache for 3 days
    except Exception as e:
        print("❌ Error fetching highlights:", e)
        highlights = []

    return JsonResponse({"highlights": highlights})


def get_instagram_reels(request):
    url = "https://instagram120.p.rapidapi.com/api/instagram/posts"
    payload = {"username": "luxestaysindia"}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        videos = []
        for edge in data.get("result", {}).get("edges", []):
            node = edge.get("node", {})
            video_versions = node.get("video_versions")
            if video_versions:
                video_url = video_versions[0].get("url")
                if video_url:
                    videos.append(video_url)

        random.shuffle(videos)
        return JsonResponse({"videos": videos[:10]})

    except Exception as e:
        print("❌ Error parsing reels:", e)
        return JsonResponse({"videos": []})



# -------------------------------
# Image Proxy - Prevent Hotlink Errors
# -------------------------------

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse(status=400)

    try:
        resp = requests.get(image_url, stream=True, timeout=5)
        resp.raise_for_status()
        return HttpResponse(resp.content, content_type=resp.headers.get('Content-Type', 'image/jpeg'))
    except requests.exceptions.RequestException:
        # Return a transparent 1x1 GIF as fallback
        pixel_base64 = 'R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=='
        pixel = base64.b64decode(pixel_base64)
        return HttpResponse(pixel, content_type='image/gif')
