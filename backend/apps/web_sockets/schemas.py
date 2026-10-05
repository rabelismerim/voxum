from rest_framework import serializers

from rest_framework.serializers import SerializerMethodField
from apps.voxum_base.views_sockets import Schema

fields = Schema.get_schemas()


class SocketsSchema(serializers.Serializer):
    """Serializer Creditor fields"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in fields:
            # Utilizando SerializerMethodField e associando o serializer correspondente
            serializer_instance = field['serializer'](read_only=True, many=field['many'])
            field_name = field['channel']

            # Cria o campo dinamicamente mantendo a compatibilidade
            self.fields[field_name] = SerializerMethodField()
            setattr(self, f'get_{field_name}', lambda obj, s=serializer_instance: s.to_representation(obj))

    class Meta:
        fields = '__all__'