import random
import string

from django.contrib.auth.models import User
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
    # 生成验证码
    code = generate_code()
    # 保存验证码
    VerificationCode.objects.create(
        phone=phone,
        code=code,
        purpose=serializer.validated_data.get('purpose', 'register')
    )
    # 模拟发送短信 - 直接返回验证码方便测试
    return Response({'message': '验证码已发送', 'code': code})


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

    if not last_code or last_code.code != code:
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
