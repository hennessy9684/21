from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count, Q, Avg, Sum, Max
from django.utils import timezone
from datetime import date, timedelta, datetime
import json, csv, os
import io
from openpyxl import load_workbook
from ..models import UserProfile, DailyTopic, CheckInRecord, Message, Reply, Notification, QuizQuestion, QuizResult, Announcement
from django.contrib.auth.models import User


# ── Admin access decorator ─────────────────────────────────────────────

def get_user_from_token(request):
    """从请求中获取Token对应的用户"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        from rest_framework.authtoken.models import Token
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            pass
    return None


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return view_func(request, *args, **kwargs)
            try:
                if user.profile.role in ['admin', 'super_admin']:
                    return view_func(request, *args, **kwargs)
            except:
                pass
        else:
            token_user = get_user_from_token(request)
            if token_user:
                user = token_user
                try:
                    if user.profile.role in ['admin', 'super_admin']:
                        return view_func(request, *args, **kwargs)
                except:
                    pass
        return redirect(settings.LOGIN_URL)
    return wrapper


def _get_managed_school(request):
    """获取当前管理员负责的学校。super_admin 返回 None 表示不受限制"""
    user = request.user
    if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'super_admin'):
        return None  # 超级管理员 / Django staff → 不受限制
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return user.profile.managed_school or '__none__'  # __none__ 表示没有分配学校，查不到任何用户
    return '__none__'


def _filter_profiles_by_school(request):
    """根据管理员学校过滤 UserProfile 查询集，排除管理员账号"""
    school = _get_managed_school(request)
    if school is None:
        return UserProfile.objects.exclude(role__in=['admin', 'super_admin'])
    if school == '__none__':
        return UserProfile.objects.none()
    return UserProfile.objects.filter(school=school).exclude(role__in=['admin', 'super_admin'])


def super_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                return view_func(request, *args, **kwargs)
            try:
                if user.profile.role == 'super_admin':
                    return view_func(request, *args, **kwargs)
            except:
                pass
        else:
            token_user = get_user_from_token(request)
            if token_user:
                user = token_user
                try:
                    if user.profile.role == 'super_admin':
                        return view_func(request, *args, **kwargs)
                except:
                    pass
        return redirect(settings.LOGIN_URL)
    return wrapper


def _is_super_admin(user):
    """判断用户是否为超级管理员"""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return getattr(user.profile, 'role', '') == 'super_admin'


# ── Config helpers ─────────────────────────────────────────────────────

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'admin_config.json')

DEFAULT_CONFIG = {
    'activity_name': '21天安全用网打卡活动',
    'slogan': '每天打卡，做网络安全小达人！',
    'start_date': '',
    'end_date': '',
    'allow_makeup': False,
    'makeup_limit': 3,
}


def _load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    return {**DEFAULT_CONFIG, **config}


def _save_config(data):
    config = {**DEFAULT_CONFIG, **data}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ── Helper: calculate streak days (consecutive from day 1) ─────────────

def _calc_streak(user):
    """Count consecutive check-in days starting from day 1."""
    days = (
        CheckInRecord.objects.filter(user=user)
        .order_by('day')
        .values_list('day', flat=True)
    )
    if not days:
        return 0
    day_set = set(days)
    streak = 0
    for d in range(1, 22):
        if d in day_set:
            streak += 1
        else:
            break
    return streak
