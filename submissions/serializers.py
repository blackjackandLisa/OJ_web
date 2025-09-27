from rest_framework import serializers
from .models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    problem = serializers.StringRelatedField(read_only=True)
    is_accepted = serializers.ReadOnlyField()
    
    class Meta:
        model = Submission
        fields = ['id', 'user', 'problem', 'language', 'status', 'time_used',
                 'memory_used', 'score', 'error_message', 'test_results',
                 'is_accepted', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'time_used', 'memory_used',
                           'score', 'error_message', 'test_results', 'created_at']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['problem', 'language', 'code']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
