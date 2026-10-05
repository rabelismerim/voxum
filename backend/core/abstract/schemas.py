from rest_framework import serializers


class AbstractModelSchema(serializers.ModelSerializer):
    def __init__(self, *args, exclude=(), **kwargs):
        self._dynamic_exclude = set((exclude,) if isinstance(exclude, str) else exclude)
        fields = kwargs.pop('fields', None)
        self._dynamic_fields = set((fields,) if isinstance(fields, str) else fields or ())
        super().__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def get_fields(self):
        fields = super().get_fields()
        if self._dynamic_fields:
            fields = {
                field_name: field
                for field_name, field in fields.items()
                if field_name in self._dynamic_fields
            }
        for field_name in self._dynamic_exclude:
            fields.pop(field_name, None)
        optional_fields = getattr(self.Meta, 'non_required_fields', ())
        if optional_fields == '__all__':
            optional_fields = fields
        for field_name in optional_fields:
            if field_name in fields:
                fields[field_name].required = False
        return fields


class AbstractDescriptionSchema(AbstractModelSchema):
    pass


class AbstractStatusSchema(AbstractModelSchema):
    pass


class SerializerMethodFieldChild(serializers.SerializerMethodField):
    def __init__(self, method_name=None, child=None, **kwargs):
        self.child = child
        super().__init__(method_name=method_name, **kwargs)

    def to_representation(self, value):
        result = super().to_representation(value)
        if result is None or self.child is None:
            return result
        return self.child.to_representation(result)
