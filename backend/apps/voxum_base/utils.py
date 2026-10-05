import re
import logging
import secrets
import sys
import traceback
import functools

from datetime import datetime

from asgiref.sync import async_to_sync
from core.abstract.exceptions import ValidationErrorAdapter  # Ajustado para core local
from channels.layers import get_channel_layer
from django.contrib.auth.models import Group
from django.db import transaction
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from core.permissions.models import TypeGroupChoices, GroupUserGuest, TypeRolesChoices


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))
    return inner


def receiver_commit(*signal_args, **signal_kwargs):
    def decorator(func):
        @receiver(*signal_args, **signal_kwargs)
        def wrapper(*args, **kwargs):
            in_atomic_block = transaction.get_connection().in_atomic_block
            if in_atomic_block is False:
                func(*args, **kwargs)
            else:
                transaction.on_commit(lambda: func(*args, **kwargs))
        return wrapper
    return decorator


def get_new_code():
    return secrets.randbelow(900000) + 100000


def get_traceback_err(e) -> tuple:
    logging.error(e, exc_info=True)
    type_, value, e_traceback_str = sys.exc_info()
    traceback_str = traceback.format_exc()

    if hasattr(e, 'messages'):
        e = e.messages
    elif ((type_ == ValidationError or type_ == ValidationErrorAdapter) or isinstance(type_, (
            ValidationError, ValidationErrorAdapter))) and hasattr(e, 'get_full_details'):
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


def timeit(method):
    @functools.wraps(method)
    def timed(*args, **kwargs):
        start_time = datetime.now()
        class_name = ''
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__ + '.'

        method_name = f'{class_name}{method.__name__}'
        logging.info(f"Start time of {method_name}: {start_time}")

        result = method(*args, **kwargs)
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        elapsed_seconds = elapsed_time.total_seconds()

        logging.info(f"Execution of {method_name} took {elapsed_time}")
        logging.info(f"Execution of {method_name} took {elapsed_seconds:.4f} in seconds")
        return result
    return timed


def count_group_connections(group_name):
    channel_layer = get_channel_layer()
    if hasattr(channel_layer, 'count_group_connections'):
        return async_to_sync(channel_layer.count_group_connections)(group_name)
    groups = getattr(channel_layer, 'groups', None)
    if groups is None:
        raise RuntimeError('The configured channel layer cannot count group connections.')
    return len(groups.get(group_name, {}))


def check_is_user_guest(user):
    return user.groups.filter(name=GroupUserGuest).exists()


def get_user_privileged_group_names():
    return [TypeGroupChoices.CONSULTANT.label, TypeGroupChoices.MANAGER.label, TypeRolesChoices.ADMIN.label]


def get_user_internal_group_names():
    return get_user_privileged_group_names()


def check_is_user_internal(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.groups.filter(name__in=get_user_internal_group_names()).exists()


def check_is_user_privileged(user):
    return user.groups.filter(name__in=get_user_privileged_group_names()).exists()


def get_privileged_groups():
    return Group.objects.filter(name__in=get_user_privileged_group_names())


def is_valid_cpf(cpf):
    if not cpf:
        return False
    cpf = ''.join(re.findall(r'\d', str(cpf))).zfill(11)
    int_cpf = [int(x) for x in cpf]
    new = int_cpf[:9]
    while len(new) < 11:
        r = sum([(len(new) + 1 - i) * v for i, v in enumerate(new)]) % 11
        f = (11 - r) if r > 1 else 0
        new.append(f)
        if new == int_cpf:
            return True
    return False


def is_valid_cnpj(cnpj):
    if not cnpj:
        return False
    cnpj = ''.join(re.findall(r'\d', str(cnpj))).zfill(14)
    int_cnpj = [int(x) for x in cnpj]
    new = int_cnpj[:12]
    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(new) < 14:
        r = sum([x * y for (x, y) in zip(new, prod)]) % 11
        f = (11 - r) if r > 1 else 0
        new.append(f)
        prod.insert(0, 6)
        if new == int_cnpj:
            return True
    return False


def get_legal_number(legal_number):
    legal_number = ''.join(re.findall(r'\d', str(legal_number)))
    if not is_valid_cpf(legal_number):
        if is_valid_cnpj(legal_number):
            return legal_number.zfill(14)
    return legal_number.zfill(11)


def get_classe_format(classe):
    return str(classe).upper()