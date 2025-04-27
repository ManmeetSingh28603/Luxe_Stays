from django.shortcuts import render, redirect
from django.http import JsonResponse
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

        ContactSubmission.objects.create(
            name=name,
            email=email,
            message=message
        )

        subject = f"New Contact Form Submission from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            email,  # From user's email
            [os.getenv("EMAIL_HOST_USER")],  # Your email from .env
            fail_silently=False,
        )

        # Optional: success message
        # messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
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