import hashlib

from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer, NestedUpdateMixin
from utils import get_user_model

from apps.voxum_base.schemas import EntitySchema
from apps.voxum_base.serializers import CustomNestedUpdateMixin
from apps.guest.models import UserGuest
from core.abstract.schemas import AbstractDescriptionSchema, AbstractStatusSchema

User = get_user_model()

user_fields_exclude = ["password", "last_login", "is_superuser", "is_staff", "date_joined", "userpicture",
                       "user_img", "login_date", "groups", "user_permissions"]


def generate_unique_number(legal_number):
    """
        Generates a unique number based on the MD5 hash of the input.
   """
    sha256_hash = hashlib.sha256(str(legal_number).strip().encode()).hexdigest()
    return int(sha256_hash[-5:], 16)


class UserSchema(AbstractStatusSchema):
    default_validators = []
    validators = []

    class Meta:
        model = User
        exclude = user_fields_exclude
        read_only_fields = ("is_active", 'status')
        write_only_fields = ('username',)
        extra_kwargs = {
            'email': {
                'validators': []
            },
            'username': {
                'required': False,
            }
        }

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data.get('username')

        if not username:
            username = email.split('@')
            username = f'{username[0]}_{username[1].split(".")[0]}'
            validated_data['username'] = username
        if email:
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.filter(username=username).first()

        if user:
            if not email:
                validated_data.pop('email', None)
            user = user.dict_update(**validated_data)
            return user
        return super().create(validated_data)


class UserDetailSchema(AbstractStatusSchema):
    default_validators = []
    validators = []

    class Meta:
        model = User
        exclude = user_fields_exclude
        read_only_fields = ("is_active", 'status')
        non_required_fields = '__all__'


class UserGuestSchema(WritableNestedModelSerializer, AbstractDescriptionSchema):
    user = UserSchema()
    entity = EntitySchema()
    user_ciam = serializers.JSONField(read_only=True, allow_null=True, required=False)

    class Meta:
        model = UserGuest
        fields = '__all__'


class UserGuestUpdateSchema(NestedUpdateMixin, AbstractDescriptionSchema):
    user = UserSchema(read_only=True)
    entity = EntitySchema(read_only=True)
    # user_ciam = serializers.JSONField(read_only=True, allow_null=True, required=False)

    class Meta:
        model = UserGuest
        fields = '__all__'


class UserGuestDetailSchema(CustomNestedUpdateMixin, AbstractDescriptionSchema):
    user = UserDetailSchema(required=False)
    entity = EntitySchema(required=False)
    # user_ciam = serializers.JSONField(read_only=True, allow_null=True, required=False)

    class Meta:
        model = UserGuest
        fields = '__all__'
        non_required_fields = '__all__'


class UserGuestCiamSchema(serializers.Serializer):
    status = serializers.IntegerField(read_only=True)
    success = serializers.BooleanField(read_only=True)
    data = serializers.DictField(read_only=True)