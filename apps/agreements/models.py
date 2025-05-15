from django.db import models
from apps.waste_generators.models import WasteSourceMaster
from apps.waste_collectors.models import Collector
from apps.common.models import TimeStampedModel
from apps.core.models import CommodityMater, MeasuringUnitMaster

class Agreement(TimeStampedModel):
    generator = models.ForeignKey(WasteSourceMaster, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    agreement_paper = models.FileField(upload_to='agreements', blank=True)
    expiration_date = models.DateField(default="2025-05-04")


    def __str__(self):
        return f"Agreement: {self.generator.waste_source.name} ↔ {self.collector.name}"


class AgreementItem(TimeStampedModel):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    commodity = models.ForeignKey(CommodityMater, on_delete=models.CASCADE)
    measuring_unit = models.ForeignKey(MeasuringUnitMaster, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=100)  # e.g., 'Daily', 'Weekly'
    custom_schedule_dates = models.TextField(blank=True, null=True)  # CSV format or JSON

    def __str__(self):
        return f"{self.commodity.name} - {self.quantity} {self.measuring_unit.name}"

class AgreementSchedule(models.Model):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    scheduled_day = models.CharField(max_length=20)
    time_range = models.CharField(max_length=50)