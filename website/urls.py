# website/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Other pages (add these as needed)
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('get-followers/', views.get_instagram_followers, name='get_followers'),
    path('get-highlights/', views.get_instagram_highlights, name='get_highlights'),
    path('proxy-image/', views.proxy_image, name='proxy-image'),

]
