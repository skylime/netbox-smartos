import uuid
from contextlib import ExitStack

from dcim.choices import InterfaceTypeChoices
from dcim.fields import mac_unix_expanded_uppercase
from dcim.models import MACAddress
from django.db import transaction
from django.utils import timezone
from ipam.models import IPAddress
from netaddr import EUI, IPNetwork
from netbox.jobs import JobRunner
from netbox.registry import registry
from users.models import User
from utilities.request import NetBoxFakeRequest
from virtualization.choices import VirtualMachineStatusChoices
from virtualization.models import VirtualMachine

from netbox_smartos.custom_fields import ensure_custom_fields_exist

VM_STATE_MAP = {
    "configured": VirtualMachineStatusChoices.STATUS_PLANNED,
    "down": VirtualMachineStatusChoices.STATUS_OFFLINE,
    "failed": VirtualMachineStatusChoices.STATUS_FAILED,
    "incomplete": VirtualMachineStatusChoices.STATUS_PLANNED,
    "installed": VirtualMachineStatusChoices.STATUS_PLANNED,
    "provisioning": VirtualMachineStatusChoices.STATUS_PLANNED,
    "ready": VirtualMachineStatusChoices.STATUS_PLANNED,
    "receiving": VirtualMachineStatusChoices.STATUS_PLANNED,
    "running": VirtualMachineStatusChoices.STATUS_ACTIVE,
    "shutting_down": VirtualMachineStatusChoices.STATUS_DECOMMISSIONING,
    "stopped": VirtualMachineStatusChoices.STATUS_OFFLINE,
    "stopping": VirtualMachineStatusChoices.STATUS_DECOMMISSIONING,
}


def update_attr(obj, attr, value):
    if not value:
        return

    if getattr(obj, attr) == value:
        return

    setattr(obj, attr, value)
    obj.has_changed = True


def update_cf_attr(obj, attr, value):
    if not value:
        return

    if obj.custom_field_data.get(attr) == value:
        return

    obj.custom_field_data[attr] = value
    obj.has_changed = True


def discover_mac(interface, mac_address):
    if not mac_address:
        return

    mac_changed = False
    if not interface.primary_mac_address:
        if getattr(interface, "has_changed", False) or interface.pk is None:
            interface.save()
        interface.primary_mac_address = MACAddress(assigned_object=interface)
        interface.has_changed = True
        mac_changed = True

    formatted_mac = EUI(mac_address, version=48, dialect=mac_unix_expanded_uppercase)
    if interface.primary_mac_address.mac_address != formatted_mac:
        interface.primary_mac_address.mac_address = formatted_mac
        mac_changed = True
    if mac_changed:
        interface.primary_mac_address.save()


