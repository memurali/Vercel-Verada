from django.contrib import admin
from .models import (
    Waiver, Official, AuditLocation, Audit, NonComplianceNotice,
    AuditCommoditi, AuditCompliance
)
from django.utils.html import format_html

@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ('title', 'issued_at', 'valid_until')
    search_fields = ('title',)
    list_filter = ('issued_at', 'valid_until')

@admin.register(Official)
class OfficialAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'user')
    search_fields = ('name', 'designation')
    autocomplete_fields = ['user']

@admin.register(AuditLocation)
class AuditLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('officer', 'destination', 'scheduled_date', 'end_date', 'status', 'is_waiver_applied')
    list_filter = ('status', 'scheduled_date', 'end_date', 'is_waiver_applied')
    search_fields = ('officer__name', 'destination__source__name')
    autocomplete_fields = ['officer', 'destination', 'waiver']
    fieldsets = (
        ("General Info", {
            'fields': ('officer', 'destination', 'status', 'waiver')
        }),
        ("Schedule", {
            'fields': ('scheduled_date', 'scheduled_time', 'end_date', 'end_time', 'location', 'audit_type')
        }),
        ('Waiver Info', {
            'fields': ('is_waiver_applied', 'waiver_type')
        }),
        ("Conducted Info", {
            'fields': ('conducted_date', 'audit_findings', 'media')
        }),
    )

@admin.register(AuditCommoditi)
class AuditCommoditiAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'audit',
        'commodity_group',
        'weight',
        'contaminant_found',
        'image_preview',
        'created_at',
    )
    list_filter = ('commodity_group', 'contaminant_found')
    search_fields = ('audit__id', 'commodity_group__name')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = "Image Preview"

@admin.register(AuditCompliance)
class AuditComplianceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'audit',
        'compliance',
        'created_at',
    )
    list_filter = ('compliance',)
    search_fields = ('audit__id',)

@admin.register(NonComplianceNotice)
class NonComplianceNoticeAdmin(admin.ModelAdmin):
    list_display = ('audit', 'issue_description', 'raised_at', 'resolved_at')
    list_filter = ('raised_at', 'resolved_at')
    search_fields = ('issue_description', 'corrective_action')
    autocomplete_fields = ['audit']
