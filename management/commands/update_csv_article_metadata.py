
import csv
import pprint
import uuid

from core.models import Account
from django.core.management.base import BaseCommand
from journal import models

from plugins.imports.utils import DummyRequest
from plugins.imports.utils import update_article_metadata
from plugins.imports.models import CSVImportCreateArticle, CSVImportUpdateArticle

class Command(BaseCommand):
    """ CLI interface for the CSV importer"""

    help = "CLI interface for the CSV importer"

    def add_arguments(self, parser):
        parser.add_argument('csv_file')
        parser.add_argument('--owner-id', default=1)

    def handle(self, *args, **options):
        owner = Account.objects.get(pk=options["owner_id"])

        with open(options["csv_file"], "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            rows, csv_import = update_article_metadata(
                reader,
                owner=owner,
                import_id=uuid.uuid4()
            )

            for row in rows:
                if row.get("error"):
                    self.stderr.write(f"Row failed: {row.error}\n{row.article}")

            created = CSVImportCreateArticle.objects.filter(csv_import=csv_import).all()
            total_created = created.count()
            if total_created > 0:
                self.stderr.write(f"The following {total_created} articles were created:")
                for c in created:
                    self.stderr.write(f"\t{c}")

            updated = CSVImportUpdateArticle.objects.filter(csv_import=csv_import).all()
            total_updated = updated.count()
            if total_updated > 0:
                self.stderr.write(f"The following {total_updated} articles were updated:")
                for u in updated:
                    self.stderr.write(f"\t{u}")
