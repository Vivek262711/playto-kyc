from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'merchant', 'event_type', 'timestamp']
    list_filter = ['event_type']
    search_fields = ['merchant__name']
    readonly_fields = ['timestamp']
