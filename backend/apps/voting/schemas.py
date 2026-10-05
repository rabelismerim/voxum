"""
Serializa os campos do modelo Home para uso na API.

Este módulo define um serializer do Django REST Framework que herda tanto de
`serializers.ModelSerializer` quanto de uma classe personalizada `AbstractModelSchema`.
O serializer converte instâncias do modelo `Home` para e do formato JSON, e
valida os dados recebidos com base nos campos do modelo.

Attributes:
    - `Meta`: Uma classe aninhada que especifica metadados para o serializer. O atributo `model`
      especifica a classe de modelo na qual o serializer deve se basear, e
      `fields` lista os nomes de todos os campos que devem ser incluídos na representação serializada.
"""
from core.abstract.exceptions import ValidationErrorAdapter
from core.abstract.schemas import AbstractModelSchema
from core.abstract.schemas import SerializerMethodFieldChild
from django.db.models.signals import post_save
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers, renderers
from drf_yasg.utils import swagger_serializer_method
from utils import _, get_user_model

from apps.voxum_base.utils import get_traceback_err
from apps.meetings.models import RepresentativeMeeting
from apps.meetings.schemas import ClasseSchema
from core.abstract.schemas import AbstractDescriptionSchema

from apps.creditor.models import Creditor, Representative
from apps.creditor.schemas import CreditorSchema
from apps.voting.models import Voting, Choice, VotingResult, TypeVotingChoices


class ResultChoicesVoting(serializers.Serializer):
    """Serializador para o resultado de cada escolha de uma votação

    Attributes:
        value: A opção do voto.
        count_voters: Numero de votantes.
        percentage_voters: Porcentagem de votantes.
        """
    value = serializers.CharField(read_only=True)
    count_voters = serializers.FloatField(read_only=True)
    percentage_voters = serializers.FloatField(read_only=True)

    total_voters_credit_value = serializers.FloatField(read_only=True)
    total_percentage_voters = serializers.FloatField(read_only=True)


class VotingResultClassSchema(serializers.Serializer):
    """
    Serializer schema for a simplified representation of a group of voting results.

    Attributes:
        classe: A UUIDField for the class of the voting results.
        name: A CharField for the name of the voting results.
        count_voters: An IntegerField for the count of voters in the voting results.
        count_qualified_creditors: An IntegerField for the count of qualified creditors in the voting results.
        count_remaining: An IntegerField for the count of remaining voters in the voting results.
        percentage_voters: A FloatField for the percentage of voters in the voting results.
        percentage_remaining: A FloatField for the percentage of remaining voters in the voting results.
    """
    classe = serializers.UUIDField()
    name = serializers.CharField()
    count_voters = serializers.IntegerField()
    count_qualified_creditors = serializers.IntegerField()
    count_accredited_creditors = serializers.IntegerField()
    count_remaining = serializers.IntegerField()
    percentage_voters = serializers.FloatField()
    percentage_remaining = serializers.FloatField()

    total_credit_value = serializers.FloatField()
    total_accredited_credit_value = serializers.FloatField()
    total_voters_credit_value = serializers.FloatField()
    total_remaining = serializers.IntegerField()
    total_percentage_voters = serializers.FloatField()
    total_percentage_remaining = serializers.FloatField()

    choices = ResultChoicesVoting(many=True, read_only=True)


class ChoiceCreateSchema(AbstractDescriptionSchema):
    """
    Serializer schema for creating a Choice instance.

    Attributes:
        classe: A nested ClasseSchema instance for the classe field.
        classe_id: A write-only UUIDField for the classe foreign key.
        voting_id: A write-only UUIDField for the voting foreign key.
    """
    classe = ClasseSchema(read_only=True)
    classe_id = serializers.UUIDField(write_only=True)
    voting_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Choice
        exclude = ('voting',)
        ref_name = 'VotingChoice'


class ChoiceSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a simplified representation of a Choice instance.

    Attributes:
        classe: A nested ClasseSchema instance for the classe field.
        classe_id: A write-only UUIDField for the classe foreign key.
    """
    classe = ClasseSchema(read_only=True)
    classe_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Choice
        exclude = ('voting',)
        ref_name = 'VotingChoiceDetail'


class ChoiceToVotingSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a simplified representation of a Choice instance.

    Attributes:
        classe: A nested ClasseSchema instance for the classe field.
        classe_id: A write-only UUIDField for the classe foreign key.
    """
    classe = ClasseSchema(read_only=True)
    classe_id = serializers.UUIDField(write_only=True)
    voting_id = serializers.UUIDField()

    class Meta:
        model = Choice
        exclude = ('voting',)


