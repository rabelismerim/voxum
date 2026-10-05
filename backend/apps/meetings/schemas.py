"""
Módulo de Serializadores (Schemas) para o app Meeting.
"""
from core.abstract.exceptions import ValidationErrorAdapter
from core.abstract.schemas import AbstractModelSchema
from django.contrib.auth.models import Group, Permission
from drf_writable_nested import WritableNestedModelSerializer

from utils import _

from apps.voxum_base.models import CHOICES_COIN
from apps.creditor.models import CHOICES_TYPE_PERSON
from apps.guest.models import UserGuest
from apps.guest.schemas import UserGuestSchema
from apps.location.schemas import LocationSchema
from apps.meetings.models import (
    Meeting, Classe, RepresentativeMeeting, UserMeeting, MeetingGroup,
    StatusMeetingChoices, StatusQuorum, SituationMeetingChoices
)
from core.abstract.schemas import AbstractStatusSchema, AbstractDescriptionSchema
from rest_framework import serializers

from apps.presence.schemas import PresenceToRepresentativeSchema
from apps.report.models import ReportMeetingChoices, ReportVotingChoices
from apps.voting.models import StatusVotingChoice, VotedByChoices
from core.base_internal_user.models import STATUS_CHOICES


class ClasseSchema(AbstractDescriptionSchema):
    class Meta:
        model = Classe
        fields = '__all__'


class RepresentativeBigNumberSchema(serializers.Serializer):
    count_voters = serializers.IntegerField(read_only=True)
    count_not_voted = serializers.IntegerField(read_only=True)
    total_credit_value = serializers.FloatField(read_only=True)
    total_voters_credit_value = serializers.FloatField(read_only=True)
    percentage_voters = serializers.FloatField(read_only=True)
    total_percentage_voters = serializers.FloatField(read_only=True)


class RepresentativeMeetingSchema(AbstractDescriptionSchema):
    meeting_id = serializers.UUIDField()
    guest = UserGuestSchema(read_only=True)
    guest_id = serializers.UUIDField(write_only=True)
    has_presence = serializers.BooleanField(read_only=True)
    all_creditors_accredited = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        guest_id = attrs['guest_id']
        if UserGuest.objects.filter(is_representative=False, id=guest_id).exists():
            raise ValidationErrorAdapter(_('O Usuário não é um representante.'))

        if RepresentativeMeeting.objects.filter(guest_id=guest_id, meeting_id=attrs['meeting_id']).exists():
            raise ValidationErrorAdapter(_('Representante já cadastrado nessa Assembleia.'))

        return attrs

    class Meta:
        model = RepresentativeMeeting
        exclude = ('meeting',)


class RepresentativeMeetingBigNumberSchema(RepresentativeMeetingSchema):
    big_numbers = serializers.JSONField(read_only=True, allow_null=True)
    online = serializers.SerializerMethodField(read_only=True)
    presence = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RepresentativeMeeting
        exclude = ('meeting',)

    def get_online(self, instance):
        representative = self.get_representative(instance)
        return representative.online if representative else False

    def get_big_numbers(self, instance):
        try:
            voting_id = self.context.get('request').query_params.get('voting_id')
        except (KeyError, AttributeError):
            voting_id = getattr(instance, 'voting_id', None)

        if voting_id:
            return RepresentativeBigNumberSchema(instance.get_big_numbers(voting_id)).data
        return None

    def get_representative(self, instance):
        representative_ = getattr(instance, 'representative_reference_meeting', None)
        if representative_:
            return representative_

        request = self.context.get('request')
        if request:
            try:
                meeting_reference_id = request.parser_context.get('kwargs')['meeting_id']
                representative_ = instance.get_representative_by_meeting_id(meeting_reference_id)
                setattr(instance, 'representative_reference_meeting', representative_)
                return representative_
            except (KeyError, AttributeError):
                pass

        representative_ = instance.get_representative_by_meeting_id(instance.meeting_id)
        setattr(instance, 'representative_reference_meeting', representative_)
        return representative_

    def get_presence(self, instance):
        representative = self.get_representative(instance)
        if representative:
            return PresenceToRepresentativeSchema(representative.presence_).data
        return None


class AbstractClassFieldsSchema(serializers.Serializer):
    classe = serializers.UUIDField()
    name = serializers.CharField()
    percentage_present = serializers.FloatField()
    percentage_absent = serializers.FloatField()
    percentage_accredited = serializers.FloatField()


