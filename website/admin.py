# Register your models here.
from django.contrib import admin
from .models import ContactSubmission

admin.site.register(ContactSubmission)

# admin.py
from .models import ExcelData

admin.site.register(ExcelData)