class ChoiceUpdateSchema(AbstractDescriptionSchema):
    """
    Serializer schema for updating a Choice instance.
    """

    class Meta:
        model = Choice
        exclude = ('voting', 'classe')


class VotingResultAdminSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a simplified representation of a VotingResult instance by an admin.

    Attributes:
        vote: A nested ChoiceSchema instance for the vote field.
        vote_id: A write-only UUIDField for the vote foreign key.
        creditor_id: A write-only UUIDField for the creditor foreign key.
    """
    vote = ChoiceSchema(read_only=True)
    vote_id = serializers.UUIDField(write_only=True)
    creditor_id = serializers.UUIDField(write_only=True)
    type = serializers.CharField(read_only=True)

    class Meta:
        model = VotingResult
        fields = '__all__'
        read_only_fields = ('creditor', 'type')


class CreditorVoteSchema(CreditorSchema):
    """
    Serializer schema for a detailed representation of a Creditor instance with its vote.
    """

    class Meta:
        model = Creditor
        fields = '__all__'


class CreditorResultSchema(CreditorVoteSchema):
    """
    Serializer schema for a detailed representation of a Creditor instance with its vote result.

    Attributes:
        result: A nested VotingResultAdminSchema instance for the vote result field.
    """
    result = SerializerMethodFieldChild(read_only=True, allow_null=True, child=VotingResultAdminSchema())

    @swagger_serializer_method(serializer_or_field=VotingResultAdminSchema)
    def get_result(self, instance) -> dict | None:
        vote = instance.get_result_by_id(instance.voting_id)
        if vote:
            return VotingResultAdminSchema(vote).data
        return None

    class Meta:
        model = Creditor
        fields = '__all__'


class QualifiedCreditorsSchema(AbstractModelSchema):
    """
    Serializer schema for a simplified representation of a group of qualified creditors.

    Attributes:
        classe: A UUIDField for the class of the creditors.
        name: A CharField for the name of the creditors.
        creditors: A nested CreditorResultSchema instance for the creditors field.
    """
    classe = serializers.UUIDField()
    name = serializers.CharField()
    creditors = CreditorResultSchema(many=True)
    choices = ChoiceSchema(many=True, exclude=('classe',))


class QualifiedCreditorsByRepresentativesSchema(QualifiedCreditorsSchema):
    """
    Serializer schema for representing qualified creditors grouped by representatives.

    Attributes:
        classe (serializers.UUIDField): The UUID field for representing the class.
        name (serializers.CharField): The character field for representing the name.
        creditors (CreditorResultSchema): The schema for representing creditor results (many).

    """
    creditors = CreditorResultSchema(many=True, exclude=('representatives',))


class GroupChoiceSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a group of choices with the same class.

    Attributes:
        classe: A read-only field for the class of the choices.
        choices: A nested ChoiceSchema instance for the choices field.
    """
    classe = serializers.ReadOnlyField()
    choices = ChoiceSchema(many=True, exclude=('classe',))

    class Meta:
        model = Choice
        fields = ('choices', 'classe')


class VotingAdminDetailSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a detailed representation of a Voting instance by an admin.

    Attributes:
        meeting_id: A UUIDField for the meeting foreign key.
        class_choice: A nested GroupChoiceSchema instance for the class_choice field.
        type_display: A CharField for the display name of the voting type.
        results: A nested VotingResultClassSchema instance for the results field.
    """
    meeting_id = serializers.UUIDField()
    choices = serializers.ListField(child=serializers.CharField(), write_only=True)
    classes = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    class_choice = GroupChoiceSchema(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    results = VotingResultClassSchema(read_only=True, many=True)

    class Meta:
        model = Voting
        exclude = ('meeting',)


class RepresentativesByClassSchema(AbstractDescriptionSchema):
    """
    Serializer schema for representing representatives grouped by class.

    Attributes:
        qualified_creditors (QualifiedCreditorsByRepresentativesSchema): The schema for qualified creditors (many).

    Meta:
        model (RepresentativeMeeting): The model associated with the schema.
        fields (str): The fields to include in the schema.

    """
    qualified_creditors = QualifiedCreditorsByRepresentativesSchema(many=True)

    class Meta:
        model = RepresentativeMeeting
        fields = '__all__'


class VotingAdminListDetailSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a detailed representation of a Voting instance by an admin.

    Attributes:
        meeting_id: A UUIDField for the meeting foreign key.
        type_display: A CharField for the display name of the voting type.
    """
    meeting_id = serializers.UUIDField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Voting
        exclude = ('meeting',)


