from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address_line_1', 'city', 'state', 'pin_code')
    search_fields = ('address_line_1', 'city', 'state', 'pin_code')
