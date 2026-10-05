"""
Serializes the fields of the Home model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Home` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from apps.location.models import Location
from core.abstract.schemas import AbstractDescriptionSchema


class LocationSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Home model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Home
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = LocationSchema()
    """

    class Meta:
        model = Location
        fields = '__all__'