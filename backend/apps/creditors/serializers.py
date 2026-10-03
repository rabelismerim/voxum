from rest_framework import serializers
from apps.creditors.models import RecoveringCompany, Creditor, Representative

class RecoveringCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoveringCompany
        fields = '__all__'

class RepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Representative
        fields = '__all__'

class CreditorSerializer(serializers.ModelSerializer):
    representatives = RepresentativeSerializer(many=True, read_only=True)
    creditor_class_display = serializers.CharField(source='get_creditor_class_display', read_only=True)

    class Meta:
        model = Creditor
        fields = '__all__'