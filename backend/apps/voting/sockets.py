from django.db.models.signals import post_save, post_delete

from apps.voxum_base.views_sockets import Schema
from apps.meetings.models import Meeting
from apps.voting.models import StatusVotingChoice, Voting
from apps.voting.schemas import VotingAdminSchema, VotingListAdminSchema
from apps.web_sockets.signals import update_voting_list, update_voting_progress_detail, update_voting_by_meeting_list, \
    started_update_voting_progress_detail


# class VotingList(Schema):
#     """
#     Schema class for creditor list.
#
#     Attributes:
#         serializer: Serializer class for the schema.
#         channel: Channel to send the serialized data.
#         filter_key: Key used for filtering the data.
#
#     Methods:
#         get_room: Get the room for sending the data.
#         filter: Apply additional filters for data retrieval.
#     """
#     serializer = VotingAdminSchema
#     channel = 'voting_list'
#     many = True
#     filter_key = 'meeting_id'
#     # send_initial = False
#     signals = []
#     type = 'array'
#
#     def get_room(self):
#         """
#         Get the room for sending the data.
#
#         Returns:
#             str: The room name.
#         """
#         return self.instance.meeting.id
#
#     def filter(self):
#         """
#         Apply additional filters for data retrieval.
#
#         Returns:
#             dict: The filter parameters.
#         """
#         return {self.filter_key: self.instance.meeting.id}


class VotingByMeetingList(Schema):
    """
    Schema class for creditor list.

    Attributes:
        serializer: Serializer class for the schema.
        channel: Channel to send the serialized data.
        filter_key: Key used for filtering the data.

    Methods:
        get_room: Get the room for sending the data.
        filter: Apply additional filters for data retrieval.
    """
    serializer = VotingListAdminSchema
    channel = 'voting_list'
    many = True
    filter_key = 'meeting_id'
    signals = [update_voting_by_meeting_list]
    type = 'array_update'
    send_initial = False
    model = Meeting

    def get_room(self):
        """
        Get the room for sending the data.

        Returns:
            str: The room name.
        """

        return self.instance.id

    def filter(self):
        """
        Apply additional filters for data retrieval.

        Returns:
            dict: The filter parameters.
        """
        return {self.filter_key: self.instance.id}


class VotingDelete(Schema):
    """
    Schema class for creditor list.

    Attributes:
        serializer: Serializer class for the schema.
        channel: Channel to send the serialized data.
        filter_key: Key used for filtering the data.

    Methods:
        get_room: Get the room for sending the data.
        filter: Apply additional filters for data retrieval.
    """
    serializer = VotingListAdminSchema
    channel = 'voting_list'
    many = False
    filter_key = 'id'
    model = Voting
    send_initial = False
    signals = [post_delete]
    type = 'array_delete'

    def get_room(self):
        """
        Get the room for sending the data.

        Returns:
            str: The room name.
        """
        return self.instance.meeting.id

    def filter(self):
        """
        Apply additional filters for data retrieval.

        Returns:
            dict: The filter parameters.
        """
        return {self.filter_key: self.instance.id}


class VotingDetail(Schema):
    """
    Schema class for creditor list.

    Attributes:
        serializer: Serializer class for the schema.
        channel: Channel to send the serialized data.
        filter_key: Key used for filtering the data.

    Methods:
        get_room: Get the room for sending the data.
        filter: Apply additional filters for data retrieval.
    """
    serializer = VotingListAdminSchema
    channel = 'voting_list'
    many = False
    filter_key = 'meeting_id'
    send_initial = False
    signals = [post_save, update_voting_list]
    type = 'array_patch'

    identifier = 'voting_detail'

    def get_room(self):
        """
        Get the room for sending the data.

        Returns:
            str: The room name.
        """
        return self.instance.meeting.id

    def filter(self):
        """
        Apply additional filters for data retrieval.

        Returns:
            dict: The filter parameters.
        """
        return {self.filter_key: self.instance.meeting.id}


