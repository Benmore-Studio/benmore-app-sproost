from rest_framework import serializers
from .models import ContractorProfile

class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__' 
        
class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__' 