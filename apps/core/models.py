from django.db import models
from apps.common.models import TimeStampedModel
from apps.users.models import User

class MeasuringUnitMaster(TimeStampedModel):
    name = models.CharField(max_length=100)
    symbol = models.ImageField(upload_to='measuring_unit')
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    def __str__(self):
        return self.name
    
class CommodityGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    def __str__(self):
        return self.name

class CommodityMater(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    measuring_unit = models.ForeignKey(MeasuringUnitMaster, on_delete=models.CASCADE)
    sub_commodity = models.CharField(max_length=255, blank=True, null=True)
    group = models.ForeignKey(CommodityGroup, on_delete=models.SET_NULL, null=True, verbose_name="Commodity Group")

    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    commodity_doc = models.FileField(upload_to='commodity', blank=True, null=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commodity_created_user', null=True)

    def __str__(self):
        return self.name
