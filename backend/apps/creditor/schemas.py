from apps.voxum_base.exceptions import ValidationErrorAdapter
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from utils import _

from apps.voxum_base.schemas import CoinSchema
from core.abstract.schemas import AbstractStatusSchema, AbstractDescriptionSchema
from apps.creditor.models import Creditor, Representative

from apps.guest.schemas import UserGuestSchema
from apps.meetings.models import RepresentativeMeeting
from apps.meetings.schemas import ClasseSchema, RepresentativeMeetingSchema
from apps.presence.schemas import PresenceSchema
from apps.recovering.schemas import RecoveringSchema
from apps.voting.models import VotingResult, Choice
class AbstractGuest(serializers.Serializer):
    pass


class RepresentativeSchema(AbstractGuest, WritableNestedModelSerializer, AbstractStatusSchema):
    representative = RepresentativeMeetingSchema(read_only=True)
    representative_id = serializers.UUIDField(write_only=True)
    able_to_vote = serializers.BooleanField(read_only=True)

    class Meta:
        model = Representative
        exclude = ('creditor',)


class RepresentativeDetailSchema(AbstractDescriptionSchema):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    id = serializers.UUIDField(read_only=True)

    non_required_fields = '__all__'

    class Meta:
        model = RepresentativeMeeting
        non_required_fields = '__all__'
        fields = ('email', 'doc_ok', 'is_accredited', 'id')

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        representative: RepresentativeMeeting = super().update(instance, validated_data)

        if email:
            representative.guest.user.email = email
            representative.guest.user.save()

        return representative


class AbstractCreditorSchema(AbstractStatusSchema, AbstractGuest, WritableNestedModelSerializer):
    guest = UserGuestSchema(read_only=True)
    guest_id = serializers.UUIDField(write_only=True)

    classe = ClasseSchema(read_only=True)
    recovering = RecoveringSchema(read_only=True)

    type_person_display = serializers.CharField(source='get_type_person_display', read_only=True)
    presence = PresenceSchema(read_only=True)
    representatives = RepresentativeSchema(many=True, required=False, allow_null=True)
    able_to_vote = serializers.BooleanField(read_only=True)

    class Meta:
        model = Creditor
        exclude = ('meeting',)

    def validate(self, attrs):
        priorities = [item.get('priority') for item in attrs.get('representatives', [])]

        if priorities:
            attrs['priority'] = len(priorities) + 1
        else:
            attrs['priority'] = 0

        expected_priorities = set(range(len(priorities)))
        priorities = set(priorities)
        if priorities != expected_priorities:
            missing_priorities = expected_priorities - priorities
            raise ValidationErrorAdapter(_("Estão faltando as prioridades: {}").format(missing_priorities))

        return super().validate(attrs)


class ChoiceSchema(AbstractDescriptionSchema):
    voting_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Choice
        exclude = ('voting',)
        read_only_fields = tuple(field.name for field in Choice._meta.fields)
        ref_name = 'CreditorChoice'


class VotingResultDetailSchema(AbstractDescriptionSchema):
    vote = ChoiceSchema(read_only=True)
    type = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = VotingResult
        exclude = ('creditor',)
        read_only_fields = tuple(field.name for field in VotingResult._meta.fields)
        ref_name = 'CreditorVotingResultDetail'


class DefaultCreditorSchema(AbstractCreditorSchema):
    meeting_id = serializers.UUIDField()
    classe_id = serializers.UUIDField(write_only=True)
    recovering_id = serializers.UUIDField(write_only=True)
    votes = VotingResultDetailSchema(source='get_votes', read_only=True, many=True)
    is_accredited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Creditor
        exclude = ('meeting',)

    def validate(self, attrs):
        representative_ids = [item.get('representative_id') for item in attrs.get('representatives', [])]
        guest_user_id = attrs['guest_id']

        if Representative.objects.filter(representative__id__in=representative_ids,
                                         representative__guest__id=guest_user_id).exists():
            raise ValidationErrorAdapter(_('O Usuário convidado não pode ser representante dele mesmo'))
        validate = super().validate(attrs)
        return validate

    def create(self, validated_data):
        representatives = validated_data.pop('representatives', [])
        creditor = super().create(validated_data)
        for representative in representatives:
            new_representative = RepresentativeSchema(data=representative)
            new_representative.is_valid(raise_exception=True)
            Representative(creditor=creditor, **new_representative.validated_data).save()
        return creditor


class CreditorSchema(DefaultCreditorSchema):
    coin = CoinSchema()


class MassiveCreditorSchema(DefaultCreditorSchema):
    code = serializers.IntegerField()
    coin_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Creditor
        exclude = ('meeting', 'coin')


class CreditorDetailSchema(AbstractCreditorSchema):
    classe_id = serializers.UUIDField(write_only=True, required=False)
    recovering_id = serializers.UUIDField(write_only=True, required=False)
    coin = CoinSchema(required=False)
    guest_id = serializers.UUIDField(write_only=True, required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Creditor
        exclude = ('meeting',)
        non_required_fields = '__all__'

    def validate(self, attrs):
        guest_user_id = self.instance.guest_id
        representative_ids = [item.get('representative_id') for item in attrs.get('representatives', [])]
        if Representative.objects.filter(representative__id__in=representative_ids,
                                         representative__guest__id=guest_user_id).exists():
            raise ValidationErrorAdapter(_('O Usuário convidado não pode ser representante dele mesmo'))
        validate = super().validate(attrs)
        return validate

    def update(self, instance, validated_data):
        representatives = validated_data.pop('representatives', None)
        email = validated_data.pop('email', None)
        creditor = super().update(instance, validated_data)
        guest = creditor.guest
        user = creditor.guest.user

        if email:
            if email != user.email:
                msal_user = getattr(guest, 'msaluserguest', None)
                if msal_user:
                    from apps.guest.models import MsalGuestStatusChoices
                    msal_user.status = MsalGuestStatusChoices.IN_LINE
                    msal_user.save()

                if creditor:
                    creditor.reset_meeting_invite()

            user.email = email
            user.save()

        if isinstance(representatives, list):
            ids = [representative.get('id') for representative in representatives if representative.get('id')]
            instance.representatives.exclude(id__in=ids).delete()
            for representative in representatives:
                new_representative = RepresentativeSchema(data=representative)
                new_representative.is_valid(raise_exception=True)
                Representative(creditor=creditor, **new_representative.validated_data).save()
        return creditor