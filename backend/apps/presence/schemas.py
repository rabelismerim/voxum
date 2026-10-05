import datetime
import logging
import sys

from core.abstract.schemas import AbstractStatusSchema
from django.db.models import Q
from rest_framework import serializers, renderers
from rest_framework.exceptions import ValidationError
from utils import _

from apps.creditor.models import Creditor, Representative
from apps.meetings.models import RepresentativeMeeting
from apps.presence.models import Presence, PresenceRepresentative


class PresenceSchema(AbstractStatusSchema):
    creditor_id = serializers.UUIDField()
    accredited_by = serializers.IntegerField(source='accredited_by__get_full_name', read_only=True)

    class Meta:
        model = Presence
        exclude = ('creditor',)
        read_only_fields = (
            'is_present', 'is_accredited', 'accredited_by', 'accredited_date', 'arrival_date', 'departure_date',
            'departure_reason')

    def create(self, validated_data):
        date_now = datetime.datetime.now()
        validated_data['arrival_date'] = date_now
        validated_data['is_present'] = True
        validated_data['accredited_date'] = date_now
        validated_data['is_accredited'] = True

        presence = Presence.objects.filter(creditor_id=validated_data['creditor_id']).first()
        request = self.context.get('request')
        validated_data['accredited_by'] = request.user
        if presence:
            if presence.is_accredited:
                raise ValidationError(_('Presença já registrada'))
            presence.register_accreditation(request.user)
        else:
            presence = super().create(validated_data)
        return presence


class PresenceToRepresentativeSchema(AbstractStatusSchema):
    representative_id = serializers.UUIDField()

    class Meta:
        model = PresenceRepresentative
        exclude = ('representative',)
        read_only_fields = ('is_present', 'arrival_date', 'departure_date', 'departure_reason')

    def create(self, validated_data):
        validated_data['is_present'] = True
        validated_data['arrival_date'] = datetime.datetime.now()
        return super().create(validated_data)


class PresenceDetailSchema(AbstractStatusSchema):
    creditor_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Presence
        exclude = ('creditor',)
        non_required_fields = '__all__'


class PresenceArrivalSchema(AbstractStatusSchema):
    class Meta:
        model = Presence
        exclude = ('creditor',)
        read_only_fields = tuple(field.name for field in Presence._meta.fields)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.register_accreditation(user)
        return instance


class PresenceDepartureSchema(AbstractStatusSchema):
    class Meta:
        model = Presence
        exclude = ('creditor',)
        exclude_read_only_fields = ['departure_reason']

    def update(self, instance, validated_data):
        instance.register_departure_date(validated_data.get('departure_reason'))
        return instance


class PresenceResultsCreateSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
    presence_result = PresenceSchema(required=False, read_only=True)
    errors = serializers.ListField(child=serializers.CharField(), required=False, read_only=True)
    creditor_id = serializers.UUIDField(read_only=True)
    representative_id = serializers.UUIDField(read_only=True)
    presence_representative = PresenceToRepresentativeSchema(read_only=True, allow_null=True)


