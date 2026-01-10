# SmartOS netbox_exporter


Installation:

- copy "example_config.json" to "config.json" and adjust the "url" and "token" values to match your plugin installation.
- run `./deploy.sh <hostname>`
- reboot the server or issue `svccfg import /opt/custom/smf/netbox_exporter.xml`

