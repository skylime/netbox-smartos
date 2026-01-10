from dcim.api.serializers import DeviceSerializer
from rest_framework import serializers

from netbox_smartos.models import SmartOSReport


class SmartOSReportSerializer(serializers.Serializer):
    device = DeviceSerializer(nested=True, read_only=True)
    token = serializers.CharField(write_only=True)
    report = serializers.JSONField()

    class Meta:
        model = SmartOSReport
        fields = ("id", "device", "token", "report", "last_heartbeat", "last_processed")
        brief_fields = ("id", "device")