class ProcessSmartOSReportJob(JobRunner):
    class Meta:
        name = "Process SmartOS Report"

    def run(self, device, *args, **kwargs):
        self.logger.debug(f"Processing {device}")

        user, _ = User.objects.get_or_create(username="smartos-bot")
        request = NetBoxFakeRequest(
            {
                "META": {},
                "POST": {},
                "GET": {},
                "FILES": {},
                "user": user,
                "path": "",
                "id": uuid.uuid4(),
            }
        )

        with ExitStack() as stack:
            for request_processor in registry["request_processors"]:
                stack.enter_context(request_processor(request))

            with transaction.atomic():
                self._process(device)

    def _process(self, device):
        ensure_custom_fields_exist()
        sysinfo = device.smartos_report.report.get("sysinfo", {})
        vms = device.smartos_report.report.get("vm", {})
        imgs = device.smartos_report.report.get("img", {})
        img_by_uuid = {
            img["manifest"]["uuid"]: img
            for img in imgs
            if "manifest" in img and "uuid" in img["manifest"]
        }

        device.has_changed = False

        update_attr(device, "serial", sysinfo.get("Serial Number"))

        update_cf_attr(device, "smartos_device_uuid", sysinfo.get("UUID"))
        update_cf_attr(device, "smartos_version", sysinfo.get("Live Image"))

        if device.has_changed:
            device.save()

        # Interfaces
        nics = sysinfo.get("Network Interfaces", {})
        for name, nic_info in nics.items():
            interface, _ = device.interfaces.get_or_create(name=name)

            interface.has_changed = False
            mac_address = nic_info.get("MAC Address")
            discover_mac(interface, mac_address)

            nic_tags = ",".join(sorted(nic_info.get("NIC Names", [])))
            update_cf_attr(interface, "smartos_nictag", nic_tags)

            if interface.has_changed:
                interface.save()

            # IPv4 can't be done bacause we don't have the prefix len

        # Nictags in "Virtual Network Interfaces"
        vnics = sysinfo.get("Virtual Network Interfaces", {})
        for name, nic_info in vnics.items():
            interface, _ = device.interfaces.get_or_create(name=name)
            update_attr(interface, "type", InterfaceTypeChoices.TYPE_VIRTUAL)

            interface.has_changed = False
            mac_address = nic_info.get("MAC Address")
            discover_mac(interface, mac_address)

            if parent_name := nic_info.get("Host Interface"):
                parent = device.interfaces.filter(name=parent_name).first()
                update_attr(interface, "parent", parent)

            if interface.has_changed:
                interface.save()

        # VMs
        vm_ids = set([vm["uuid"] for vm in vms])
        device.virtual_machines.exclude(name__in=vm_ids).delete()
        for vm_info in vms:
            if (
                VirtualMachine.objects.exclude(device=device)
                .filter(name=vm_info["uuid"])
                .exists()
            ):
                self.logger.warning(f"Duplicate VM with UUID {vm_info['uuid']}")
                continue

            vm, _ = VirtualMachine.objects.get_or_create(name=vm_info["uuid"])
            vm.has_changed = False

            update_attr(vm, "description", vm_info.get("alias"))
            update_attr(vm, "device", device)
            update_attr(vm, "cluster", device.cluster)
            update_attr(vm, "site", device.site)
            update_attr(vm, "memory", vm_info.get("ram"))
            update_attr(vm, "disk", vm_info.get("quota", 0) * 1024)
            update_attr(vm, "vcpus", vm_info.get("cpu_cap", 0) / 100)

            state = vm_info.get("state")
            if state in VM_STATE_MAP:
                update_attr(vm, "status", VM_STATE_MAP[state])

            update_cf_attr(vm, "smartos_brand", vm_info.get("brand"))
            update_cf_attr(vm, "smartos_owner_uuid", vm_info.get("owner_uuid"))
            update_cf_attr(vm, "smartos_billing_uuid", vm_info.get("billing_id"))

            img_uuid = vm_info.get("image_uuid")
            img_manifest = img_by_uuid.get(img_uuid, {}).get("manifest", {})
            update_cf_attr(vm, "smartos_image_uuid", img_uuid)
            update_cf_attr(vm, "smartos_image_name", img_manifest.get("name"))
            update_cf_attr(vm, "smartos_image_version", img_manifest.get("version"))

            if vm.has_changed:
                vm.save()

            nic_by_name = {nic["interface"]: nic for nic in vm_info.get("nics", [])}
            vm.interfaces.exclude(name__in=nic_by_name.keys()).delete()
            for name, nic_info in nic_by_name.items():
                nic, _ = vm.interfaces.get_or_create(name=name)

                nic.has_changed = False
                discover_mac(nic, nic_info.get("mac"))
                update_cf_attr(nic, "smartos_nictag", nic_info.get("nic_tag"))

                if nic.has_changed:
                    nic.save()

                addrs = []
                for addr in nic_info.get("ips", []):
                    if addr in ["dhcp", "addrconf"]:
                        continue
                    ip_addr = IPNetwork(addr)

                    addr = (
                        IPAddress.objects.filter(
                            address__net_host_contained=ip_addr.ip
                        ).first()
                        or IPAddress()
                    )
                    if addr.pk:
                        addr.has_changed = False
                    else:
                        addr.has_changed = True

                    update_attr(addr, "address", ip_addr)

                    # TODO: if primary nic we could also set this as primary so on vm

                    if addr.has_changed:
                        addr.save()

                    addrs += [addr]

                nic.ip_addresses.set(addrs)

        device.smartos_report.last_processed = timezone.now()
        device.smartos_report.save()
