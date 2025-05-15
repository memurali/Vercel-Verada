from django.contrib import admin
from apps.core.models import CommodityMater, MeasuringUnitMaster, CommodityGroup


@admin.register(CommodityGroup)
class CommodityGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name']

@admin.register(CommodityMater)
class CommodityMaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(MeasuringUnitMaster)
class MeasuringUnitMasterAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

