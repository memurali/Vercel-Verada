from django.db import models
from apps.core.models import CommodityMater
from apps.users.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ClientCommodity(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commoditie = models.ForeignKey(CommodityMater, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} - {self.commoditie.name}"

    class Meta:
        verbose_name = 'Client Commoditie'
        verbose_name_plural = 'Client Commodities'