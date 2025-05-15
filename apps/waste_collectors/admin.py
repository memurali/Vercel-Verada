from django.contrib import admin
from .models import CollectorType, Collector, WasteDestination


@admin.register(CollectorType)
class CollectorTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Collector)
class CollectorAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'collector_type', 'user', 'get_full_address'
    )
    list_filter = ('collector_type',)
    search_fields = ('name', 'address')
    autocomplete_fields = ['user', 'collector_type']

    def get_full_address(self, obj):
        return str(obj.address) if obj.address else "-"
    get_full_address.short_description = 'Address'


@admin.register(WasteDestination)
class WasteDestinationAdmin(admin.ModelAdmin):
    list_display = (
        'source', 'destination_type', 'received_at'
    )
    list_filter = ('destination_type', 'received_at')
    search_fields = ('source__name',)
    autocomplete_fields = ['source']
