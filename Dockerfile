ARG NETBOX_VERSION=v4.4.10

FROM netboxcommunity/netbox:${NETBOX_VERSION}

RUN apt-get update && apt-get install -y postgresql-client

RUN mkdir -p /netbox_smartos
COPY requirements-dev.txt /netbox_smartos/requirements-dev.txt
RUN /usr/local/bin/uv pip install -r /netbox_smartos/requirements-dev.txt

RUN ipython profile create && echo "c.TerminalInteractiveShell.display_completions = 'readlinelike'" >> /root/.ipython/profile_default/ipython_config.py

COPY . /netbox_smartos/

RUN /usr/local/bin/uv pip install --editable /netbox_smartos
