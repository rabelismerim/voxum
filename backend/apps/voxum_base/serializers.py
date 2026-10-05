from core.abstract.exceptions import ValidationErrorAdapter  # Ajustado para core local
from drf_writable_nested import NestedUpdateMixin
from rest_framework import serializers
from typing import TypeVar

T = TypeVar('T', bound=serializers.ModelSerializer)


class GetOrCreateMixin:
    class Meta:
        model = None
        get_or_create_fields = []

    def create(self: T, validated_data):
        model_class = self.Meta.model
        field_names: list = getattr(self.Meta, 'get_or_create_fields', [])

        for field_name in field_names:
            if field_name in validated_data:
                instance, created = model_class.objects.get_or_create(
                    **{field_name: validated_data[field_name]}
                )
                if not created:
                    for attr, value in validated_data.items():
                        if attr != field_name:
                            setattr(instance, attr, value)
                    instance.save()
                    return instance

        return super().create(validated_data)


class CustomNestedUpdateMixin(NestedUpdateMixin):
    def _get_related_pk_instance(self, field_source, data, model_class):
        pk = data.get('pk') or data.get(model_class._meta.pk.attname)
        if pk:
            return str(pk)
        instance_related = getattr(self.instance, field_source)
        if instance_related:
            return instance_related.id
        return None

    def update_or_create_direct_relations(self, attrs, relations):
        for field_name, (field, field_source) in relations.items():
            obj = None
            data = self.get_initial()[field_name]
            model_class = field.Meta.model
            pk = self._get_related_pk_instance(field_source, data, model_class)
            if pk:
                obj = model_class.objects.filter(pk=pk).first()
            serializer = self._get_serializer_for_field(
                field,
                instance=obj,
                data=data,
            )

            try:
                serializer.is_valid(raise_exception=True)
                attrs[field_source] = serializer.save(
                    **self._get_save_kwargs(field_name)
                )
            except ValidationErrorAdapter as exc:
                raise ValidationErrorAdapter({field_name: exc.detail})