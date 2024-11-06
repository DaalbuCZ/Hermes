from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Create a new TestResult database for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "db_name", type=str, help="The name of the new TestResult database"
        )

    def handle(self, *args, **kwargs):
        db_name = kwargs["db_name"]
        db_path = os.path.join(settings.BASE_DIR, f"{db_name}.sqlite3")
        if not os.path.exists(db_path):
            with open(db_path, "w"):
                pass
            self.stdout.write(
                self.style.SUCCESS(
                    f"TestResult database {db_name} created successfully"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"TestResult database {db_name} already exists")
            )
