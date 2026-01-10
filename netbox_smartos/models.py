from annoying.fields import AutoOneToOneField
from dcim.models import Device
from django.db import models


class SmartOSReport(models.Model):
    device = AutoOneToOneField(
        to=Device, on_delete=models.CASCADE, related_name="smartos_report"
    )
    report = models.JSONField(default=dict)
    last_heartbeat = models.DateTimeField(null=True)
    last_processed = models.DateTimeField(null=True)

    def __str__(self):
        return self.device.name
