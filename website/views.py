from django.shortcuts import render

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