from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Role, UserRole, Permission,
    RolePermission, UserPermission,
    Client, Subscription, UserSubscription,
    OTPRequest, Module
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'is_active', 'client')
    list_filter = ('is_active', 'client')
    search_fields = ('username', 'email', 'company_name')
    ordering = ('username',)

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'company_name', 'profile_photo')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('User Type', {
            'fields': ('client',)
        }),
        ('Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at', 'updated_at')
    list_filter = ('role',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    list_filter = ('code',)
    ordering = ('id',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('module', 'can_read', 'can_write', 'can_delete', 'created_at', 'updated_at')
    list_filter = ('module__name', 'can_read', 'can_write', 'can_delete')
    search_fields = ('name', 'module__name')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    list_filter = ('role',)


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission')
    list_filter = ('permission',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_phone', 'company_email', 'company_website')
    search_fields = ('company_name', 'company_email', 'company_tax_id')
    list_filter = ('company_industry',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'start_date', 'end_date', 'payment_status')
    list_filter = ('payment_status', 'start_date', 'end_date')


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'session_token', 'is_verified', 'created_at', 'expired_status')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email', 'code', 'session_token')
    readonly_fields = ('created_at', 'session_token', 'expired_status')

    def expired_status(self, obj):
        return obj.is_expired()
    expired_status.short_description = 'Is Expired'
    expired_status.boolean = True