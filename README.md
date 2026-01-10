# netbox-smartos

Netbox plugin for smartos vm and inventory integration.



## Installation


Generate a long random secret api token and add the following entries to your netbox configuration:


```
PLUGINS = [
    "netbox_smartos",
]

PLUGINS_CONFIG = {
    "netbox_smartos": {
        "api_token": "secret",
    },
}

```

Run `manage.py migrate` and `manage.py create_netbox_smartos_initial_data`.

On your smartos hosts install the `netbox_exporter`, see `netbox_exporter/README.md` for details.

