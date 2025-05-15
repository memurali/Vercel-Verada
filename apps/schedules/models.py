from django.db import models
from apps.users.models import User
from apps.common.models import TimeStampedModel

class ScheduledAudit(models.Model):
    inspector = models.ForeignKey(User, on_delete=models.CASCADE)
    scheduled_for = models.DateField()
    notes = models.TextField(blank=True, null=True)

class ScheduledReport(TimeStampedModel):
    REPORT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
    ]
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Dates'),
    ]

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100, choices=REPORT_TYPE_CHOICES)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    custom_schedule_dates = models.TextField(blank=True, null=True)
    recipients = models.TextField()  # email addresses
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default='active')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

