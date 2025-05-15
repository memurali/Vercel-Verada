from django.db import models
from apps.users.models import User, Client

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    table_name = models.CharField(max_length=255, null=True, blank=True)
    record_id = models.IntegerField()
    old_value = models.JSONField()
    new_value = models.JSONField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.user} - {self.table_name} - {self.action}"
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
class SupportQuery(TimeStampedModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    query_type = models.CharField(max_length=50)
    query_text = models.TextField()
    module_name = models.CharField(max_length=100, null=True, blank=True)
    support_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_queries")
    description = models.TextField()
    resolution_provided = models.TextField(blank=True, null=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    query_media = models.FileField(upload_to='support_query', null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    exception_code = models.CharField(max_length=255, blank=True, null=True)
    exception_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"SupportQuery #{self.id} - {self.status}"
    
class SystemSetting(TimeStampedModel):
    name = models.CharField(max_length=255)
    value = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Address(models.Model):
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)

    def __str__(self):
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.pin_code,
        ]
        return ', '.join([p for p in parts if p])