class VotingListAdminSchema(WritableNestedModelSerializer, VotingAdminListDetailSchema):
    """
    Serializer schema for creating and updating a Voting instance by an admin.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)


class VotingAdminSchema(WritableNestedModelSerializer, VotingAdminDetailSchema):
    """
    Serializer schema for creating and updating a Voting instance by an admin.

    Attributes:
        qualified_creditors: A nested QualifiedCreditorsSchema instance for the qualified_creditors field.
    """
    qualified_creditors = serializers.IntegerField(source='count_qualified_creditors', read_only=True)
    qualified_representatives = serializers.IntegerField(source='count_qualified_representatives', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    def validate(self, attrs):
        type_voting = attrs.get('type')
        if type_voting == TypeVotingChoices.ASSUNTO:
            attrs.pop('choices', None)
        return super().validate(attrs)

    def create(self, validated_data):
        choices = validated_data.pop('choices', [])
        classes = validated_data.pop('classes', [])
        voting = super().create(validated_data)

        from apps.voting.models import dispatch_voting_choice
        post_save.disconnect(dispatch_voting_choice, sender=Choice)

        for classe in classes:
            for choice in choices:
                choice_data = {
                    'value': choice,
                    'classe_id': classe,
                    'voting_id': voting.id,
                }
                serializer = ChoiceToVotingSchema(data=choice_data, context={'request': self.context['request']})
                serializer.is_valid(raise_exception=True)
                serializer.save()

        voting.create_default_choices(classes)
        post_save.connect(dispatch_voting_choice, sender=Choice)

        return voting


class VotingAdminUpdateSchema(AbstractDescriptionSchema):
    """
    Serializer schema for updating a Voting instance by an admin.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Voting
        exclude = ('meeting',)
        non_required_fields = '__all__'


class VotingResultDetailInternalSchema(AbstractDescriptionSchema):
    """
    Serializer schema for a detailed representation of a VotingResult instance.

    Attributes:
        vote: A nested ChoiceSchema instance for the vote field.
        vote_id: A write-only UUIDField for the vote foreign key.
        creditor_id: A read-only UUIDField for the creditor foreign key.

    """
    vote = ChoiceSchema(read_only=True)
    vote_id = serializers.UUIDField(write_only=True)
    type = serializers.CharField(read_only=True)
    voted_by_id = serializers.UUIDField(read_only=True, allow_null=True)
    creditor_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = VotingResult
        exclude = ('voted_by', 'creditor')
        non_required_fields = '__all__'


class VotingResultDetailSchema(VotingResultDetailInternalSchema):
    """
    Serializer schema for a detailed representation of a VotingResult instance.

    Attributes:
        vote: A nested ChoiceSchema instance for the vote field.
        vote_id: A write-only UUIDField for the vote foreign key.
        creditor: A nested CreditorSchema instance for the creditor field.

    """
    creditor = CreditorSchema(read_only=True)

    class Meta:
        model = VotingResult
        exclude = ('voted_by',)
        non_required_fields = '__all__'
        ref_name = 'VotingResultDetail'


class VotingResultSchema(VotingResultDetailSchema):
    """
    Serializer schema for a simplified representation of a VotingResult instance.

    Attributes:
        creditor_id: A write-only UUIDField for the creditor foreign key.
    """
    creditor_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = VotingResult
        fields = '__all__'
        non_required_fields = '__all__'
        read_only_fields = ('voted_by',)

    def validate(self, attrs):
        request = self.context.get('request')

        if request:
            user_id = request.user.id
        else:
            user_id = self.context.get('user_id')

        if not user_id:
            raise ValidationErrorAdapter({'voted_by': _('Deve fornecer um user_id')})

        user = get_user_model().objects.filter(id=user_id).first()
        attrs['voted_by_id'] = user_id
        attrs['create_user'] = user.username
        attrs['update_user'] = user.username
        return super().validate(attrs)


