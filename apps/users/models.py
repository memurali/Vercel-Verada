from django.db import models
from django.contrib.auth.models import (
    AbstractUser, 
    Group, 
    Permission, 
    BaseUserManager
)

import uuid
from django.utils import timezone
from django.templatetags.static import static
from django.db.models import Q

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Client(TimeStampedModel):
    company_name = models.CharField(max_length=255)
    company_phone = models.CharField(max_length=20)
    company_logo = models.ImageField(upload_to='company_logo', blank=True)
    company_address = models.TextField()
    company_email = models.EmailField()
    company_website = models.URLField(blank=True, null=True)
    company_tax_id = models.CharField(max_length=50, blank=True, null=True)
    company_registration_number = models.CharField(max_length=50, blank=True, null=True)
    company_industry = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.IntegerField(null=True, blank=True)
    company_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # or use `related_name='+'` to disable reverse
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # or use `related_name='+'`
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    activation_token = models.CharField(max_length=128, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photo', blank=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def _has_role(self, role_name, restricted_only=False):
        query = Q(role__name__iexact=role_name)
        if restricted_only:
            query &= Q(role__restricted=True)
        return self.user_role.filter(query).exists()

    @property
    def get_profile_photo_url(self):
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return static("images/default-profile.png")
    
    @property
    def get_roles(self):
        return [ur.role.name.lower() for ur in self.user_role.all()]
    
    @property
    def is_auditor(self):
        return self.user_role.filter(role__name__iexact='Auditor').exists()
    
    @property
    def is_cityadmin(self):
        return self.user_role.filter(role__name__iexact='City Admin').exists()
    
    @property
    def is_data_manager(self):
        return self.user_role.filter(role__name__iexact='Data Manager').exists()
    
    def has_role(self, role_name):
        return self._has_role(role_name)


    def __str__(self):
        return f"{self.username}"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Role(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    restricted = models.BooleanField(default=False)  # New field

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

class UserRole(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.role}"
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

class Permission(TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module')
    description = models.TextField(blank=True, null=True)
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.module.name
    
    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.role} → {self.permission}"
    
    class Meta:
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
    
class UserPermission(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_permission')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.permission}"
    
    class Meta:
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'

class Subscription(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subsriptions'

class UserSubscription(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user} - {self.subscription.name}"
    
    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'


class OTPRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_otp')
    code = models.CharField(max_length=6)
    session_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)