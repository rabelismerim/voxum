import logging
import re
import sys
import traceback

from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.voxum_base.models import ExcelWorker, ErrorFile
from rest_framework.exceptions import ValidationError
from utils import _

from apps.voxum_base.models import CHOICES_COIN
from apps.voxum_base.schemas import CoinSchema, EntitySchema
from apps.voxum_base.utils import get_legal_number
from apps.creditor.models import CHOICES_TYPE_PERSON, Creditor, Representative, get_new_creditor_code
from apps.creditor.schemas import MassiveCreditorSchema, RepresentativeSchema
from apps.guest.models import MsalGuestStatusChoices, UserGuest
from apps.guest.schemas import UserGuestSchema, generate_unique_number, UserGuestUpdateSchema, UserSchema
from apps.meetings.models import Meeting, Classe, RepresentativeMeeting, get_new_representative_code
from apps.recovering.models import Recovering
from apps.web_sockets.signals import signal_meeting_detail, update_creditor_list


class ParseTitleMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls.columns = []

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, str) and not attr_name.startswith('__'):
                new_cls.columns.append(
                    {"title": attr_value, 'choice': new_cls.get_choices(attr_value), 'default': None, 'type': 'str',
                     'example': new_cls.get_examples(attr_value)})

        return new_cls


class ParseTitle(metaclass=ParseTitleMeta):
    choices = {}
    examples = {}

    @classmethod
    def get_choices(cls, title):
        return cls.choices.get(title, None)

    @classmethod
    def get_examples(cls, title):
        return cls.examples.get(title, None)

    @classmethod
    def get_subclasses(cls):
        """
        Get the subclasses of the Schema class.

        Returns:
            list: List of subclasses.
        """
        return cls.__subclasses__()


def get_username(first_name, last_name, legal_number):
    return f'{first_name}_{generate_unique_number(legal_number)}_{legal_number[:4]}_{last_name}'[
           :150].replace(' ', '').lower()


def get_classes_choices():
    return list(Classe.objects.all().values_list('id', 'description'))


def validate_credit_value(value):
    try:
        value = re.sub(r'[^0-9,.]', '', str(value))
        return float(value.replace('.', '').replace(',', '.'))
    except ValueError:
        raise ValueError(f"O valor '{value}' não é válido para o campo Valor.")