class CreditorsPresenceSerializer(AbstractClassFieldsSchema):
    count_creditors = serializers.IntegerField()
    count_present = serializers.IntegerField()
    count_absent = serializers.IntegerField()
    count_accredited = serializers.IntegerField()


class CreditorsCreditSerializer(AbstractClassFieldsSchema):
    total_credit = serializers.FloatField()
    total_credit_present = serializers.FloatField()
    total_credit_absent = serializers.FloatField()
    total_credit_accredited = serializers.FloatField()


class PermissionSchema(AbstractDescriptionSchema):
    class Meta:
        model = Permission
        fields = '__all__'


class GroupSchema(AbstractStatusSchema):
    permissions = PermissionSchema(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'


class UserMeetingIdsSchema(AbstractStatusSchema, WritableNestedModelSerializer):
    name = serializers.CharField(source='user', read_only=True)
    groups = GroupSchema(many=True, read_only=True)

    class Meta:
        model = UserMeeting
        fields = ('id', 'name', 'user_id', 'groups')


class MeetingToGuestSchema(AbstractStatusSchema):
    location = serializers.CharField(source='location.description', read_only=True)
    situation = serializers.CharField(read_only=True)
    situation_display = serializers.CharField(source='get_situation_display', read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingListSchema(AbstractStatusSchema):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    situation_display = serializers.CharField(source='get_situation_display', read_only=True)
    count_creditors = serializers.IntegerField(read_only=True)
    total_credit = serializers.FloatField(read_only=True)
    location = serializers.CharField(source='location.description', read_only=True)

    class Meta:
        model = Meeting
        fields = (
            'id', 'name', 'status', 'status_display', 'start_date', 'description',
            'count_creditors', 'total_credit', 'location', 'has_quorum',
            'situation', 'situation_display'
        )


class MeetingGroupListSchema(AbstractStatusSchema):
    has_quorum_first_call = serializers.BooleanField(read_only=True)
    has_quorum_after_first_call = serializers.BooleanField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'name', 'order', 'has_quorum', 'has_quorum_first_call', 'has_quorum_after_first_call')


class MeetingSchema(MeetingListSchema):
    location = LocationSchema(read_only=True)
    location_id = serializers.UUIDField(write_only=True)
    status_quorum = serializers.CharField(read_only=True)
    status_quorum_display = serializers.CharField(source='get_status_quorum_display', read_only=True)
    count_representatives = serializers.IntegerField(read_only=True)
    creditors_presence_status = CreditorsPresenceSerializer(read_only=True, many=True)
    creditors_credit = CreditorsCreditSerializer(read_only=True, many=True)
    situation_display = serializers.CharField(source='get_situation_display', read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingGuestSchema(AbstractStatusSchema):
    location = LocationSchema(read_only=True)
    available_to_enter = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    situation_display = serializers.CharField(source='get_situation_display', read_only=True)

    class Meta:
        model = Meeting
        fields = (
            'location', 'description', 'name', 'zoom_url', 'start_date',
            'status', 'status_display', 'id', 'available_to_enter',
            'situation', 'situation_display'
        )


class MeetingUpdateSchema(AbstractStatusSchema):
    location = LocationSchema(read_only=True)
    location_id = serializers.UUIDField(write_only=True, required=False)
    situation_display = serializers.CharField(read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'
        non_required_fields = '__all__'

    def save(self, **kwargs):
        current_url = self.instance.zoom_url
        new_url = self.validated_data.get('zoom_url', None)

        if new_url is not None and new_url != current_url:
            for creditor in self.instance.creditors:
                creditor.reset_meeting_invite()

        return super().save(**kwargs)


class MeetingBigNumbersSchema(AbstractStatusSchema):
    count_creditors = serializers.IntegerField(read_only=True)
    count_representatives = serializers.IntegerField(read_only=True)
    total_credit = serializers.FloatField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('count_creditors', 'count_representatives', 'total_credit')
        read_only_fields = ('count_creditors', 'count_representatives', 'total_credit')


class UserMeetingSchema(AbstractStatusSchema, WritableNestedModelSerializer):
    groups = GroupSchema(many=True, read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    meeting_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserMeeting
        exclude = ('meeting', 'user')


class UserMeetingCreateSchema(AbstractStatusSchema, WritableNestedModelSerializer):
    groups = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    user_id = serializers.IntegerField()
    meeting_id = serializers.UUIDField()

    class Meta:
        model = UserMeeting
        exclude = ('meeting', 'user')

    def validate(self, attrs):
        if UserMeeting.objects.filter(user_id=attrs['user_id'], meeting_id=attrs['meeting_id']).exists():
            raise ValidationErrorAdapter({'user': _('Usuário já cadastrado')})
        return super().validate(attrs)


class UserMeetingUpdateSchema(AbstractStatusSchema, WritableNestedModelSerializer):
    groups = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = UserMeeting
        exclude = ('meeting', 'user')


class AbstractChoicesSerializer(serializers.Serializer):
    id = serializers.CharField()
    legend = serializers.CharField(max_length=1)

    def to_representation(self, choice):
        return {'id': choice[0], 'legend': choice[1]}


class ChoicesOptionsSchema(serializers.Serializer):
    descriptions = {
        'meeting_status_options': _('Opções para os status possíveis para a Assembleia'),
        'status_quorum': _('Opções para os status possíveis para o quorum da Assembleia'),
        'coin_options': _('Opções para os tipos de moedas'),
        'type_person_options': _('Opções para os possíveis tipos de pessoas'),
        'status_voting_options': _('Opções para os possíveis status da Votação'),
        'choices_presence_options': _('Opções para os possíveis status da Presença do Credor'),
        'user_status_options': _('Opções para os possíveis status do User'),
        'report_options': _('Opções para os possíveis status dos relatórios'),
        'voted_by_options': _('Opções para os possíveis tipo de votantes do Resultado do Voto'),
        'situation_meeting_options': _('Opções para os possíveis tipo de situações da Assembleia'),
    }

    meeting_status_options = AbstractChoicesSerializer(StatusMeetingChoices.choices, many=True)
    meeting_status_quorum_options = AbstractChoicesSerializer(StatusQuorum.choices, many=True)
    coin_options = AbstractChoicesSerializer(CHOICES_COIN, many=True)
    type_person_options = AbstractChoicesSerializer(CHOICES_TYPE_PERSON, many=True)
    status_voting_options = AbstractChoicesSerializer(StatusVotingChoice.choices, many=True)
    user_status_options = AbstractChoicesSerializer(STATUS_CHOICES, many=True)
    report_meeting_options = AbstractChoicesSerializer(ReportMeetingChoices.choices, many=True)
    report_voting_options = AbstractChoicesSerializer(ReportVotingChoices.choices, many=True)
    voted_by_options = AbstractChoicesSerializer(VotedByChoices.choices, many=True)
    situation_meeting_options = AbstractChoicesSerializer(SituationMeetingChoices.choices, many=True)

    class Meta:
        fields = '__all__'


class StartRegisterPresenceSerializer(serializers.Serializer):
    time = serializers.TimeField()

    def update(self, instance, validated_data):
        time_extension = validated_data.get('time')
        instance.start_register_presence_voting(time_extension)
        return instance


class ExtendRegisterPresenceSerializer(serializers.Serializer):
    time = serializers.TimeField()

    def update(self, instance, validated_data):
        time_extension = validated_data.get('time')
        instance.extend_register_presence_voting(time_extension)
        return instance


class EndRegisterPresenceSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.end_register_presence_voting()
        return instance


class MeetingGroupSchema(AbstractStatusSchema):
    meetings = MeetingGroupListSchema(many=True)

    class Meta:
        model = MeetingGroup
        fields = '__all__'


class SuspendMeetingSchema(AbstractStatusSchema):
    class Meta:
        model = Meeting
        fields = ('name', 'location_id', 'start_date', 'status', 'description', 'situation')
        non_required_fields = '__all__'

    def update(self, meeting, validated_data):
        request = self.context.get('request')
        meeting_reference_id = request.parser_context.get('kwargs').get('id')
        validated_data['meeting_reference_id'] = meeting_reference_id

        start_date = validated_data.get('start_date')
        if not start_date:
            raise ValidationErrorAdapter({'start_date': _('Precisa do campo start_date para agendar uma nova assembleia')})

        if meeting.order == 1:
            meeting.finish()
        else:
            meeting.suspend()

        for field in self.fields:
            if field not in validated_data:
                validated_data[field] = getattr(meeting, field)

        validated_data['meeting_group'] = meeting.get_meeting_group()
        validated_data['order'] = meeting.meeting_group.count_meetings() + 1
        validated_data['status'] = StatusMeetingChoices.SCHEDULED
        validated_data['installed'] = True if (meeting.order == 1 and not meeting.installed) else False

        new_meeting = super().create(validated_data)
        new_meeting.duplicate_meeting()

        return meeting


class MeetingDispatchLinkCiamSchema(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    force = serializers.BooleanField(required=False, default=False, write_only=True)