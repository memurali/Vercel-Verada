from django.db import models
from apps.common.models import TimeStampedModel
from apps.users.models import User
from apps.waste_source_group.models import WasteGroupMaster, WasteGeneratorGroup, MasterSource, MasterDestination
from apps.core.models import CommodityGroup
from apps.common.models import Address
from apps.core.models import CommodityMater

class WasteSourceMaster(TimeStampedModel):
    waste_source = models.ForeignKey(MasterSource, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    waste_group = models.ForeignKey(WasteGeneratorGroup, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField(null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.waste_source.name

class WasteSourceSpecificationMaster(models.Model):
    waste_source = models.ForeignKey(WasteSourceMaster, on_delete=models.CASCADE)
    specification = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    def __str__(self):
        return f"{self.waste_source} - {self.specification}"

class Generator(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)

    waste_source = models.ForeignKey(WasteSourceMaster, on_delete=models.CASCADE, null=True)
    waste_source_specification =  models.ForeignKey(WasteSourceSpecificationMaster, on_delete=models.CASCADE, null=True)
    Waste_generator_group = models.ForeignKey(WasteGeneratorGroup, on_delete=models.CASCADE, null=True)

    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField(null=True)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class WasteSource(TimeStampedModel):
    waste_source = models.ForeignKey(MasterSource, on_delete=models.CASCADE)
    waste_type = models.ForeignKey(CommodityGroup, on_delete=models.CASCADE)
    food_type = models.ForeignKey(CommodityMater, on_delete=models.CASCADE)
    waste_weight = models.FloatField()

    def __str__(self):
        return f"{self.waste_source.name} - {self.food_type} ({self.waste_weight}kg)"
    
class WastePickUp(TimeStampedModel):
    from apps.waste_collectors.models import Collector

    pickup_date = models.DateField()
    waste_source = models.ForeignKey(WasteSource, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='waste_pickup', blank=True, null=True)
    destination = models.ForeignKey(Collector, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pickup_date} at {self.address}"