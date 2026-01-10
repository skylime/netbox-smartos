from django.urls import path

from . import views

app_name = "netbox_smartos"

urlpatterns = [
    path("report", views.DeviceReportView.as_view(), name="device-report"),
]
