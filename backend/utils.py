import secrets
from functools import wraps

from django.contrib.auth import get_user_model as django_get_user_model
from django.utils.translation import gettext_lazy


_ = gettext_lazy


def get_user_model():
    return django_get_user_model()


def secret_number(min_value, max_value):
    if min_value > max_value:
        raise ValueError('min_value must be less than or equal to max_value')
    return secrets.randbelow(max_value - min_value + 1) + min_value


def doc(description):
    def decorate(target):
        target.__doc__ = str(description)
        if isinstance(target, type):
            docs = dict(getattr(target, 'docs', {}))
            docs.setdefault('init', str(description))
            target.docs = docs
        return target

    return decorate
