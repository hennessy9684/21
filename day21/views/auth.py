import random
import string
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import UserProfile, VerificationCode
from ..serializers import (
    UserProfileSerializer, UserRegisterSerializer, UserLoginSerializer,
    SendCodeSerializer,
)
from ..sms import get_sms_client


def generate_code():
    """生成6位验证码"""
    return ''.join(random.choices(string.digits, k=6))


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def send_code(request):
    """发送验证码"""
    serializer = SendCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    phone = serializer.validated_data['phone']
    purpose = serializer.validated_data.get('purpose', 'register')

    # 频率限制：60秒内只能发送一次
    recent = VerificationCode.objects.filter(
        phone=phone, purpose=purpose,
        created_at__gt=timezone.now() - timedelta(seconds=60)
    ).first()
    if recent:
        remaining = 60 - int((timezone.now() - recent.created_at).total_seconds())
        return Response(
            {'error': f'发送过于频繁，请{remaining}秒后再试'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # 生成并保存验证码
    code = generate_code()
    VerificationCode.objects.create(
        phone=phone,
        code=code,
        purpose=purpose
    )

    # 调用阿里云短信发送
    sms = get_sms_client()
    sms_result = sms.send_verify_code(phone, code)

    if sms_result:
        return Response({'message': '验证码已发送，5分钟内有效'})
    else:
        # 短信配置未完成或发送失败时，开发环境下返回验证码方便测试
        from django.conf import settings
        if settings.DEBUG:
            return Response({
                'message': '验证码已发送（调试模式）',
                'code': code,
                'debug': True
            })
        return Response({'message': '验证码已发送，5分钟内有效'})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """注册：手机号 + 验证码 + 密码"""
    serializer = UserRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    phone = serializer.validated_data['phone']
    code = serializer.validated_data['code']
    password = serializer.validated_data['password']
    nickname = serializer.validated_data.get('nickname', '')

    # 验证验证码
    last_code = VerificationCode.objects.filter(
        phone=phone, purpose='register', is_used=False
    ).first()

    if not last_code:
        return Response({'error': '请先获取验证码'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证码5分钟过期
    if timezone.now() - last_code.created_at > timedelta(minutes=5):
        last_code.is_used = True
        last_code.save()
        return Response({'error': '验证码已过期，请重新获取'}, status=status.HTTP_400_BAD_REQUEST)

    if last_code.code != code:
        return Response({'error': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查手机号是否已注册
    if UserProfile.objects.filter(phone=phone).exists():
        return Response({'error': '该手机号已注册'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建用户
    username = f'user_{phone}'
    user = User.objects.create_user(
        username=username,
        password=password,
    )
    UserProfile.objects.create(
        user=user,
        phone=phone,
        nickname=nickname or f'小朋友{phone[-4:]}',
    )
    # 创建Token
    token, _ = Token.objects.get_or_create(user=user)

    # 标记验证码已使用
    last_code.is_used = True
    last_code.save()

    return Response({
        'message': '注册成功',
        'user': UserProfileSerializer(user.profile).data,
        'token': token.key,
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """登录：手机号 + 密码"""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    phone = serializer.validated_data['phone']
    password = serializer.validated_data['password']

    try:
        profile = UserProfile.objects.get(phone=phone)
        user = profile.user
    except UserProfile.DoesNotExist:
        return Response({'error': '手机号未注册'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'error': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建或获取Token
    token, _ = Token.objects.get_or_create(user=user)

    # 为管理员用户创建Django会话，以便访问后台管理页面
    from django.contrib.auth import login as django_login
    if profile.role in ['admin', 'super_admin'] or user.is_staff:
        django_login(request, user)

    return Response({
        'message': '登录成功',
        'user': UserProfileSerializer(profile).data,
        'token': token.key,
    })
