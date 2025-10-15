from django.db import models
from django.utils import timezone


class WhatsAppMessage(models.Model):
    """
    Store incoming WhatsApp messages
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('location', 'Location'),
        ('contacts', 'Contacts'),
        ('interactive', 'Interactive'),
        ('unknown', 'Unknown'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    
    # Message identifiers
    message_id = models.CharField(max_length=255, unique=True, db_index=True)
    wamid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Sender information
    from_number = models.CharField(max_length=20, db_index=True)
    from_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    text_body = models.TextField(blank=True, null=True)
    
    # Media fields (for images, videos, audio, documents)
    media_id = models.CharField(max_length=255, blank=True, null=True)
    media_mime_type = models.CharField(max_length=100, blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    media_caption = models.TextField(blank=True, null=True)
    
    # Location fields
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    location_address = models.TextField(blank=True, null=True)
    
    # Metadata
    timestamp = models.DateTimeField(db_index=True)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    
    # Raw webhook data for debugging
    raw_payload = models.JSONField(blank=True, null=True)
    
    # Context (reply to message)
    context_message_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['from_number', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.from_number} - {self.message_type} - {self.timestamp}"


class WhatsAppMessageStatus(models.Model):
    """
    Store status updates for sent messages (delivered, read, etc.)
    """
    STATUS_TYPES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    message_id = models.CharField(max_length=255, db_index=True)
    recipient_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Raw webhook data
    raw_payload = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['message_id', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.message_id} - {self.status} - {self.timestamp}"


class WhatsAppConversation(models.Model):
    """
    Group messages by phone number for easier conversation tracking
    """
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    last_message_at = models.DateTimeField(default=timezone.now)
    message_count = models.IntegerField(default=0)
    unread_count = models.IntegerField(default=0)
    
    # Customer info (can be linked to your customer database)
    customer_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_message_at']
    
    def __str__(self):
        return f"{self.contact_name or self.phone_number} - {self.message_count} messages"
