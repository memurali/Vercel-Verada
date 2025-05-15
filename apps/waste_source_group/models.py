from django.db import models
import re

class WasteGeneratorGroup(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Waste Generator Group"
        verbose_name_plural = "Waste Generator Groups"

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class WasteGroupMaster(models.Model):
    waste_group_generator = models.ForeignKey(WasteGeneratorGroup, on_delete=models.CASCADE)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.waste_group_generator.name

class MasterSource(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    def save(self, *args, **kwargs):
        if not self.code:
            # remove non-alphanumeric characters, convert to lowercase, and remove spaces
            cleaned = re.sub(r'[^a-zA-Z0-9]', '', self.name)
            self.code = cleaned.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

class MasterDestination(models.Model):
    name = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')