from django.contrib.auth.models import Group
from rest_framework import serializers

from core.abstract.schemas import AbstractStatusSchema
from utils import get_user_model


class GroupSchema(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class UserInternalSchema(AbstractStatusSchema):
    groups = GroupSchema(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'status', 'userpicture', 'user_img', 'login_date', 'created_at',
            'updated_at', 'groups',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