class CreditorTitle(ParseTitle):
    creditor = 'CREDOR'
    creditor_email = 'CREDOR EMAIL[OPCIONAL]'
    creditor_cpf_cnpj = 'CREDOR CPF/CNPJ'
    representative = 'REPRESENTANTE[OPCIONAL]'
    representative_email = 'REPRESENTANTE EMAIL'
    representative_cpf_cnpj = 'REPRESENTANTE CPF/CNPJ'
    type_person = 'TIPO DE PESSOA'
    value = 'VALOR'
    recovering = 'EMPRESA DEVEDORA'
    coin = 'MOEDA'
    classe = 'CLASSE'
    doc_ok = 'DOCUMENTOS OK'
    representative_doc_ok = 'DOCUMENTOS REPRESENTANTE OK'
    choices = {
        coin: CHOICES_COIN,
        type_person: CHOICES_TYPE_PERSON,
        classe: get_classes_choices,
    }
    examples = {
        creditor: 'Nome do credor',
        creditor_email: 'email_credor@emailexterno.com',
        creditor_cpf_cnpj: '123.456.789-01',
        representative: 'Nome do representante',
        representative_email: 'email_representante@emailexterno.com',
        representative_cpf_cnpj: '123.456.789-02',
        value: '123.456,00',
        recovering: 'Nome da recuperanda',
        doc_ok: True,
        representative_doc_ok: True,
    }

    classes = Classe.objects.all()
    recoveries = Recovering.objects.all()
    users_guest = UserGuest.objects.all()
    representatives = RepresentativeMeeting.objects.all()
    creditors = Creditor.objects_admin.all()
    codes = creditors.values_list('code', flat=True)
    representative_codes = representatives.values_list('code', flat=True)

    def __init__(self):
        self.new_codes = []
        self.new_representative_codes = []
        self.registered_emails = []

    @classmethod
    def get_content_model(cls):
        return Meeting

    def get_classe_id(self, creditor_data):
        cred_value = CreditorValue(creditor_data)
        classe = cred_value.creditor_classe
        obj_classe = self.classes.filter(id=classe).first()
        if not obj_classe:
            raise ValidationError(_('Classe invalida'))
        return obj_classe.id

    def get_recovering_id(self, creditor_data):
        recovering = creditor_data[CreditorTitle.recovering].strip().title()
        obj_recovering = self.recoveries.filter(name=recovering).first()
        if not obj_recovering:
            obj_recovering = Recovering.objects.create(name=recovering)
        return obj_recovering.id

    def get_guest_id(self, creditor_data, meeting_id):
        cred_value = CreditorValue(creditor_data)
        creditor = cred_value.creditor
        creditor_email = cred_value.creditor_email
        creditor_cpf_cnpj = cred_value.creditor_cpf_cnpj

        if not creditor:
            raise ValidationError(_('Nome do credor não pode ser nulo'))
        if len(creditor) == 1:
            raise ValidationError(_('Nome do credor deve conter nome e sobrenome'))
        if not creditor_cpf_cnpj:
            raise ValidationError(_('CPF/CNPJ do credor não pode ser nulo'))

        creditor_cpf_cnpj = get_legal_number(creditor_cpf_cnpj)

        creditor_full_name = creditor
        first_name = creditor_full_name[0]
        last_name = ' '.join(creditor_full_name[1:])

        if creditor_email is not None and creditor_email:
            creditor_email = creditor_email.strip().lower()
        else:
            creditor_email = ''

        user_guest = self.users_guest.filter(entity__legal_number=creditor_cpf_cnpj).first()

        username = get_username(first_name, last_name, creditor_cpf_cnpj)

        guest_payload = {
            "user": {
                "first_name": first_name,
                "last_name": last_name,
                "email": creditor_email,
                "username": username,
                "status": 'A',
            },
            "entity": {
                "legal_number": creditor_cpf_cnpj
            },
            "is_representative": False
        }

        return self.get_create_user_guest(user_guest, guest_payload, meeting_id)

    def get_create_user_guest(self, user_guest, guest_payload, meeting_id):
        if user_guest:
            current_email = user_guest.user.email
            user_schema_data = guest_payload.pop('user')
            entity_data = guest_payload.pop('entity')
            guest_payload.pop('is_representative')

            user_update = UserSchema(instance=user_guest.user, data=user_schema_data, partial=True)
            user_update.is_valid()
            user_update.save()

            entity_serializer = EntitySchema(instance=user_guest.entity, data=entity_data, partial=True)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()

            guest_serializer = UserGuestUpdateSchema(instance=user_guest, data=guest_payload)
            guest_serializer.is_valid(raise_exception=True)
            guest = guest_serializer.save()

            if current_email != user_schema_data['email']:
                msal_user = getattr(user_guest, 'msaluserguest', None)

                if msal_user:
                    msal_user.status = MsalGuestStatusChoices.IN_LINE
                    msal_user.save()

                creditor = user_guest.creditor_set.filter(meeting__id=meeting_id).first()

                if creditor:
                    creditor.reset_meeting_invite()

            return guest.id

        guest_serializer = UserGuestSchema(data=guest_payload)
        guest_serializer.is_valid(raise_exception=True)
        guest = guest_serializer.save()
        return guest.id

    def get_representative_id(self, creditor_data, meeting_id):
        representative = creditor_data[CreditorTitle.representative]
        representative_email = creditor_data[CreditorTitle.representative_email]
        representative_cpf_cnpj = creditor_data[CreditorTitle.representative_cpf_cnpj]

        if any([representative, representative_email, representative_cpf_cnpj]) is False:
            return

        if not representative:
            raise ValidationError(_('Nome do representante não pode ser nulo'))
        if len(representative.split(' ')) == 1:
            raise ValidationError(_('Nome do representante deve conter nome e sobrenome'))
        if not representative_email:
            raise ValidationError(_('Email do representante não pode ser nulo'))
        if not representative_cpf_cnpj:
            raise ValidationError(_('CPF/CNPJ do representante não pode ser nulo'))

        representative_email = representative_email.strip().lower()
        representative_cpf_cnpj = get_legal_number(representative_cpf_cnpj)

        user_guest = self.users_guest.filter(entity__legal_number=representative_cpf_cnpj).first()
        representative_code = self.get_representative_code(representative_cpf_cnpj)
        representative_full_name = representative.strip().title().split()
        first_name = representative_full_name[0]
        last_name = ' '.join(representative_full_name[1:])
        username = get_username(first_name, last_name, representative_cpf_cnpj)

        guest_payload = {
            "user": {
                "first_name": first_name,
                "last_name": last_name,
                "email": representative_email,
                "username": username,
                "status": 'A',
            },
            "entity": {
                "legal_number": representative_cpf_cnpj
            },

            "is_representative": True
        }
        guest_id = self.get_create_user_guest(user_guest, guest_payload, meeting_id)

        new_representative = \
            RepresentativeMeeting.objects.update_or_create(guest_id=guest_id, meeting_id=meeting_id,
                                                           defaults={"doc_ok": self.get_boolean(
                                                               creditor_data.get(CreditorTitle.representative_doc_ok,
                                                                                 False)), 'code': representative_code})[
                0]
        return new_representative.id

    def get_coin(self, creditor_data):
        coin_payload = {
            "type": creditor_data[CreditorTitle.coin].strip()
        }

        coin_serializer = CoinSchema(data=coin_payload)
        coin_serializer.is_valid(raise_exception=True)
        coin = coin_serializer.save()
        return coin.id

    def get_traceback_err(self, e) -> tuple:
        logging.error(e, exc_info=True)
        type_, value, e_traceback_str = sys.exc_info()

        traceback_str = traceback.format_exc()

        if hasattr(e, 'messages'):
            e = e.messages
        elif (type_ == ValidationError or isinstance(type_, ValidationError)) and hasattr(e, 'get_full_details'):
            def get_error_message(values):
                messages = []

                def extract_messages(message_values):
                    if isinstance(message_values, dict):
                        for key, val in message_values.items():
                            if isinstance(val, dict) and 'message' in val:
                                messages.extend(val['message'])
                            else:
                                extract_messages(val)
                    elif isinstance(message_values, list):
                        messages.extend([msg['message'] for msg in message_values])

                extract_messages(values)
                return ', '.join(messages)

            e = get_error_message(e.get_full_details())

        return traceback_str, e

    def get_code(self, additional_legal_number=None):
        retries = 5
        for i in range(retries):
            code = get_new_creditor_code()

            if additional_legal_number:
                code = f'{code}{generate_unique_number(get_legal_number(additional_legal_number))}'

            if code not in self.codes and code not in self.new_codes:
                self.new_codes.append(code)
                return code

        raise ValidationError(_('Falha ao gerar código para o Credor'))

    def get_representative_code(self, additional_legal_number=None):
        retries = 5
        for i in range(retries):
            code = get_new_representative_code()

            if additional_legal_number:
                code = f'{code}{generate_unique_number(get_legal_number(additional_legal_number))}'

            if code not in self.representative_codes and code not in self.new_representative_codes:
                self.new_representative_codes.append(code)
                return code

        raise ValidationError(_('Falha ao gerar código para o Representante'))

    @staticmethod
    def get_boolean(value):
        if value is None:
            return False
        return str(value).lower() in ['true', 'verdadeiro', '1', 'sim', 'yes', 'y', 'ok', '1.0']

    def update_or_create_creditor(self, creditor_data, meeting_id, representatives):
        creditor_cpf_cnpj = get_legal_number(creditor_data[CreditorTitle.creditor_cpf_cnpj])
        classe_id = self.get_classe_id(creditor_data)
        existing_creditor = self.creditors.filter(guest__entity__legal_number=creditor_cpf_cnpj, meeting_id=meeting_id,
                                                  classe_id=classe_id).first()

        guest_id = self.get_guest_id(creditor_data, meeting_id)
        coin_id = self.get_coin(creditor_data)

        creditor_payload = {
            "guest_id": guest_id,
            "meeting_id": meeting_id,
            "classe_id": classe_id,
            "recovering_id": self.get_recovering_id(creditor_data),
            "coin_id": coin_id,
            "type_person": creditor_data[CreditorTitle.type_person].strip(),
            "credit_value": validate_credit_value(creditor_data[CreditorTitle.value]),
            "code": self.get_code(creditor_cpf_cnpj),
            "representatives": representatives,
            "doc_ok": self.get_boolean(creditor_data.get(CreditorTitle.doc_ok, False)),
        }

        creditor = MassiveCreditorSchema(data=creditor_payload)
        creditor.is_valid(raise_exception=True)

        representatives = creditor.validated_data.pop('representatives', [])
        creditor_payload.pop('representatives', [])

        if existing_creditor:
            for key, value in creditor_payload.items():
                setattr(existing_creditor, key, value)
            return representatives, existing_creditor, False

        return representatives, Creditor(**creditor.validated_data), True

    def process_callback(self, data, *args, **kwargs):
        meeting_id = kwargs['object_id']
        file_id = kwargs['instance_id']
        errors_bulk = []
        creditors_bulk = []
        creditors_update_bulk = []
        creditors_representative_list = []
        creditors_representative_bulk = []
        fields_bulk_update = ['recovering_id', 'coin_id', 'type_person', 'credit_value', 'code', 'doc_ok']

        user_guest_group = Group.objects.get_or_create(name='User Guest')[0]

        if not data or (len(data) == 1 and data[0][CreditorTitle.creditor] is None):
            errors_bulk.append(
                ErrorFile(file_id=file_id, error='line:0, Lista de credores enviado pelo Excel vazia', status='P'))

        else:
            creditor_payload_data = {}
            with transaction.atomic():
                for creditor_data in data:
                    representatives = []
                    try:
                        representative_id = self.get_representative_id(creditor_data, meeting_id)

                        if representative_id:
                            if creditor_data[CreditorTitle.representative_cpf_cnpj] == creditor_data[
                                CreditorTitle.creditor_cpf_cnpj]:
                                raise ValidationError(_('O Usuário convidado não pode ser representante dele mesmo'))

                            representatives.append(
                                {
                                    "representative_id": representative_id,
                                    "priority": 0,
                                }
                            )

                        creditor_legal_number = creditor_data[CreditorTitle.creditor_cpf_cnpj]
                        list_representatives, new_creditor, created = self.update_or_create_creditor(creditor_data,
                                                                                                     meeting_id,
                                                                                                     representatives)

                        creditor_payload_data[str(new_creditor.id)] = creditor_data
                        if created:
                            creditors_bulk.append(new_creditor)
                        else:
                            creditors_update_bulk.append(new_creditor)

                        creditor_payload_data[str(new_creditor.id)] = creditor_data

                        if list_representatives:
                            creditors_representative_list.append((new_creditor, list_representatives))


                    except Exception as e:
                        traceback_str, err = self.get_traceback_err(e)
                        errors_bulk.append(
                            ErrorFile(file_id=file_id, error=f'line:{creditor_data["INDEX"]}, {err}',
                                      data=creditor_data, status='P',
                                      traceback=traceback_str))

                if not errors_bulk:
                    try:
                        Creditor.objects.bulk_create(creditors_bulk, ignore_conflicts=True)
                        ignored_creditors_bulk = creditors_bulk
                        for count in range(5):
                            new_creditors_bulk = []
                            for creditor_bulk in ignored_creditors_bulk:
                                has_creditor = self.creditors.filter(id=creditor_bulk.id).exists()
                                if not has_creditor:
                                    creditor_bulk.code = self.get_code(creditor_legal_number)

                                    new_creditors_bulk.append(creditor_bulk)
                            ignored_creditors_bulk = new_creditors_bulk

                            if new_creditors_bulk:
                                Creditor.objects.bulk_create(new_creditors_bulk, ignore_conflicts=True)
                            else:
                                break

                        if ignored_creditors_bulk:
                            Creditor.objects.bulk_create(ignored_creditors_bulk)

                        Creditor.objects.bulk_update(creditors_update_bulk, fields=fields_bulk_update)
                        ignored_creditors_bulk = creditors_update_bulk
                        for count in range(5):
                            new_creditors_bulk = []
                            for creditor_bulk in ignored_creditors_bulk:
                                has_creditor = self.creditors.filter(id=creditor_bulk.id).exists()
                                if not has_creditor:
                                    creditor_bulk.code = self.get_code(creditor_legal_number)

                                    new_creditors_bulk.append(creditor_bulk)
                            ignored_creditors_bulk = new_creditors_bulk

                            if new_creditors_bulk:
                                Creditor.objects.bulk_update(new_creditors_bulk, fields=fields_bulk_update)
                            else:
                                break

                        if ignored_creditors_bulk:
                            Creditor.objects.bulk_update(ignored_creditors_bulk)

                        for creditor in creditors_bulk:
                            creditor.guest.user.groups.add(user_guest_group)

                        for creditor, representatives in creditors_representative_list:
                            ids = [representative.get('id') for representative in representatives if
                                   representative.get('id')]
                            creditor.representatives.exclude(id__in=ids).delete()
                            for representative in representatives:
                                new_representative = RepresentativeSchema(data=representative)
                                new_representative.is_valid(raise_exception=True)
                                representative_guest = Representative(creditor=creditor,
                                                                      **new_representative.validated_data)
                                creditors_representative_bulk.append(representative_guest)
                                representative_guest.representative.guest.user.groups.add(user_guest_group)

                        Representative.objects.bulk_create(creditors_representative_bulk)

                    except Exception as e:
                        traceback_str, err = self.get_traceback_err(e)

                        count_duplicates = str(e).count('creditor_creditor_meeting_id_guest_id_classe_id')

                        payload = creditor_data
                        error = err
                        if count_duplicates > 0:
                            creditors_erros = self.get_creditors_erros(creditors_bulk, e)

                            if creditors_erros:
                                for creditor_err in creditors_erros:

                                    payload = creditor_payload_data.get(str(creditor_err.id))

                                    if payload:
                                        cred_value = CreditorValue(payload)
                                        creditor_full_name = cred_value.creditor_full_name
                                        creditor_email = cred_value.creditor_email
                                        creditor_cpf_cnpj = cred_value.creditor_cpf_cnpj
                                        creditor_classe = cred_value.creditor_classe

                                        error = (
                                            f'line:{payload["INDEX"]}, credor "{creditor_full_name}"'
                                            f'{creditor_email or "email não informado"}/'
                                            f'"{creditor_cpf_cnpj}" já registrado na classe "{creditor_classe}"')
                                    else:
                                        error = 'Existe credores duplicados para registro'

                                    errors_bulk.append(
                                        ErrorFile(file_id=file_id, error=error, data=payload, status='P',
                                                  traceback=traceback_str))
                            else:
                                error = 'Existe credores duplicados para registro'

                                errors_bulk.append(
                                    ErrorFile(file_id=file_id, error=error, data=payload, status='P',
                                              traceback=traceback_str))
                        else:
                            errors_bulk.append(
                                ErrorFile(file_id=file_id, error=error, data=payload, status='P',
                                          traceback=traceback_str))
                if errors_bulk:
                    transaction.set_rollback(True)

        if errors_bulk:
            ErrorFile.objects.bulk_create(errors_bulk)
            raise ValidationError('Erro ao subir credores em massa')

        if creditors_bulk or creditors_update_bulk:
            instance = creditors_bulk[0] if creditors_bulk else creditors_update_bulk[0]
            update_creditor_list.send(instance=instance, sender=Creditor)
            signal_meeting_detail.send(instance=instance.meeting, sender=Meeting)
        return data

    def get_creditors_erros(self, creditors_bulk, err):
        string_err = 'Key (meeting_id, guest_id, classe_id)=('
        string_err_pt = 'Chave (meeting_id, guest_id, classe_id)=('
        string_errs = str(err).split(string_err if str(err).count(string_err) > 0 else string_err_pt)
        creditors_bulk_err = []

        try:
            text_already_exists = ') already exists.' if string_errs[1].count(
                ') already exists.') > 0 else ') já existe.'
            cleaned_string_errs = string_errs[1].replace(text_already_exists, '').strip().split(',')
            meeting_id, guest_id, classe_id = cleaned_string_errs
        except IndexError:
            return creditors_bulk_err

        for creditor in creditors_bulk:
            if str(creditor.meeting_id) == meeting_id.strip() and str(creditor.guest_id) == guest_id.strip() and str(
                    creditor.classe_id) == classe_id.strip():
                creditors_bulk_err.append(creditor)

        return creditors_bulk_err


