import os
import random
import base64
import logging
import requests
import pandas as pd
from functools import wraps
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.core.mail import send_mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import ContactSubmission, ExcelData

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CACHE_TIMEOUT = 60 * 60 * 24 * 5  # 5 days
EXCEL_CACHE_KEY = 'excel_properties_data'
INSTAGRAM_CACHE_KEY = 'instagram_followers_count'
HIGHLIGHTS_CACHE_KEY = 'instagram_highlights'
REELS_CACHE_KEY = 'instagram_reels'
MAX_PROPERTIES_DISPLAY = 9
REQUEST_TIMEOUT = 10

def handle_exceptions(func):
    """Decorator to handle exceptions gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return JsonResponse({'error': 'An error occurred'}, status=500)
    return wrapper

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    import html
    return html.escape(text.strip())

@handle_exceptions
def read_excel_data() -> List[Dict[str, Any]]:
    """Read and cache Excel data with error handling"""
    cached_data = cache.get(EXCEL_CACHE_KEY)
    if cached_data:
        logger.info("Using cached Excel data")
        return cached_data

    try:
        latest_excel = ExcelData.objects.select_related().last()
        if not latest_excel:
            logger.warning("No Excel file uploaded in admin")
            return []

        # Check if file exists
        if not os.path.exists(latest_excel.file.path):
            logger.error(f"Excel file not found: {latest_excel.file.path}")
            return []

        df = pd.read_excel(latest_excel.file.path)
        
        # Validate required columns
        required_columns = ['Property Name ', 'Location', 'Instagram Reel Link 1', 'Direct Website Link ']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return []

        # Clean and process data
        df = df.rename(columns={
            'Property Name ': 'name',
            'Location': 'location',
            'Instagram Reel Link 1': 'reel_url',
            'Direct Website Link ': 'website_url',
        })

        # Filter and clean data
        df = df[['name', 'location', 'reel_url', 'website_url']].dropna()
        df = df[df['name'].str.strip() != '']
        
        properties = df.to_dict(orient='records')
        
        # Cache the processed data
        cache.set(EXCEL_CACHE_KEY, properties, CACHE_TIMEOUT)
        logger.info(f"Successfully processed {len(properties)} properties from Excel")
        
        return properties

    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        return []

# -------------------------------
# Basic Page Views (Optimized)
# -------------------------------

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request: HttpRequest) -> HttpResponse:
    """Optimized home page with caching"""
    return render(request, 'website/home.html')

@cache_page(60 * 30)  # Cache for 30 minutes
def about(request: HttpRequest) -> HttpResponse:
    """Optimized about page with caching"""
    return render(request, 'website/about.html')

@cache_page(60 * 60)  # Cache for 1 hour
def thank_you(request: HttpRequest) -> HttpResponse:
    """Optimized thank you page with caching"""
    return render(request, 'website/thank_you.html')

# -------------------------------
# Services Page - Load Properties from Excel (Optimized)
# -------------------------------

@handle_exceptions
def services(request: HttpRequest) -> HttpResponse:
    """Optimized services page with better error handling and caching"""
    try:
        properties = read_excel_data()
        
        # Randomly sample properties for display
        if len(properties) > MAX_PROPERTIES_DISPLAY:
            properties = random.sample(properties, MAX_PROPERTIES_DISPLAY)
        
        context = {
            'properties': properties,
            'total_properties': len(properties)
        }
        
        return render(request, 'website/services.html', context)

    except Exception as e:
        logger.error(f"Error in services view: {str(e)}")
        return render(request, 'website/services.html', {
            'properties': [],
            'total_properties': 0,
            'error_message': 'Unable to load properties at this time.'
        })

# -------------------------------
# Contact Page - Form Handling (Optimized)
# -------------------------------

@require_http_methods(["GET", "POST"])
def contact(request: HttpRequest) -> HttpResponse:
    """Optimized contact form with validation and error handling"""
    if request.method == "POST":
        return handle_contact_submission(request)
    
    return render(request, 'website/contact.html')

@transaction.atomic
def handle_contact_submission(request: HttpRequest) -> HttpResponse:
    """Handle contact form submission with validation"""
    try:
        # Get and sanitize form data
        name = sanitize_input(request.POST.get('name', ''))
        email = sanitize_input(request.POST.get('email', ''))
        message = sanitize_input(request.POST.get('message', ''))

        # Validate inputs
        errors = []
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if not email or not validate_email(email):
            errors.append("Please enter a valid email address")
        
        if not message or len(message) < 10:
            errors.append("Message must be at least 10 characters long")

        if errors:
            return render(request, 'website/contact.html', {
                'errors': errors,
                'form_data': {'name': name, 'email': email, 'message': message}
            })

        # Save to database
        contact_submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            message=message
        )

        # Send emails asynchronously (in production, use Celery)
        send_contact_emails(name, email, message)

        logger.info(f"Contact form submitted by {name} ({email})")
        return redirect('thank_you')

    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        return render(request, 'website/contact.html', {
            'errors': ['An error occurred. Please try again later.']
        })

def send_contact_emails(name: str, email: str, message: str) -> None:
    """Send contact form emails with error handling"""
    try:
        # Email to Admin
        admin_subject = f"New Contact Form Submission from {name}"
        admin_message = f"""
Name: {name}
Email: {email}

Message:
{message}

Submitted at: {ContactSubmission.objects.last().submitted_at}
        """.strip()

        send_mail(
            admin_subject,
            admin_message,
            email,
            [os.getenv("EMAIL_HOST_USER")],
            fail_silently=False,
        )

        # Confirmation email to user
        user_subject = "Thank you for contacting Luxe Stays India!"
        user_message = f"""
