from django.contrib import admin
from apps.waste_source_group.models import WasteGeneratorGroup, WasteGroupMaster, MasterSource, MasterDestination

@admin.register(WasteGeneratorGroup)
class WasteGeneratorGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)


@admin.register(WasteGroupMaster)
class WasteGroupMasterAdmin(admin.ModelAdmin):
    list_display = ['waste_group_generator__name']
    search_fields = ['waste_group_generator__name']


@admin.register(MasterSource)
class MasterSourceAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(MasterDestination)
class MasterDestinationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']