from importlib.metadata import metadata

from netbox.plugins import PluginConfig

metadata = metadata("netbox_smartos")


class NetboxSmartOSConfig(PluginConfig):
    name = "netbox_smartos"
    verbose_name = "Netbox SmartOS"
    description = "SmartOS integration"
    version = metadata.get("Version")
    base_url = "smartos"
    min_version = "4.2.0"
    django_apps = []
    author = "SkyLime GmbH"
    author_email = "info@skylime.net"


config = NetboxSmartOSConfig
