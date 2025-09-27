from rest_framework import serializers
from .models import Category, Tag, Problem, TestCase, GlobalTemplate, ProblemTemplate


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'input_data', 'expected_output', 'is_sample', 'order']


class GlobalTemplateSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = GlobalTemplate
        fields = ['id', 'name', 'language', 'language_display', 'template_code', 
                 'description', 'creator', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['creator', 'created_at', 'updated_at']


class ProblemTemplateSerializer(serializers.ModelSerializer):
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    
    class Meta:
        model = ProblemTemplate
        fields = ['id', 'problem', 'problem_title', 'language', 'language_display', 
                 'template_code', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProblemListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    acceptance_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty', 'category', 'tags', 'author', 
                 'time_limit', 'memory_limit', 'total_submissions', 
                 'accepted_submissions', 'acceptance_rate', 'created_at']


class ProblemDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    test_cases = TestCaseSerializer(many=True, read_only=True)
    templates = ProblemTemplateSerializer(many=True, read_only=True)
    acceptance_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'description', 'input_format', 'output_format',
                 'sample_input', 'sample_output', 'hint', 'time_limit', 
                 'memory_limit', 'difficulty', 'category', 'tags', 'author',
                 'total_submissions', 'accepted_submissions', 'acceptance_rate',
                 'test_cases', 'templates', 'created_at', 'updated_at']


class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'input_format', 'output_format',
                 'sample_input', 'sample_output', 'hint', 'time_limit',
                 'memory_limit', 'difficulty', 'category', 'tags', 'is_public']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)