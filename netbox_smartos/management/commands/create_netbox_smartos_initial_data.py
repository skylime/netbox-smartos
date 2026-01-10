from dcim.models.sites import Site
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from users.models import User

from netbox_smartos.custom_fields import ensure_custom_fields_exist


def create_admin():
    admin, _ = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "first_name": "Super",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )
    admin.password = make_password("admin")
    admin.save()
    return admin


def create_initial_site():
    Site.objects.get_or_create(
        name="demo",
        defaults={
            "slug": "demo",
        },
    )


class Command(BaseCommand):
    help = "Create initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dev",
            action="store_true",
            dest="dev",
            default=False,
            help="Also create dev seed data",
        )

    def handle(self, *args, **options):
        if options["dev"]:
            create_admin()
            create_initial_site()
        ensure_custom_fields_exist()
