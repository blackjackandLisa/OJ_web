from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserActivityLog, UserRanking


class UserSerializer(serializers.ModelSerializer):
    acceptance_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'avatar', 'school', 
                 'student_id', 'bio', 'rating', 'total_submissions', 
                 'accepted_submissions', 'acceptance_rate', 'is_verified', 
                 'date_joined']
        read_only_fields = ['id', 'rating', 'total_submissions', 
                           'accepted_submissions', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'nickname']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    acceptance_rate = serializers.ReadOnlyField()
    rank = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'avatar', 'school', 
                 'student_id', 'bio', 'rating', 'total_submissions', 
                 'accepted_submissions', 'acceptance_rate', 'rank', 'is_verified', 
                 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'rating', 'total_submissions', 
                           'accepted_submissions', 'date_joined', 'last_login']
    
    def get_rank(self, obj):
        return obj.get_rank()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户资料更新序列化器"""
    
    class Meta:
        model = User
        fields = ['nickname', 'email', 'school', 'student_id', 'bio', 'avatar']
    
    def validate_email(self, value):
        """验证邮箱唯一性"""
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被使用')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码错误')
        return value
    
    def validate_new_password(self, value):
        """验证新密码"""
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """验证密码确认"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('新密码和确认密码不匹配')
        return attrs


class UserActivityLogSerializer(serializers.ModelSerializer):
    """用户活动日志序列化器"""
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = ['id', 'user', 'action', 'action_display', 'description', 
                 'ip_address', 'created_at']


class UserRankingSerializer(serializers.ModelSerializer):
    """用户排行榜序列化器"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = UserRanking
        fields = ['rank', 'user', 'rating', 'solved_count', 'updated_at']


class UserStatsSerializer(serializers.ModelSerializer):
    """用户统计序列化器"""
    acceptance_rate = serializers.ReadOnlyField()
    rank = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'rating', 'total_submissions', 
                 'accepted_submissions', 'acceptance_rate', 'rank', 'recent_activity']
    
    def get_rank(self, obj):
        return obj.get_rank()
    
    def get_recent_activity(self, obj):
        """获取最近活动"""
        recent_logs = UserActivityLog.objects.filter(user=obj)[:5]
        return UserActivityLogSerializer(recent_logs, many=True).data
