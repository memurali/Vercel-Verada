from django.contrib import admin
from apps.waste_generators.models import (
    WasteSourceMaster,
    WasteSourceSpecificationMaster,
    Generator, 
    WasteSource,
    WastePickUp
)

@admin.register(WasteSourceMaster)
class WasteSourceMasterAdmin(admin.ModelAdmin):
    list_display = ('waste_source__name', 'status', 'waste_group', 'get_full_address')
    list_filter = ('status', 'waste_group')
    search_fields = ('waste_source__name',)

    def get_full_address(self, obj):
        return str(obj.address) if obj.address else "-"
    get_full_address.short_description = 'Address'



@admin.register(WasteSourceSpecificationMaster)
class WasteSourceSpecificationMasterAdmin(admin.ModelAdmin):
    list_display = ('waste_source', 'specification', 'status')
    list_filter = ('status', 'waste_source')
    search_fields = ('specification',)
    autocomplete_fields = ['waste_source']


@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'pin_code', 'waste_source', 'waste_source_specification', 'created_at', 'updated_at')
    list_filter = ('city',)
    search_fields = ('name', 'address_line_1', 'city', 'pin_code')
    autocomplete_fields = ['user', 'waste_source', 'waste_source_specification']


@admin.register(WasteSource)
class WasteSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'waste_source', 'waste_type', 'food_type', 'waste_weight', 'created_at')
    list_filter = ('waste_type', 'food_type')
    search_fields = ('waste_source__name', 'food_type__name', 'waste_type__name')


@admin.register(WastePickUp)
class WastePickUpAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_date', 'waste_source', 'destination', 'address', 'created_at')
    list_filter = ('pickup_date', 'destination')
    search_fields = ('waste_source__generator__name', 'destination__name', 'address')
