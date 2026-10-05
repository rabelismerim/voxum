"""
Serializes the fields of the Recovering model for use in the API.
"""
from core.abstract.schemas import AbstractDescriptionSchema

from apps.recovering.models import Recovering


class RecoveringSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Recovering model for use in the API.
    """

    class Meta:
        model = Recovering
        fields = '__all__'