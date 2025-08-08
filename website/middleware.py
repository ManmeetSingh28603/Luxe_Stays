"""
Custom middleware for Luxe Stays India project.
Handles analytics, security, and performance monitoring.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings
from .models import PageView

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to track page views and user analytics.
    """
    
    def process_request(self, request):
        """Track request start time"""
        request.start_time = time.time()
        
        # Skip tracking for admin, static files, and API endpoints
        if any(path in request.path for path in ['/admin/', '/static/', '/media/', '/api/']):
            return None
        
        return None
    
    def process_response(self, request, response):
        """Track page views and response time"""
        # Skip tracking for admin, static files, and API endpoints
        if any(path in request.path for path in ['/admin/', '/static/', '/media/', '/api/']):
            return response
        
        # Calculate response time
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            response['X-Response-Time'] = f'{response_time:.3f}s'
        
        # Track page view (only for successful responses)
        if response.status_code == 200 and request.method == 'GET':
            try:
                # Determine page name
                page_name = self.get_page_name(request.path)
                
                # Track page view asynchronously (in production, use Celery)
                PageView.track_view(request, page_name)
                
            except Exception as e:
                logger.error(f"Error tracking page view: {str(e)}")
        
        return response
    
    def get_page_name(self, path):
        """Get human-readable page name from path"""
        page_mapping = {
            '/': 'Home',
            '/services/': 'Services',
            '/about/': 'About',
            '/contact/': 'Contact',
            '/thank-you/': 'Thank You',
        }
        
        return page_mapping.get(path, path.strip('/').title())


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers and handle security-related tasks.
    """
    
    def process_response(self, request, response):
        """Add security headers"""
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self' https://instagram120.p.rapidapi.com; "
            "frame-src 'none'; "
            "object-src 'none';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response


class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and optimize performance.
    """
    
    def process_request(self, request):
        """Start performance monitoring"""
        request.performance_start = time.time()
        return None
    
    def process_response(self, request, response):
        """Monitor response performance"""
        if hasattr(request, 'performance_start'):
            duration = time.time() - request.performance_start
            
            # Log slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow request: {request.path} took {duration:.3f}s "
                    f"(IP: {self.get_client_ip(request)})"
                )
            
            # Add performance headers
            response['X-Request-Duration'] = f'{duration:.3f}s'
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceMiddleware(MiddlewareMixin):
    """
    Middleware to handle maintenance mode.
    """
    
    def process_request(self, request):
        """Check if site is in maintenance mode"""
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access during maintenance
            if request.path.startswith('/admin/'):
                return None
            
            # Return maintenance page
            maintenance_message = getattr(settings, 'MAINTENANCE_MESSAGE', 
                                        'Site is under maintenance. Please check back soon.')
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Site Maintenance - Luxe Stays India</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: #F5EFE6; 
                        color: #C17C5E; 
                    }}
                    .container {{ 
                        max-width: 600px; 
                        margin: 0 auto; 
                        background: white; 
                        padding: 40px; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                    }}
                    h1 {{ color: #C17C5E; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛠️ Site Maintenance</h1>
                    <p>{maintenance_message}</p>
                    <p>We'll be back soon!</p>
                </div>
            </body>
            </html>
            """
            
            return HttpResponse(html, status=503)
        
        return None


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle errors gracefully.
    """
    
    def process_exception(self, request, exception):
        """Handle exceptions gracefully"""
        logger.error(
            f"Exception in {request.path}: {str(exception)} "
            f"(IP: {self.get_client_ip(request)})"
        )
        
        # Return a user-friendly error page
        if not settings.DEBUG:
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error - Luxe Stays India</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: #F5EFE6; 
                        color: #C17C5E; 
                    }
                    .container { 
                        max-width: 600px; 
                        margin: 0 auto; 
                        background: white; 
                        padding: 40px; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                    }
                    h1 { color: #C17C5E; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>😔 Something went wrong</h1>
                    <p>We're sorry, but something went wrong. Please try again later.</p>
                    <p><a href="/" style="color: #C17C5E;">Return to Home</a></p>
                </div>
            </body>
            </html>
            """
            
            return HttpResponse(html, status=500)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 