from django.db import models
from apps.common.models import TimeStampedModel
from apps.users.models import User
from apps.waste_generators.models import Generator
from django.utils.timezone import now
from apps.common.models import Address

class CollectorType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Collector(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Collector Tax ID")
    collector_type = models.ForeignKey(CollectorType, on_delete=models.SET_NULL, null=True)
    collector_create_date = models.DateField(default=now)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class WasteDestination(models.Model):
    source = models.ForeignKey(Generator, on_delete=models.CASCADE)
    DESTINATION_TYPE_CHOICES = [
        ('donation', 'Donation'),
        ('compost', 'Compost'),
        ('landfill', 'Landfill'),
    ]
    destination_type = models.CharField(max_length=50, choices=DESTINATION_TYPE_CHOICES)
    received_at = models.DateField()

    def __str__(self):
        return f"{self.source.name} → {self.destination_type}"
