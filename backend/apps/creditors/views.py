from rest_framework import viewsets
from apps.creditors.models import RecoveringCompany, Creditor, Representative
from apps.creditors.serializers import RecoveringCompanySerializer, CreditorSerializer, RepresentativeSerializer

class RecoveringCompanyViewSet(viewsets.ModelViewSet):
    queryset = RecoveringCompany.objects.all()
    serializer_class = RecoveringCompanySerializer

class CreditorViewSet(viewsets.ModelViewSet):
    queryset = Creditor.objects.filter(is_deleted=False)
    serializer_class = CreditorSerializer
    filterset_fields = ['recovering_company', 'creditor_class', 'doc_ok']

class RepresentativeViewSet(viewsets.ModelViewSet):
    queryset = Representative.objects.all()
    serializer_class = RepresentativeSerializer