class CreditorValue:

    def __init__(self, creditor_data):
        self.creditor_data = creditor_data

    @property
    def creditor(self):
        creditor = self.creditor_data[CreditorTitle.creditor]
        if creditor:
            return creditor.strip().title().split()

    @property
    def creditor_full_name(self):
        creditor = self.creditor_data[CreditorTitle.creditor]
        if creditor:
            return creditor.strip().title()

    @property
    def creditor_email(self):
        email = self.creditor_data[CreditorTitle.creditor_email]
        if email:
            return email.strip().lower()

    @property
    def creditor_cpf_cnpj(self):
        creditor_cpf_cnpj = self.creditor_data[CreditorTitle.creditor_cpf_cnpj]
        if creditor_cpf_cnpj:
            return str(creditor_cpf_cnpj).strip().title()

    @property
    def creditor_classe(self):
        creditor_classe = self.creditor_data[CreditorTitle.classe]
        if creditor_classe:
            return creditor_classe.strip()


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner


@receiver(post_save, sender=ExcelWorker)
@on_transaction_commit
def start_callback_worker(sender, instance, created, **kwargs):
    for sub in ParseTitle.get_subclasses():
        obj = sub.get_content_model()
        is_instance_of = instance.content_type.model_class() == obj
        if is_instance_of:
            instance.process(callback=sub().process_callback)
            break