from django.contrib import admin
from .models import WhatsAppMessage, WhatsAppMessageStatus, WhatsAppConversation


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = [
        'from_number', 
        'from_name', 
        'message_type', 
        'text_preview',
        'timestamp', 
        'status'
    ]
    list_filter = ['message_type', 'status', 'timestamp']
    search_fields = ['from_number', 'from_name', 'text_body']
    readonly_fields = [
        'message_id', 
        'wamid', 
        'from_number', 
        'timestamp', 
        'received_at',
        'raw_payload'
    ]
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('message_id', 'wamid', 'from_number', 'from_name', 'message_type', 'status')
        }),
        ('Content', {
            'fields': ('text_body', 'media_id', 'media_mime_type', 'media_url', 'media_caption')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name', 'location_address'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('timestamp', 'received_at', 'context_message_id'),
        }),
        ('Raw Data', {
            'fields': ('raw_payload',),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        if obj.text_body:
            return obj.text_body[:50] + ('...' if len(obj.text_body) > 50 else '')
        elif obj.media_caption:
            return f"[{obj.message_type}] {obj.media_caption[:30]}"
        else:
            return f"[{obj.message_type}]"
    text_preview.short_description = 'Preview'


@admin.register(WhatsAppMessageStatus)
class WhatsAppMessageStatusAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'recipient_number', 'status', 'timestamp', 'error_code']
    list_filter = ['status', 'timestamp']
    search_fields = ['message_id', 'recipient_number']
    readonly_fields = ['message_id', 'recipient_number', 'status', 'timestamp', 'raw_payload']
    ordering = ['-timestamp']


@admin.register(WhatsAppConversation)
class WhatsAppConversationAdmin(admin.ModelAdmin):
    list_display = [
        'phone_number', 
        'contact_name', 
        'message_count', 
        'unread_count',
        'last_message_at'
    ]
    list_filter = ['last_message_at']
    search_fields = ['phone_number', 'contact_name', 'customer_email']
    readonly_fields = ['phone_number', 'message_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('phone_number', 'contact_name', 'customer_email')
        }),
        ('Message Stats', {
            'fields': ('message_count', 'unread_count', 'last_message_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