class PresenceGuestSchema(AbstractStatusSchema):
    result = PresenceResultsCreateSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Presence
        fields = '__all__'
        exclude_read_only_fields = ('creditor_id',)

    def create(self, validated_data):
        request = self.context.get('request')
        meeting_id = request.parser_context.get('kwargs').get('meeting_id')
        user = request.user
        presences = Presence.objects.all()
        creditor = Creditor.objects.filter(meeting_id=meeting_id, guest__user=user).first()
        if creditor:
            creditor.meeting.check_able_to_register_presence()
            validated_data['creditor'] = creditor
        callback = []

        representative = RepresentativeMeeting.objects.filter(meeting_id=meeting_id, guest__user=user).first()

        if creditor and not representative:
            presence = presences.filter(creditor=creditor).first()
            if presence:
                if presence.is_accredited:
                    raise ValidationError(_('Presença já registrada'))
                presence.register_accreditation(user)
                return presence

            presence = super().create(validated_data)
            presence.register_accreditation(user)

            return presence

        elif creditor:
            try:
                presence = presences.filter(creditor=creditor).first()
                if presence:
                    if presence.is_accredited:
                        raise ValidationError(_('Presença já registrada'))
                else:
                    presence = super().create(validated_data)
                presence.register_accreditation(user)
            except ValidationError as e:
                logging.error(e, exc_info=True)

        if representative:
            creditors = Creditor.objects.filter(meeting_id=meeting_id,
                                                representative__representative__guest__user=user).distinct()

            relations_representative_creditor = representative.representative_set.all()

            for relation_representative_creditor in relations_representative_creditor:
                presence_representative = PresenceRepresentative.objects.filter(
                    representative=relation_representative_creditor).first()

                presence_representative__payload = {
                    'is_present': True,
                    'arrival_date': datetime.datetime.now(),
                    'representative': relation_representative_creditor,
                }
                if not presence_representative:
                    presence_representative = PresenceRepresentative.objects.create(**presence_representative__payload)

                relation_representative_creditor.representative.register_accreditation(user)

            for creditor in creditors:
                creditor.meeting.check_able_to_register_presence()
                errors = []
                presence_obj = None

                try:
                    presence_obj = presences.filter(creditor=creditor).first()
                    if not presence_obj:
                        presence_obj = Presence.objects.create(creditor=creditor, is_accredited=False,
                                                               arrival_date=datetime.datetime.now())
                    else:
                        if presence_obj.is_accredited:
                            raise ValidationError(_('Presença já registrada'))
                    presence_obj.register_accreditation(user)

                except Exception as e:
                    logging.error(e, exc_info=True)
                    type_, value, traceback = sys.exc_info()

                    if type_ == ValidationError or isinstance(type_, ValidationError):
                        errors.extend(list(value.detail))
                    else:
                        errors.append(e)

                obj_callback = {
                    'creditor_id': creditor.id,
                }

                if not errors:
                    obj_callback['success'] = True
                    obj_callback['presence_result'] = PresenceSchema(presence_obj).data
                else:
                    obj_callback['success'] = False
                    obj_callback['errors'] = errors
                callback.append(obj_callback)

            return {
                'result': callback
            }

        raise ValidationError('Credor/representante não encontrado')


class PresenceRepresentativeSchema(serializers.Serializer):
    renderer_classes = [renderers.JSONRenderer]
    representative_id = serializers.UUIDField(write_only=True)
    result = PresenceResultsCreateSerializer(many=True, read_only=True)

    def create(self, validated_data):
        representatives_creditors = Representative.objects.filter(representative_id=validated_data['representative_id'])
        callback = []
        user = self.context['request'].user

        creditor_ids = representatives_creditors.values_list('creditor_id', flat=True)
        for creditor_id in creditor_ids:
            relation_representative_creditor = representatives_creditors.filter(
                creditor_id=creditor_id).first()
            errors = []
            presence_obj = None
            presence_representative = None

            if not relation_representative_creditor:
                errors.append(_('Relação entre representante e credor inválida'))
            else:
                creditor = relation_representative_creditor.creditor

                presence_representative = PresenceRepresentative.objects.filter(
                    representative=relation_representative_creditor).first()

                presence_representative__payload = {
                    'is_present': True,
                    'arrival_date': datetime.datetime.now(),
                    'representative': relation_representative_creditor,
                }
                if not presence_representative:
                    presence_representative = PresenceRepresentative.objects.create(**presence_representative__payload)

                try:
                    presence_obj = creditor.get_presence()
                    if not presence_obj:
                        presence_obj = Presence.objects.create(creditor=creditor)
                    presence_obj.register_accreditation(user)

                except Exception as e:
                    logging.error(e, exc_info=True)
                    type_, value, traceback = sys.exc_info()

                    if type_ == ValidationError or isinstance(type_, ValidationError):
                        errors.extend(list(value.detail))
                    else:
                        errors.append(e)

            relation_representative_creditor.representative.register_accreditation(user)

            obj_callback = {
                'creditor_id': creditor_id,
                'representative_id': validated_data['representative_id'],
                'presence_representative': presence_representative,
            }

            if not errors:
                obj_callback['success'] = True
                obj_callback['presence_result'] = PresenceSchema(presence_obj).data
            else:
                obj_callback['success'] = False
                obj_callback['errors'] = errors
            callback.append(obj_callback)

        return {
            'result': callback,
        }


class PresenceRepresentativeGuestSchema(PresenceRepresentativeSchema):
    def validate(self, attrs):
        user = self.context['request'].user

        # Validação genérica para administradores/consultores ou permissão direta do usuário guest
        from core.permissions.views import IsUserManagerOrConsultantPermission
        # Alternativamente, verificação limpa de permissão sem acoplamento à função legada
        is_manager_or_consultant = IsUserManagerOrConsultantPermission().has_permission(self.context.get('request'), None)

        if not is_manager_or_consultant:
            representative = RepresentativeMeeting.objects.filter(
                Q(id=attrs['representative_id']) | Q(representative__id=attrs['representative_id']),
                guest__user=user).exists()
            if not representative:
                raise ValidationError('Relação entre representante inválido')

        return super().validate(attrs)