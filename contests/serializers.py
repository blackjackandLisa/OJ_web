from rest_framework import serializers
from .models import Contest, ContestProblem, ContestParticipation, ContestSubmission


class ContestProblemSerializer(serializers.ModelSerializer):
    problem = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ContestProblem
        fields = ['id', 'problem', 'order', 'points']


class ContestListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    participant_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'start_time', 'end_time',
                 'duration', 'status', 'is_public', 'created_by',
                 'participant_count', 'created_at']


class ContestDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    problems = ContestProblemSerializer(many=True, read_only=True)
    participant_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'start_time', 'end_time',
                 'duration', 'status', 'is_public', 'password', 'max_participants',
                 'created_by', 'problems', 'participant_count', 'created_at']


class ContestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ['title', 'description', 'start_time', 'end_time', 'duration',
                 'is_public', 'password', 'max_participants']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ContestParticipationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    contest = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ContestParticipation
        fields = ['id', 'user', 'contest', 'score', 'solved_count', 'penalty', 'joined_at']
