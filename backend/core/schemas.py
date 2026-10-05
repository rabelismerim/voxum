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
from core.base_internal_user.schemas import GroupSchema, UserInternalSchema
from django.contrib.auth.models import Group
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from utils import get_user_model

from config.schemas import AbstractStatusSchema

from apps.voxum_base.utils import check_is_user_internal, check_is_user_guest


class UserInternalEditSchema(WritableNestedModelSerializer, AbstractStatusSchema):
    """
    Serializer for fields of the Group model.

    Attributes:
        groups (GroupSchema): Groups associated with the model. Read and write access.
    """
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'is_active', 'groups', 'status']


class VoxumGroupSchema(GroupSchema):
    class Meta:
        model = Group
        fields = ['name', 'permissions', 'id']
        extra_kwargs = {
            'name': {'validators': []},
        }


class CustomUserInternalSchema(UserInternalSchema):
    is_user_guest = serializers.SerializerMethodField(read_only=True)
    is_user_internal = serializers.SerializerMethodField(read_only=True)
    user_permissions = serializers.SerializerMethodField(read_only=True)

    def get_is_user_guest(self, obj):
        return check_is_user_guest(obj)

    def get_is_user_internal(self, obj):
        return check_is_user_internal(obj)

    def get_user_permissions(self, obj):
        return [
            {'codename': permission.rsplit('.', 1)[-1]}
            for permission in obj.get_all_permissions()
        ]

    class Meta(UserInternalSchema.Meta):
        fields = UserInternalSchema.Meta.fields + [
            'is_user_guest',
            'is_user_internal',
            'user_permissions',
        ]