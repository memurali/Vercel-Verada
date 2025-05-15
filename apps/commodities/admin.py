from django.contrib import admin
from apps.commodities.models import ClientCommodity

@admin.register(ClientCommodity)
class ClientCommodityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'commoditie')
    search_fields = ('user__first_name', 'user__email', 'commoditie__name')
    list_filter = ('commoditie', 'user')
    autocomplete_fields = ('user', 'commoditie')  # if you have many records

    # Optional: better ordering
    ordering = ('-created_at',)