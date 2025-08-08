"""
WSGI config for luxestays_project project - Vercel Deployment Version.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use Vercel-specific settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxestays_project.settings_vercel')

application = get_wsgi_application() 