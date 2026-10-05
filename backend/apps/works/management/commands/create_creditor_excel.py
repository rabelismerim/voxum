import json
import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.voxum_base.models import Worker, GenericFieldChoices, GenericField, GenericModelPath

from apps.works.models import CreditorTitle


class Command(BaseCommand):
    help = 'Criar ou atualizar o Excel de credores'
    path = 'meeting_creditors'
    excel_name = 'massive_create_creditors'

    def create_upload_path(self):
        meeting_content_object = ContentType.objects.get(app_label="meeting", model="meeting")

        GenericModelPath.objects.get_or_create(
            content_object=meeting_content_object,
            path=self.path
        )

    def handle(self, *args, **options):
        self.create_upload_path()

        columns = CreditorTitle.columns

        fields = []
        fields_options = []
        fields_created = []
        fields_updated = []

        for field in columns:
            title = str(field['title'])
            if field['choice']:

                if callable(field['choice']):
                    field_choices = field['choice']()
                else:
                    field_choices = field['choice']

                options = json.loads(json.dumps(field_choices, default=str))  # Remove __proxy__ get_text_lazy
                new_field_choices, created = GenericFieldChoices.objects.get_or_create(name=title, options=options)
                fields_options.append(new_field_choices.id)
            else:
                example = field.get('example')
                has_example = example is not None
                new_field, created = GenericField.objects.get_or_create(name=title, field_type='CharField',
                                                                        example=example, has_example=has_example)
                fields.append(new_field.id)
                if created:
                    fields_created.append(new_field)
                else:
                    fields_updated.append(new_field)

        worker, created = Worker.objects.get_or_create(name=self.excel_name)
        worker.fields.clear()
        worker.fields_opts.clear()

        worker.fields.add(*fields)
        worker.fields_opts.add(*fields_options)

        total_created = len(fields_created)
        total_updated = len(fields_updated)
        logging.debug(f'Successful {"created" if created else "updated"} worker {worker}')
        logging.debug(f'Successful created {total_created} fields')
        logging.debug(f'Successful updated {total_updated} fields')