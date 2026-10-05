from rest_framework.exceptions import ValidationError


class ValidationErrorAdapter(ValidationError):
    pass
