from rest_framework import permissions

from apps.creditor.models import Creditor
from apps.meetings.models import RepresentativeMeeting
from apps.creditor.schemas import (
    CreditorDetailSchema,
    CreditorSchema,
    RepresentativeDetailSchema,
    RepresentativeSchema,
)
from core.abstract.views import AbstractViewApi
from core.permissions.views import IsUserManagerOrConsultantPermission


class CreditorApi(AbstractViewApi):
    model = Creditor
    model_query = Creditor.objects.all()
    serializer_class = CreditorSchema
    http_method_names = ['get', 'post']
    pagination = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


class CreditorDetailApi(AbstractViewApi):
    model = Creditor
    model_query = Creditor.objects.all()
    serializer_class = CreditorDetailSchema
    http_method_names = ['get', 'put', 'delete']
    many = False
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


class CreditorMeetingApi(AbstractViewApi):
    model = Creditor
    model_query = Creditor.objects.all()
    serializer_class = CreditorSchema
    http_method_names = ['get']
    pagination = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


class CreditorRepresentativeApi(AbstractViewApi):
    model = Creditor
    model_query = Creditor.objects.all()
    serializer_class = CreditorSchema
    http_method_names = ['get']
    pagination = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    def get_queryset(self):
        representative_id = self.kwargs['representative__representative__id']
        return self.model_query.filter(representatives__representative__id=representative_id)


class RepresentativeDetailApi(AbstractViewApi):
    model = RepresentativeMeeting
    model_query = RepresentativeMeeting.objects.all()
    serializer_class = RepresentativeDetailSchema
    http_method_names = ['get', 'put']
    many = False
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
