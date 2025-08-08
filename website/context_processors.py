"""
Context processors for Luxe Stays India project.
Provides global context data to all templates.
"""

from django.conf import settings
from django.core.cache import cache
from .models import SiteSettings


def site_settings(request):
    """
    Add site settings to template context.
    """
    try:
        # Get site settings from cache or database
        site_settings = cache.get('site_settings')
        if site_settings is None:
            site_settings = SiteSettings.get_settings()
            cache.set('site_settings', site_settings, 60 * 60)  # Cache for 1 hour
        
        return {
            'site_settings': site_settings,
            'site_name': getattr(settings, 'SITE_NAME', 'Luxe Stays India'),
            'site_description': getattr(settings, 'SITE_DESCRIPTION', ''),
        }
    except Exception:
        # Fallback if site settings don't exist
        return {
            'site_settings': None,
            'site_name': getattr(settings, 'SITE_NAME', 'Luxe Stays India'),
            'site_description': getattr(settings, 'SITE_DESCRIPTION', ''),
        }


def analytics(request):
    """
    Add analytics configuration to template context.
    """
    return {
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'facebook_pixel_id': getattr(settings, 'FACEBOOK_PIXEL_ID', ''),
        'instagram_username': getattr(settings, 'INSTAGRAM_USERNAME', 'luxestaysindia'),
    }


def maintenance_mode(request):
    """
    Add maintenance mode status to template context.
    """
    return {
        'maintenance_mode': getattr(settings, 'MAINTENANCE_MODE', False),
        'maintenance_message': getattr(settings, 'MAINTENANCE_MESSAGE', ''),
    }


def debug_info(request):
    """
    Add debug information to template context (only in debug mode).
    """
    if settings.DEBUG:
        return {
            'debug': True,
            'request_path': request.path,
            'request_method': request.method,
        }
    return {'debug': False} 