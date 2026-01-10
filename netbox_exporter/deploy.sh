#!/bin/bash
set -e

if [ $# -ne 1 ]; then
	echo "${0} [host]"
	exit 0
fi

host=${1}

ssh -n $host "rm -rf /opt/netbox_exporter"
ssh -n $host "mkdir  /opt/netbox_exporter"
scp -r * $host:/opt/netbox_exporter
ssh -n $host "mkdir -p /opt/custom/smf/"
ssh -n $host "cp /opt/netbox_exporter/manifest.xml /opt/custom/smf/netbox_exporter.xml"
