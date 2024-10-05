from rest_framework import serializers
from profiles.models import AgentProfile

class AgentAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning agents to homeowners by registration ID.
    
    ----------------------------
    INPUT PARAMETERS:
    - registration_id: str
    
    -----------------------------
    """
    registration_ID = serializers.CharField(max_length=100)
