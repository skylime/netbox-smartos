from core.models import ObjectType
from dcim.models import Device, Interface
from extras.models import CustomField
from virtualization.models import VirtualMachine, VMInterface


def ensure_custom_fields_exist():
    base_defaults = {
        "required": False,
        "is_cloneable": False,
        "default": None,
        "weight": 100,
        "search_weight": 100,
        "filter_logic": "exact",
        "ui_visible": "always",
        "ui_editable": "yes",
        "group_name": "SmartOS",
    }

    smartos_device_uuid, _ = CustomField.objects.get_or_create(
        name="smartos_device_uuid",
        defaults={
            **base_defaults,
            "label": "UUID",
            "type": "text",
        },
    )
    smartos_device_uuid.object_types.add(ObjectType.objects.get_for_model(Device))

    smartos_version, _ = CustomField.objects.get_or_create(
        name="smartos_version",
        defaults={
            **base_defaults,
            "label": "Version",
            "type": "text",
        },
    )
    smartos_version.object_types.add(ObjectType.objects.get_for_model(Device))

    smartos_nictag, _ = CustomField.objects.get_or_create(
        name="smartos_nictag",
        defaults={
            **base_defaults,
            "label": "Nic Tag",
            "type": "text",
        },
    )
    smartos_nictag.object_types.add(ObjectType.objects.get_for_model(Interface))
    smartos_nictag.object_types.add(ObjectType.objects.get_for_model(VMInterface))

    smartos_brand, _ = CustomField.objects.get_or_create(
        name="smartos_brand",
        defaults={
            **base_defaults,
            "label": "Brand",
            "type": "text",
            "weight": 100,
        },
    )
    smartos_brand.object_types.add(ObjectType.objects.get_for_model(VirtualMachine))

    smartos_image_uuid, _ = CustomField.objects.get_or_create(
        name="smartos_image_uuid",
        defaults={
            **base_defaults,
            "label": "Image UUID",
            "type": "text",
            "weight": 101,
        },
    )
    smartos_image_uuid.object_types.add(
        ObjectType.objects.get_for_model(VirtualMachine)
    )

    smartos_image_name, _ = CustomField.objects.get_or_create(
        name="smartos_image_name",
        defaults={
            **base_defaults,
            "label": "Image Name",
            "type": "text",
            "weight": 102,
        },
    )
    smartos_image_name.object_types.add(
        ObjectType.objects.get_for_model(VirtualMachine)
    )

    smartos_image_version, _ = CustomField.objects.get_or_create(
        name="smartos_image_version",
        defaults={
            **base_defaults,
            "label": "Image Version",
            "type": "text",
            "weight": 103,
        },
    )
    smartos_image_version.object_types.add(
        ObjectType.objects.get_for_model(VirtualMachine)
    )

    smartos_owner_uuid, _ = CustomField.objects.get_or_create(
        name="smartos_owner_uuid",
        defaults={
            **base_defaults,
            "label": "Owner UUID",
            "type": "text",
            "weight": 105,
        },
    )
    smartos_owner_uuid.object_types.add(
        ObjectType.objects.get_for_model(VirtualMachine)
    )

    smartos_billing_uuid, _ = CustomField.objects.get_or_create(
        name="smartos_billing_uuid",
        defaults={
            **base_defaults,
            "label": "Billing UUID",
            "type": "text",
            "weight": 104,
        },
    )
    smartos_billing_uuid.object_types.add(
        ObjectType.objects.get_for_model(VirtualMachine)
    )