class VotingProgressDetail(Schema):
    """
    Schema for managing the details of a voting in progress.

    Attributes:
        serializer: Serializer used for managing the voting details.
        channel: Channel name for managing the voting progress.
        many: Boolean indicating if the schema handles multiple objects.
        filter_key: Key used for filtering the voting details.
        send_initial: Boolean indicating if initial data should be sent.
        signals: List of signals used for this schema.
        has_filter: Boolean indicating if the get data apply a filter.
    """
    serializer = VotingAdminSchema
    channel = 'voting_progress'
    many = False
    filter_key = 'meeting_id'
    send_initial = True
    signals = [update_voting_progress_detail, started_update_voting_progress_detail]
    has_filter = True
    type = 'object'
    is_priority = True
    identifier = 'voting_progress_detail'

    # TODO: separar o post_save do update_voting_progress_detail, enviar apenas as informações da votação quando for extend
    def get_room(self):
        """
        Get the room for sending the data.

        Returns:
            str: The room name.
        """
        return self.instance.meeting.id

    def filter(self):
        """
        Define filters for retrieving specific voting details when receive signals.

        Returns:
            dict: Filter criteria for retrieving voting details.
        """
        return {self.filter_key: self.instance.meeting.id, "meeting": self.instance.meeting,
                'status': StatusVotingChoice.INICIADA}

    @classmethod
    def get_filters(cls, room_id):
        """
        Get filters based on the room ID and statis of Voting.

        Args:
            room_id: ID of the room.

        Returns:
            dict: Filter criteria based on the room ID.
        """
        return {cls.filter_key: room_id, 'status': StatusVotingChoice.INICIADA}


class VotingProgressListDetail(VotingProgressDetail):
    serializer = VotingListAdminSchema
    type = 'object_patch'
    signals = [post_save]
    send_initial = False

# class VotingGuestProgressDetail(SchemaGuest):
#     """
#     Schema for managing the details of a voting in progress.
#
#     Attributes:
#         serializer: Serializer used for managing the voting details.
#         channel: Channel name for managing the voting progress.
#         many: Boolean indicating if the schema handles multiple objects.
#         filter_key: Key used for filtering the voting details.
#         send_initial: Boolean indicating if initial data should be sent.
#         signals: List of signals used for this schema.
#         has_filter: Boolean indicating if the get data apply a filter.
#     """
#     serializer = VotingAdminSchema
#     channel = 'voting_progress_detail_guest'
#     many = False
#     filter_key = 'meeting_id'
#     send_initial = True
#     signals = [post_save]
#     has_filter = True
#
#     def get_room(self):
#         """
#         Get the room for sending the data.
#
#         Returns:
#             str: The room name.
#         """
#         return f'{self.instance.meeting.id}_'
#
#     def filter(self):
#         """
#         Define filters for retrieving specific voting details when receive signals.
#
#         Returns:
#             dict: Filter criteria for retrieving voting details.
#         """
#         return {self.filter_key: self.instance.meeting.id, "meeting": self.instance.meeting,
#                 'status': StatusVotingChoice.INICIADA}
#
#     @classmethod
#     def get_filters(cls, room_id):
#         """
#         Get filters based on the room ID and statis of Voting.
#
#         Args:
#             room_id: ID of the room.
#
#         Returns:
#             dict: Filter criteria based on the room ID.
#         """
#         return {cls.filter_key: room_id, 'status': StatusVotingChoice.INICIADA}
#
#     @classmethod
#     def get_initial_data_by_room(cls, room_id, meeting_id, user_id):
#         """
#         Asynchronously retrieve the initial data for a given room.
#
#         Args:
#             room_id (str): The ID of the room.
#             meeting_id (str): The ID of the meeting.
#             user_id (str): The ID of the user.
#
#         Returns:
#             list or Model instance: The initial data for the room.
#                 If `many` is True, a list of instances is returned.
#                 Otherwise, a single instance is returned.
#         """
#         creditor = Creditor.objects.filter(guest__user__id=user_id, meeting_id=meeting_id).first()
#
#         representative_m = RepresentativeMeeting.objects.filter(guest__user__id=user_id,
#         meeting_id=meeting_id).first()
#         if not creditor and not representative_m:
#             logging.warning(f'user_id guest conectado sem creditor {user_id}')
#             return
#
#         voting_in_progress_or_null = Voting.objects.filter(meeting_id=meeting_id,
#                                                            status=StatusVotingChoice.INICIADA).first()
#

#         if voting_in_progress_or_null:
#             voting_in_progress_or_null.qualified_creditor = voting_in_progress_or_null.qualified_creditor(
#                 creditor)
#
#             voting_in_progress_or_null.guest_choices = voting_in_progress_or_null.guest_choices(creditor)
#
#             voting_in_progress_or_null.qualified_representative = voting_in_progress_or_null.qualified_representative(
#                 representative_m)
#
#         return voting_in_progress_or_null
