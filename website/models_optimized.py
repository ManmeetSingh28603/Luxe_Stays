from django.db import models
from django.core.validators import EmailValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
import os

class ContactSubmission(models.Model):
    """Optimized contact submission model with validation and methods"""
    
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2, "Name must be at least 2 characters long")]
    )
    email = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address")]
    )
    message = models.TextField(
        validators=[MinLengthValidator(10, "Message must be at least 10 characters long")]
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        indexes = [
            models.Index(fields=['submitted_at']),
            models.Index(fields=['email']),
            models.Index(fields=['is_processed']),
        ]

    def __str__(self):
        return f"{self.name} - {self.email} ({self.submitted_at.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Check for spam (basic checks)
        if self.name and len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters long'})
        
        if self.message and len(self.message.strip()) < 10:
            raise ValidationError({'message': 'Message must be at least 10 characters long'})

    def mark_as_processed(self):
        """Mark submission as processed"""
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['is_processed', 'processed_at'])

    @property
    def is_recent(self):
        """Check if submission is from last 24 hours"""
        return (timezone.now() - self.submitted_at).days < 1

    @property
    def display_name(self):
        """Return formatted name"""
        return self.name.strip().title()

    def get_absolute_url(self):
        """Get admin URL for this object"""
        from django.urls import reverse
        return reverse('admin:website_contactsubmission_change', args=[str(self.id)])


class ExcelData(models.Model):
    """Optimized Excel data model with file validation and processing"""
    
    file = models.FileField(
        upload_to='excel_files/',
        help_text="Upload Excel file with property data"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    row_count = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # File validation
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Excel Data File"
        verbose_name_plural = "Excel Data Files"
        indexes = [
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['is_processed']),
        ]

    def __str__(self):
        return f"Excel File - {self.file.name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        """Validate file upload"""
        super().clean()
        
        if self.file:
            # Check file extension
            file_ext = os.path.splitext(self.file.name)[1].lower()
            if file_ext not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f'File type not supported. Allowed types: {", ".join(self.ALLOWED_EXTENSIONS)}'
                )
            
            # Check file size
            if self.file.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    f'File size too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB'
                )

    def save(self, *args, **kwargs):
        """Override save to add file size"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def process_file(self):
        """Process the Excel file and extract metadata"""
        try:
            import pandas as pd
            
            if not self.file:
                raise ValidationError("No file to process")
            
            # Read Excel file
            df = pd.read_excel(self.file.path)
            
            # Update metadata
            self.row_count = len(df)
            self.is_processed = True
            self.processed_at = timezone.now()
            self.save(update_fields=['row_count', 'is_processed', 'processed_at'])
            
            return df
            
        except Exception as e:
            self.error_message = str(e)
            self.save(update_fields=['error_message'])
            raise ValidationError(f"Error processing file: {str(e)}")

    @property
    def file_name(self):
        """Get just the filename"""
        return os.path.basename(self.file.name) if self.file else ""

    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file_name)[1].lower()

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def is_valid_file(self):
        """Check if file is valid"""
        return (
            self.file and 
            self.file_extension in self.ALLOWED_EXTENSIONS and 
            self.file_size <= self.MAX_FILE_SIZE
        )

    def get_absolute_url(self):
        """Get admin URL for this object"""
        from django.urls import reverse
        return reverse('admin:website_exceldata_change', args=[str(self.id)])


# Additional utility models for better functionality

class SiteSettings(models.Model):
    """Global site settings model"""
    
    site_name = models.CharField(max_length=100, default="Luxe Stays India")
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField()
    instagram_username = models.CharField(max_length=100, default="luxestaysindia")
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Social media links
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # SEO settings
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)
    
    # Maintenance mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return f"Site Settings - {self.site_name}"

    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class NewsletterSubscription(models.Model):
    """Newsletter subscription model"""
    
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"

    def unsubscribe(self):
        """Unsubscribe from newsletter"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])


class PageView(models.Model):
    """Track page views for analytics"""
    
    page_name = models.CharField(max_length=100)
    url_path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-viewed_at']
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        indexes = [
            models.Index(fields=['page_name']),
            models.Index(fields=['viewed_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.page_name} - {self.ip_address} ({self.viewed_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def track_view(cls, request, page_name):
        """Track a page view"""
        return cls.objects.create(
            page_name=page_name,
            url_path=request.path,
            ip_address=cls.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', ''),
            session_id=request.session.session_key or '',
        )

    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 