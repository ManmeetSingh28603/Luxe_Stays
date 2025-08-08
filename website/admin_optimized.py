from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    ContactSubmission, 
    ExcelData, 
    SiteSettings, 
    NewsletterSubscription, 
    PageView
)

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Optimized admin for contact submissions"""
    
    list_display = [
        'name', 
        'email', 
        'submitted_at', 
        'is_processed', 
        'is_recent_display',
        'ip_address'
    ]
    list_filter = [
        'is_processed', 
        'submitted_at',
        ('submitted_at', admin.DateFieldListFilter),
    ]
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['submitted_at', 'ip_address', 'user_agent']
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'message')
        }),
        ('Submission Details', {
            'fields': ('submitted_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processed_at')
        }),
    )

    def is_recent_display(self, obj):
        """Display if submission is recent"""
        if obj.is_recent:
            return format_html(
                '<span style="color: green;">✓ Recent</span>'
            )
        return format_html(
            '<span style="color: gray;">Old</span>'
        )
    is_recent_display.short_description = 'Recent'

    def mark_as_processed(self, request, queryset):
        """Mark selected submissions as processed"""
        updated = queryset.update(
            is_processed=True, 
            processed_at=timezone.now()
        )
        self.message_user(
            request, 
            f'Successfully marked {updated} submissions as processed.'
        )
    mark_as_processed.short_description = "Mark selected submissions as processed"

    def mark_as_unprocessed(self, request, queryset):
        """Mark selected submissions as unprocessed"""
        updated = queryset.update(
            is_processed=False, 
            processed_at=None
        )
        self.message_user(
            request, 
            f'Successfully marked {updated} submissions as unprocessed.'
        )
    mark_as_unprocessed.short_description = "Mark selected submissions as unprocessed"

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related()


@admin.register(ExcelData)
class ExcelDataAdmin(admin.ModelAdmin):
    """Optimized admin for Excel data files"""
    
    list_display = [
        'file_name', 
        'file_size_mb', 
        'row_count', 
        'uploaded_at', 
        'is_processed',
        'is_valid_file_display'
    ]
    list_filter = ['is_processed', 'uploaded_at']
    search_fields = ['file']
    readonly_fields = [
        'uploaded_at', 
        'file_size', 
        'row_count', 
        'processed_at',
        'error_message'
    ]
    actions = ['process_files', 'clear_errors']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_size', 'row_count')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processed_at', 'error_message')
        }),
    )

    def is_valid_file_display(self, obj):
        """Display file validation status"""
        if obj.is_valid_file:
            return format_html(
                '<span style="color: green;">✓ Valid</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Invalid</span>'
        )
    is_valid_file_display.short_description = 'File Status'

    def process_files(self, request, queryset):
        """Process selected Excel files"""
        processed = 0
        errors = 0
        
        for excel_file in queryset:
            try:
                excel_file.process_file()
                processed += 1
            except Exception as e:
                errors += 1
                excel_file.error_message = str(e)
                excel_file.save()
        
        if processed > 0:
            self.message_user(
                request, 
                f'Successfully processed {processed} files.'
            )
        if errors > 0:
            self.message_user(
                request, 
                f'Failed to process {errors} files. Check error messages.',
                level='WARNING'
            )
    process_files.short_description = "Process selected Excel files"

    def clear_errors(self, request, queryset):
        """Clear error messages from selected files"""
        updated = queryset.update(error_message='')
        self.message_user(
            request, 
            f'Cleared error messages from {updated} files.'
        )
    clear_errors.short_description = "Clear error messages"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for site settings"""
    
    def has_add_permission(self, request):
        """Only allow one site settings instance"""
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of site settings"""
        return False

    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'contact_email', 'phone_number', 'address')
        }),
        ('Social Media', {
            'fields': ('instagram_username', 'instagram_url', 'facebook_url', 'twitter_url', 'linkedin_url')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'facebook_pixel_id')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin for newsletter subscriptions"""
    
    list_display = ['email', 'subscribed_at', 'is_active', 'ip_address']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'ip_address']
    actions = ['unsubscribe_selected', 'resubscribe_selected']
    date_hierarchy = 'subscribed_at'

    def unsubscribe_selected(self, request, queryset):
        """Unsubscribe selected emails"""
        for subscription in queryset:
            subscription.unsubscribe()
        self.message_user(
            request, 
            f'Successfully unsubscribed {queryset.count()} emails.'
        )
    unsubscribe_selected.short_description = "Unsubscribe selected emails"

    def resubscribe_selected(self, request, queryset):
        """Resubscribe selected emails"""
        updated = queryset.update(
            is_active=True, 
            unsubscribed_at=None
        )
        self.message_user(
            request, 
            f'Successfully resubscribed {updated} emails.'
        )
    resubscribe_selected.short_description = "Resubscribe selected emails"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    """Admin for page views analytics"""
    
    list_display = ['page_name', 'ip_address', 'viewed_at', 'session_id']
    list_filter = ['page_name', 'viewed_at']
    search_fields = ['page_name', 'ip_address', 'url_path']
    readonly_fields = ['page_name', 'url_path', 'ip_address', 'user_agent', 'referrer', 'viewed_at', 'session_id']
    date_hierarchy = 'viewed_at'
    
    def has_add_permission(self, request):
        """Prevent manual addition of page views"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of page views"""
        return False

    def get_queryset(self, request):
        """Optimize queryset for large datasets"""
        return super().get_queryset(request).only(
            'page_name', 'ip_address', 'viewed_at', 'session_id', 'url_path'
        )


# Custom admin site configuration
admin.site.site_header = "Luxe Stays India - Admin"
admin.site.site_title = "Luxe Stays Admin"
admin.site.index_title = "Welcome to Luxe Stays India Administration"

# Add custom admin actions
def export_contact_submissions(modeladmin, request, queryset):
    """Export contact submissions to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_submissions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Message', 'Submitted At', 'IP Address'])
    
    for submission in queryset:
        writer.writerow([
            submission.name,
            submission.email,
            submission.message,
            submission.submitted_at,
            submission.ip_address
        ])
    
    return response
export_contact_submissions.short_description = "Export selected submissions to CSV"

# Add the action to the admin
ContactSubmissionAdmin.actions += [export_contact_submissions] 