class RepresentativeResultsCreateSerializer(serializers.Serializer):
    """
    Serializer for handling the creation of representative results.

    Attributes:
        success (BooleanField): Indicates the success status of the operation (read-only).
        vote_result (VotingResultDetailInternalSchema): Schema representing detailed voting results (read-only).
        errors (ListField): List of error messages if any (read-only).
        vote_id (UUIDField): Identifier for the vote (read-only).
        creditor_id (UUIDField): Identifier for the creditor (read-only).
    """
    success = serializers.BooleanField(read_only=True)
    vote_result = VotingResultDetailInternalSchema(required=False, read_only=True)
    errors = serializers.ListField(child=serializers.CharField(), required=False, read_only=True)
    vote_id = serializers.UUIDField(read_only=True)
    creditor_id = serializers.UUIDField(read_only=True)


class RepresentativeResultsSchema(serializers.Serializer):
    """
    Serializer for handling the creation of representative results.

    Args:
        creditors_voting (VotingResultSchema): Schema representing creditor voting results (write-only).

    Attributes:
        renderer_classes (list): List of renderer classes for serialization.
        result (RepresentativeResultsCreateSerializer): Serialized data representing the created results (read-only).

    Methods:
        create(self, validated_data): Creates representative results based on validated data.

    Raises:
        ValidationErrorAdapter: Raised when validation fails.

    Returns:
        dict: Dictionary containing the created results.
    """
    renderer_classes = [renderers.JSONRenderer]
    creditors_voting = VotingResultSchema(many=True, write_only=True)
    result = RepresentativeResultsCreateSerializer(many=True, read_only=True)
    meeting_id = serializers.UUIDField(write_only=True)
    remove_old_voting = True

    def create(self, validated_data):
        user_id = validated_data.get('user_id') or self.context.get('user_id')
        if user_id:
            representatives_creditors = Representative.objects.filter(
                representative__meeting_id=validated_data['meeting_id'], representative__guest__user_id=user_id)
        else:
            representative_id = validated_data.get('representative_id')
            representatives_creditors = Representative.objects.filter(
                representative__meeting_id=validated_data['meeting_id'], representative__id=representative_id)

            user_id = representatives_creditors.first().representative.guest.user_id
        callback = []

        vote_ids = []
        creditor_ids = []
        success = True
        for creditor in validated_data['creditors_voting']:
            creditor_ids.append(creditor['creditor_id'])
            vote_ids.append(creditor['vote_id'])

        creditors = Creditor.objects.filter(id__in=creditor_ids, guest__user_id=user_id)

        for creditor in validated_data['creditors_voting']:
            creditor_id = creditor['creditor_id']
            relation_representative_creditor = representatives_creditors.filter(creditor_id=creditor_id).exists()
            errors = []
            if not relation_representative_creditor:
                has_creditor = creditors.filter(id=creditor_id, guest__user_id=user_id).exists()
                if not has_creditor:
                    errors.append(_('Relação entre representante e credor inválida'))

            voting_schema = VotingResultSchema(data=creditor, context={'user_id': user_id})

            voting = None

            if not errors:
                try:
                    voting_schema.is_valid(raise_exception=True)
                    if self.remove_old_voting:
                        voting_id = Voting.objects.filter(choice__id=creditor['vote_id']) \
                            .values_list('id', flat=True).first()

                        VotingResult.objects.filter(creditor=creditor['creditor_id'],
                                                    vote__voting__id=voting_id).delete()
                    voting = voting_schema.save()
                except Exception as e:
                    traceback_str, e = get_traceback_err(e)
                    errors.append(e)
            obj_callback = creditor.copy()

            if not errors:
                obj_callback['success'] = True
                obj_callback['vote_result'] = VotingResultDetailSchema(voting).data
            else:
                success = False
                obj_callback['success'] = False
                obj_callback['errors'] = errors
            callback.append(obj_callback)
        return {
            'result': callback,
            'success': success
        }


class RepresentativeResultsByInternalSchema(RepresentativeResultsSchema):

    def validate(self, attrs):
        request = self.context.get('request')
        attrs = super().validate(attrs)
        attrs['representative_id'] = request.parser_context['kwargs']['representative_id']
        return attrs


