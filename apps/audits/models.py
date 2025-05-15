from django.db import models
from apps.users.models import User
from apps.common.models import TimeStampedModel
from apps.waste_collectors.models import WasteDestination
from apps.core.models import CommodityGroup
from apps.waste_source_group.models import MasterSource
from apps.waste_generators.models import WasteSourceMaster

class Waiver(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    issued_at = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Official(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offical_user')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='official_created_user')

    def __str__(self):
        return f"{self.name} ({self.designation})"

class AuditLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Audit(models.Model):
    officer = models.ForeignKey(Official, on_delete=models.CASCADE, related_name='audit_offical')
    destination = models.ForeignKey(WasteSourceMaster, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField()
    end_time = models.TimeField(null=True, blank=True)
    conducted_date = models.DateField(null=True, blank=True)
    audit_findings = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=[
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Canceled'),
        ('S', 'Scheduled')
    ], default='P')
    media = models.TextField(blank=True)
    location = models.ForeignKey(MasterSource, null=True, on_delete=models.CASCADE,related_name='audit_location')
    TYPE_CHOICE = (
        ('initial', 'Initial Audit'),
        ('verification', 'Verification Audit')
    )
    audit_type = models.CharField(max_length=20, choices=TYPE_CHOICE, default='verification')
    waiver = models.ForeignKey(Waiver, on_delete=models.CASCADE, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    is_waiver_applied = models.BooleanField(default=False)
    WAIVER_TYPE_CHOICES = (
        ('minimus', 'Minimus'),
        ('space', 'Space'),
    )
    waiver_type = models.CharField(max_length=20, choices=WAIVER_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Audit for {self.destination} on {self.scheduled_date}"
    
class AuditCommoditi(TimeStampedModel):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='audit_commoditi')
    commodity_group = models.ForeignKey(CommodityGroup, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    contamination_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='audit_item_images', blank=True, null=True)
    contaminant_found = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.audit} - {self.commodity_group.name}"
    
class AuditCompliance(TimeStampedModel):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='audit_compliance')
    compliance = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.audit} - {self.compliance}"


class NonComplianceNotice(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='audit')
    issue_description = models.TextField()
    corrective_action = models.TextField(blank=True)
    raised_at = models.DateField()
    resolved_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Non-Compliance in Audit #{self.audit.id}"