Dear {name},

Thank you for reaching out to Luxe Stays India! ✨
We have received your message and will get back to you shortly.

Your message:
{message}

Warm regards,
The Luxe Stays India Team
        """.strip()

        send_mail(
            user_subject,
            user_message,
            os.getenv("EMAIL_HOST_USER"),
            [email],
            fail_silently=False,
        )

        logger.info(f"Contact emails sent successfully for {email}")

    except Exception as e:
        logger.error(f"Error sending contact emails: {str(e)}")

# -------------------------------
# Instagram API Views (Optimized)
# -------------------------------

@handle_exceptions
@csrf_exempt
def get_instagram_followers(request: HttpRequest) -> JsonResponse:
    """Optimized Instagram followers endpoint with better caching"""
    cached_followers = cache.get(INSTAGRAM_CACHE_KEY)
    
    if cached_followers is not None:
        logger.info("Using cached Instagram followers count")
        return JsonResponse({"followers": cached_followers})

    logger.info("Fetching fresh Instagram followers count from API")
    
    try:
        response = requests.post(
            "https://instagram120.p.rapidapi.com/api/instagram/userInfo",
            json={"username": "luxestaysindia"},
            headers={
                "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        data = response.json()
        
        followers_count = data.get("result", [{}])[0].get("user", {}).get("follower_count", 0)
        
        # Cache the result
        cache.set(INSTAGRAM_CACHE_KEY, followers_count, CACHE_TIMEOUT)
        
        logger.info(f"Successfully fetched Instagram followers: {followers_count}")
        return JsonResponse({"followers": followers_count})

    except requests.exceptions.RequestException as e:
        logger.error(f"Instagram API request failed: {str(e)}")
        return JsonResponse({"followers": 0, "error": "Unable to fetch followers"})

@handle_exceptions
@csrf_exempt
def get_instagram_highlights(request: HttpRequest) -> JsonResponse:
    """Optimized Instagram highlights endpoint"""
    cached_highlights = cache.get(HIGHLIGHTS_CACHE_KEY)
    
    if cached_highlights is not None:
        logger.info("Using cached Instagram highlights")
        return JsonResponse({"highlights": cached_highlights})

    logger.info("Fetching fresh Instagram highlights from API")
    
    try:
        response = requests.post(
            "https://instagram120.p.rapidapi.com/api/instagram/highlights",
            json={"username": "luxestaysindia"},
            headers={
                "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        data = response.json()

        highlights = []
        for item in data.get("result", []):
            title = item.get("title", "Unnamed Highlight")
            if title.lower() != "about us":
                cover_media = item.get("cover_media", {})
                image_url = cover_media.get("cropped_image_version", {}).get("url", "")
                
                highlights.append({
                    "name": title,
                    "image_url": image_url
                })

        # Cache the result
        cache.set(HIGHLIGHTS_CACHE_KEY, highlights, CACHE_TIMEOUT)
        
        logger.info(f"Successfully fetched {len(highlights)} Instagram highlights")
        return JsonResponse({"highlights": highlights})

    except requests.exceptions.RequestException as e:
        logger.error(f"Instagram highlights API request failed: {str(e)}")
        return JsonResponse({"highlights": [], "error": "Unable to fetch highlights"})

@handle_exceptions
@csrf_exempt
def get_instagram_reels(request: HttpRequest) -> JsonResponse:
    """Optimized Instagram reels endpoint"""
    cached_reels = cache.get(REELS_CACHE_KEY)
    
    if cached_reels is not None:
        logger.info("Using cached Instagram reels")
        return JsonResponse({"videos": cached_reels})

    logger.info("Fetching fresh Instagram reels from API")
    
    try:
        response = requests.post(
            "https://instagram120.p.rapidapi.com/api/instagram/posts",
            json={"username": "luxestaysindia"},
            headers={
                "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        data = response.json()

        videos = []
        for edge in data.get("result", {}).get("edges", []):
            node = edge.get("node", {})
            video_versions = node.get("video_versions")
            if video_versions:
                video_url = video_versions[0].get("url")
                if video_url:
                    videos.append(video_url)

        # Shuffle and limit videos
        random.shuffle(videos)
        videos = videos[:10]  # Limit to 10 videos
        
        # Cache the result
        cache.set(REELS_CACHE_KEY, videos, CACHE_TIMEOUT)
        
        logger.info(f"Successfully fetched {len(videos)} Instagram reels")
        return JsonResponse({"videos": videos})

    except requests.exceptions.RequestException as e:
        logger.error(f"Instagram reels API request failed: {str(e)}")
        return JsonResponse({"videos": [], "error": "Unable to fetch reels"})

# -------------------------------
# Image Proxy - Prevent Hotlink Errors (Optimized)
# -------------------------------

@handle_exceptions
def proxy_image(request: HttpRequest) -> HttpResponse:
    """Optimized image proxy with better error handling"""
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse(status=400)

    try:
        response = requests.get(
            image_url, 
            stream=True, 
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; LuxeStaysBot/1.0)'}
        )
        response.raise_for_status()
        
        return HttpResponse(
            response.content, 
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Image proxy failed for {image_url}: {str(e)}")
        # Return a transparent 1x1 GIF as fallback
        pixel_base64 = 'R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=='
        pixel = base64.b64decode(pixel_base64)
        return HttpResponse(pixel, content_type='image/gif') 