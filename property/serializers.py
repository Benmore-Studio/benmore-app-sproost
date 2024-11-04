from rest_framework import serializers
from .models import AssignedAccount

class AssignedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedAccount
        fields = '__all__'