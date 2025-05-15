from django.contrib import admin
from .models import Agreement, AgreementItem, AgreementSchedule


class AgreementItemInline(admin.TabularInline):
    model = AgreementItem
    extra = 1
    fields = ('commodity', 'measuring_unit', 'quantity', 'frequency', 'custom_schedule_dates')
    autocomplete_fields = ['commodity', 'measuring_unit']


class AgreementScheduleInline(admin.TabularInline):
    model = AgreementSchedule
    extra = 1
    fields = ('scheduled_day', 'time_range')


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = (
        'generator', 'collector', 'start_date', 'end_date',
        'is_active', 'created_at', 'updated_at'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('generator__name', 'collector__name', 'notes')
    autocomplete_fields = ['generator', 'collector']
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AgreementItemInline, AgreementScheduleInline]


@admin.register(AgreementItem)
class AgreementItemAdmin(admin.ModelAdmin):
    list_display = (
        'agreement', 'commodity', 'measuring_unit',
        'quantity', 'frequency'
    )
    search_fields = ('agreement__generator__name', 'commodity__name')
    autocomplete_fields = ['agreement', 'commodity', 'measuring_unit']


@admin.register(AgreementSchedule)
class AgreementScheduleAdmin(admin.ModelAdmin):
    list_display = ('agreement', 'scheduled_day', 'time_range')
    search_fields = ('agreement__generator__name',)
    autocomplete_fields = ['agreement']
