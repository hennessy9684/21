from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, DailyTopic, CheckInRecord, Message, Reply, VerificationCode


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'phone', 'nickname', 'avatar', 'age', 'grade', 'gender', 'role',
                  'real_name', 'school', 'class_name', 'student_id',
                  'auth_status', 'auth_reason', 'auth_time']


class UserRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(max_length=128)
    nickname = serializers.CharField(max_length=50, default='')


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=128)


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    purpose = serializers.CharField(default='register')


class DailyTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTopic
        fields = '__all__'


class CheckInRecordSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = CheckInRecord
        fields = ['id', 'day', 'date', 'answer', 'online_duration',
                  'online_activities', 'online_impact', 'mood', 'is_completed',
                  'ip_address', 'user_agent', 'device_info', 'created_at',
                  'nickname', 'phone']
        read_only_fields = ['user', 'date', 'ip_address', 'user_agent',
                           'device_info', 'created_at']

    def get_nickname(self, obj):
        try:
            return obj.user.profile.nickname
        except:
            return ''

    def get_phone(self, obj):
        try:
            return obj.user.profile.phone
        except:
            return ''


class CheckInCreateSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    answer = serializers.CharField(allow_blank=True, default='')
    online_duration = serializers.CharField(allow_blank=True, default='')
    online_activities = serializers.CharField(allow_blank=True, default='')
    online_impact = serializers.CharField(allow_blank=True, default='')
    mood = serializers.CharField(default='😊')
    device_info = serializers.CharField(required=False, allow_blank=True, default='')


class ReplySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'username', 'nickname', 'content', 'created_at']
        read_only_fields = ['user', 'message', 'created_at']

    def get_username(self, obj):
        return obj.user.username

    def get_nickname(self, obj):
        try:
            return obj.user.profile.nickname
        except:
            return ''


class MessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'username', 'nickname', 'avatar', 'content',
                  'like_count', 'reply_count', 'is_liked', 'replies', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_username(self, obj):
        return obj.user.username

    def get_nickname(self, obj):
        try:
            return obj.user.profile.nickname
        except:
            return ''

    def get_avatar(self, obj):
        try:
            return obj.user.profile.avatar
        except:
            return ''

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class MessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)
