"""
Configuração de URLs para o módulo de Assembleias (Meeting).
"""
from django.urls import path

from apps.meetings.views import (
    MeetingListApi, ClasseApi, MeetingDetailApi, ChoicesOptionsApi,
    RepresentativeMeetingApi, RepresentativeMeetingListApi, StartRegisterPresenceView,
    ExtendRegisterPresenceView, EndRegisterPresenceView, MeetingSuspendApi,
    MeetingGroupApi, MeetingBigNumberApi, MeetingDetailGuestApi,
    StartDispatchLinkCiamView, StartDispatchLinkMeetingView
)

urlpatterns = [
    path('', MeetingListApi.as_view(), name='meeting'),
    path('big_numbers/<uuid:id>/', MeetingBigNumberApi.as_view(), name='meeting_big_number_detail'),
    path('<uuid:id>/', MeetingDetailApi.as_view(), name='meeting_detail'),
    path('guest/detail/<uuid:id>/', MeetingDetailGuestApi.as_view(), name='meeting_guest_detail'),
    path('class/', ClasseApi.as_view(), name='class'),
    path('options/', ChoicesOptionsApi.as_view(), name='options'),
    path('suspend/<uuid:id>/', MeetingSuspendApi.as_view()),
    path('group/', MeetingGroupApi.as_view()),

    path('representatives/', RepresentativeMeetingApi.as_view(), name='create_representative'),
    path('representatives/<uuid:meeting_id>/', RepresentativeMeetingListApi.as_view(), name='meeting_representatives_list'),

    path('dispatch_link_ciam/<uuid:id>/', StartDispatchLinkCiamView.as_view(), name='start_dispatch_link_ciam'),
    path('dispatch_link_meeting/<uuid:id>/', StartDispatchLinkMeetingView.as_view(), name='start_dispatch_link_meeting'),

    path('register_presence/start/<uuid:id>/', StartRegisterPresenceView.as_view(), name='start_register_presence'),
    path('register_presence/extend/<uuid:id>/', ExtendRegisterPresenceView.as_view(), name='extend_register_presence'),
    path('register_presence/end/<uuid:id>/', EndRegisterPresenceView.as_view(), name='stop_register_presence'),
]