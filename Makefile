container_name = netbox-smartos-netbox-1
worker_name = netbox-smartos-netbox-worker-1

build:
	docker compose build
up:
	docker compose up
reset-volumes:
	docker compose down --volumes
run: build up
reset: reset-volumes run
reload:
	docker exec -it $(container_name) curl -X GET --unix-socket /opt/unit/unit.sock http://localhost/control/applications/netbox/restart
	docker restart $(worker_name)
netbox-shell:
	docker exec -it $(container_name) bash
django-shell:
	docker exec -it $(container_name) ./manage.py shell
format:
	docker exec -it $(container_name) bash -c 'cd /netbox_smartos && isort . && ruff format .'
lint:
	docker exec -it $(container_name) bash -c 'cd /netbox_smartos && isort --check . && ruff format --check . && ruff check'
test:
	docker exec -it $(container_name) bash -c "pytest /netbox_smartos"
publish:
	rm -f dist/*
	python3 -m build --sdist
	python3 -m twine upload --verbose dist/*
