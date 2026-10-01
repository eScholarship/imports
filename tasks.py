import csv

from django.conf import settings
from django.utils import translation
from django.template.loader import render_to_string

from utils.notify_plugins.notify_email import send_email

from journal.models import Journal

from plugins.imports import utils
from plugins.imports.models import CSVImportCreateArticle, CSVImportUpdateArticle

def update_article_metadata(journal_code, csv_path, folder_path, owner, filename):
    file = open(csv_path, 'r', encoding="utf-8-sig")
    reader = csv.DictReader(file)

    with translation.override(settings.LANGUAGE_CODE):
        journal = Journal.objects.get(code=journal_code)
        errors, csv_import = utils.update_article_metadata(
            reader,
            folder_path,
            owner=owner,
            import_id=filename,
        )
        body = render_to_string(
            "import/import_complete.html",
            {
                "errors": errors,
                "created": CSVImportCreateArticle.objects.filter(csv_import=csv_import).all(),
                "updated": CSVImportUpdateArticle.objects.filter(csv_import=csv_import).all()
            },
        )

        send_email("Import Complete", owner.email, body, journal, None)

def import_supp_files(journal_code, csv_path, owner):
    with open(csv_path, 'r', encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        journal = Journal.objects.get(code=journal_code)
        errors, error_file = utils.import_supp_files(reader)

        body = render_to_string(
            "import/supp_files_import_complete.html",
            {
                "errors": errors,
                "error_file": error_file,
                "site_url": journal.site_url()
            },
        )

        send_email("Supplementary File Import Complete", owner.email, body, journal, None)