class StartVotingSerializer(serializers.Serializer):
    """
    Serializer for starting a voting process.

    Attributes:
        time: TimeField representing the time extension for the voting.

    Methods:
        update(self, instance, validated_data): Method to initiate the voting process.
    """
    time = serializers.TimeField()

    def update(self, instance, validated_data):
        time_extension = validated_data.get('time')
        instance.start_voting(time_extension)
        return instance


class ExtendVotingSerializer(serializers.Serializer):
    """
    Serializer for extending an ongoing voting.

    Attributes:
        time: TimeField representing the time extension for the voting.

    Methods:
        update(self, instance, validated_data): Method to extend an ongoing voting process.
    """
    time = serializers.TimeField()

    def update(self, instance, validated_data):
        time_extension = validated_data.get('time')
        instance.extend_voting(time_extension)
        return instance


class EndVotingSerializer(serializers.Serializer):
    """
    Serializer for ending an ongoing voting.

    Methods:
        update(self, instance, validated_data): Method to end an ongoing voting process.
    """

    def update(self, instance, validated_data):
        instance.end_voting()
        return instance


# To Guest User
class VotingGuestDetailSchema(AbstractDescriptionSchema):
    """
    Serializer schema para a votação do usuário externo

    Attributes:
        meeting_id: A UUIDField for the meeting foreign key.
        guest_choices: A nested GroupChoiceSchema instance for the class_choice field.
        type_display: A CharField for the display name of the voting type.
        qualified_creditor: A Creditor object.
    """
    meeting_id = serializers.UUIDField(read_only=True)
    creditor_id = serializers.UUIDField(read_only=True, required=False)
    guest_choices = GroupChoiceSchema(many=False, read_only=True, allow_null=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    qualified_creditor = CreditorResultSchema(read_only=True, fields=(
        'able_to_vote', 'result'), allow_null=True)
    qualified_representative = QualifiedCreditorsByRepresentativesSchema(many=True)

    class Meta:
        model = Voting
        exclude = ('meeting',)


# To Guest Without Details
class VotingGuestWithoutDetailSchema(AbstractDescriptionSchema):
    """
    Serializer schema para a votação do usuário externo

    Attributes:
        meeting_id: A UUIDField for the meeting foreign key.
        type_display: A CharField for the display name of the voting type.
    """
    meeting_id = serializers.UUIDField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Voting
        fields = ('create_user', 'created_at', 'description', 'meeting_id', 'start_date', 'end_date', 'status', 'type',
                  'type_display', 'update_user', 'updated_at')


class VotingResultGuestSchema(VotingResultSchema):
    """
    Serializer schema para a criação do voto pelo usuário externo.
    """

    type = serializers.CharField(read_only=True)

    class Meta:
        model = VotingResult
        fields = '__all__'
        non_required_fields = '__all__'

    def validate(self, attrs):
        validate = super().validate(attrs)

        user_id = self.context.get('user_id')
        if not Creditor.objects.filter(id=attrs['creditor_id'], guest__user_id=user_id).exists():
            raise ValidationErrorAdapter({'creditor': _('O Usuário não tem relação com este Credor')})

        user = get_user_model().objects.filter(id=user_id).first()
        attrs['voted_by_id'] = user_id
        attrs['create_user'] = user.username
        attrs['update_user'] = user.username

        return validate


class VotingGuestTaskSchema(AbstractModelSchema):
    task_id = serializers.UUIDField(read_only=True)


class VotingResultRepresentativeGuestSchema(RepresentativeResultsSchema):
    """
    Serializer for handling the creation of representative results, by user guest.
    """
    remove_old_voting = False

    def validate(self, attrs):
        validate = super().validate(attrs)

        user_id = self.context.get('user_id')
        representative_creditor = Representative.objects.filter(
            representative__meeting__id=attrs['meeting_id'],
            representative__guest__user_id=user_id).exists()
        if not representative_creditor:
            raise ValidationErrorAdapter({'meeting': _('O Usuário não tem relação com este Representante')})
        attrs['user_id'] = user_id
        user = get_user_model().objects.filter(id=user_id).first()
        attrs['voted_by_id'] = user_id
        attrs['create_user'] = user.username
        attrs['update_user'] = user.username
        return validate