import logging

from dcim.models import Device
from django.utils import timezone
from netbox.plugins import get_plugin_config
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from netbox_smartos.api.serializers import SmartOSReportSerializer
from netbox_smartos.jobs import ProcessSmartOSReportJob

logger = logging.getLogger("netbox_smartos.api.views")


class DeviceReportView(APIView):
    permission_classes = []
    serializer_class = SmartOSReportSerializer
    queryset = Device.objects.all()

    def post(self, request):
        serializer = SmartOSReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        if not token or (token != get_plugin_config("netbox_smartos", "api_token")):
            raise AuthenticationFailed()

        report = serializer.validated_data["report"]
        device_uuid = report.get("sysinfo", {}).get("UUID", "")
        device_hostname = report.get("sysinfo", {}).get("Hostname", "")

        device = None
        if device_uuid:
            device = Device.objects.filter(
                custom_field_data__smartos_device_uuid=device_uuid
            ).first()
        if not device and device_hostname:
            device = Device.objects.filter(name=device_hostname).first()

        if not device:
            raise ValidationError({"device": "Could not find matching device."})

        device.smartos_report.report = report
        device.smartos_report.last_heartbeat = timezone.now()
        device.smartos_report.save()

        ProcessSmartOSReportJob.enqueue(device=device)

        return Response({"status": "ok"})
