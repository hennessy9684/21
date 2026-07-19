import random
import string
from datetime import datetime

from django.db import models as dj_models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import UserProfile, DailyTopic, CheckInRecord, Message, Reply, Notification, VerificationCode, QuizQuestion, QuizResult
from .serializers import (
    UserProfileSerializer, UserRegisterSerializer, UserLoginSerializer,
    SendCodeSerializer, DailyTopicSerializer, CheckInRecordSerializer,
    CheckInCreateSerializer, MessageSerializer, MessageCreateSerializer,
    ReplySerializer,
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


@csrf_exempt
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取/更新用户资料"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': '资料不存在'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)

    # PUT
    data = request.data
    if 'nickname' in data:
        profile.nickname = data['nickname']
    if 'age' in data:
        profile.age = data['age']
    if 'grade' in data:
        profile.grade = data['grade']
    if 'gender' in data:
        profile.gender = data['gender']
    if 'avatar' in data:
        profile.avatar = data['avatar']
    profile.save()
    return Response(UserProfileSerializer(profile).data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schools(request):
    """获取所有管理员管理的学校列表（供用户选择）"""
    if not request.user.is_authenticated:
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
    qs = UserProfile.objects.filter(role='admin').exclude(managed_school='').values_list('managed_school', flat=True).distinct()
    return Response(sorted(list(qs)))


def submit_auth(request):
    """提交实名认证申请"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': '资料不存在'}, status=status.HTTP_404_NOT_FOUND)

    if profile.auth_status == 'pending':
        return Response({'error': '您的申请正在审核中，请耐心等待'}, status=status.HTTP_400_BAD_REQUEST)

    if profile.auth_status == 'approved':
        return Response({'error': '您已经通过实名认证'}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    real_name = data.get('real_name', '').strip()
    school = data.get('school', '').strip()
    class_name = data.get('class_name', '').strip()
    student_id = data.get('student_id', '').strip()

    if not real_name:
        return Response({'error': '请输入真实姓名'}, status=status.HTTP_400_BAD_REQUEST)
    if not school:
        return Response({'error': '请输入学校名称'}, status=status.HTTP_400_BAD_REQUEST)
    if not class_name:
        return Response({'error': '请输入班级'}, status=status.HTTP_400_BAD_REQUEST)
    if not student_id:
        return Response({'error': '请输入学号'}, status=status.HTTP_400_BAD_REQUEST)

    profile.real_name = real_name
    profile.school = school
    profile.class_name = class_name
    profile.student_id = student_id
    profile.auth_status = 'pending'
    profile.auth_reason = ''
    profile.auth_time = None
    profile.auth_operator = None
    profile.save()

    Notification.objects.create(
        user=request.user,
        title='实名认证申请已提交',
        content=f'您的实名认证申请已提交，请等待管理员审核',
        n_type='auth',
    )

    return Response({
        'status': 'pending',
        'message': '实名认证申请已提交，请等待管理员审核',
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def achievements(request):
    """用户成就徽章系统"""
    # 打卡统计
    total = CheckInRecord.objects.filter(user=request.user).count()
    records = CheckInRecord.objects.filter(user=request.user).order_by('-day')
    
    # 连续打卡天数
    streak = 0
    for i, r in enumerate(records):
        if r.day == total - i:
            streak += 1
        else:
            break

    # 统计各维度数据
    total_duration = 0
    for r in records:
        raw_dur = r.online_duration.strip() if r.online_duration else ''
        _, hours = _normalize_duration(raw_dur)
        total_duration += hours

    all_activities = []
    for r in records:
        if r.online_activities:
            for a in r.online_activities.replace('，', ',').split(','):
                a = a.strip()
                if a:
                    all_activities.append(a)
    study_ratio = all_activities.count('学习查资料') / max(len(all_activities), 1) * 100

    # 成就徽章定义
    badges = [
        {
            'id': 'first_day', 'name': '初次打卡', 'desc': '完成第1天打卡',
            'icon': '🌱', 'unlocked': total >= 1, 'color': '#2ed573',
        },
        {
            'id': 'streak_3', 'name': '三天坚持', 'desc': '连续打卡3天',
            'icon': '🔥', 'unlocked': streak >= 3, 'color': '#ffa502',
        },
        {
            'id': 'streak_7', 'name': '一周达人', 'desc': '连续打卡7天',
            'icon': '⭐', 'unlocked': streak >= 7, 'color': '#f9ca24',
        },
        {
            'id': 'streak_14', 'name': '半月之星', 'desc': '连续打卡14天',
            'icon': '🌟', 'unlocked': streak >= 14, 'color': '#a29bfe',
        },
        {
            'id': 'streak_21', 'name': '21天满贯', 'desc': '完成全部21天打卡',
            'icon': '🏆', 'unlocked': total >= 21, 'color': '#e84393',
        },
        {
            'id': 'halfway', 'name': '过半勇士', 'desc': '完成10天以上打卡',
            'icon': '💪', 'unlocked': total >= 10, 'color': '#667eea',
        },
        {
            'id': 'study_master', 'name': '学习达人', 'desc': '上网用途中学习占比超过40%',
            'icon': '📚', 'unlocked': study_ratio >= 40 and total >= 3, 'color': '#00b894',
        },
        {
            'id': 'healthy_user', 'name': '健康上网', 'desc': '累计上网时长合理（平均<3h）',
            'icon': '💚', 'unlocked': total >= 5 and (total_duration / total) <= 3, 'color': '#55efc4',
        },
        {
            'id': 'super_checker', 'name': '超级打卡王', 'desc': '完成全部打卡且连续21天',
            'icon': '👑', 'unlocked': total >= 21 and streak >= 21, 'color': '#ff7675',
        },
    ]

    unlocked = [b for b in badges if b['unlocked']]
    locked = [b for b in badges if not b['unlocked']]

    return Response({
        'badges': badges,
        'unlocked_count': len(unlocked),
        'total_badges': len(badges),
        'streak': streak,
        'total_checkins': total,
        'completion_rate': round(total / 21 * 100, 1),
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def daily_topics(request):
    """获取21天打卡主题"""
    topics = DailyTopic.objects.all().order_by('day')
    # 如果数据库为空，先初始化
    if not topics.exists():
        _init_topics()
        topics = DailyTopic.objects.all().order_by('day')
    serializer = DailyTopicSerializer(topics, many=True)
    return Response(serializer.data)


def _init_topics():
    """初始化21天安全用网打卡主题"""
    topics_data = [
        (1, '认识网络安全', '了解什么是网络安全，为什么它对我们很重要', '你认为网络安全是什么？请用自己的话描述一下吧！', '🔒'),
        (2, '我的网络身份', '思考你在网络上的身份，如何保护个人信息', '你在网上分享过哪些个人信息？哪些不该分享？', '🆔'),
        (3, '密码小达人', '学习创建强密码，保护账号安全', '你的密码够安全吗？说说创建强密码的小技巧！', '🔑'),
        (4, '网络诈骗大揭秘', '认识常见的网络诈骗手段', '你或身边的人遇到过网络诈骗吗？是怎么样的？', '🎭'),
        (5, '文明上网小卫士', '学习网络礼仪，做文明的小网民', '你觉得在网上应该注意哪些文明礼仪？', '😇'),
        (6, '健康上网时间', '合理安排上网时间，保护视力', '你每天上网多久？有什么控制上网时间的好方法？', '⏰'),
        (7, '网络谣言辨别', '学会辨别真假信息', '你是怎么判断网上信息真假的？分享你的方法！', '🔍'),
        (8, '保护个人隐私', '了解隐私保护的重要性', '你认为哪些信息属于个人隐私？如何保护？', '🤫'),
        (9, '安全社交', '社交媒体安全使用指南', '你在社交平台上遇到过哪些安全问题？如何处理？', '💬'),
        (10, '网络暴力说"不"', '认识网络暴力，学会保护自己', '遇到网络暴力时你会怎么做？如何帮助他人？', '🚫'),
        (11, '游戏安全指南', '安全玩游戏，远离游戏陷阱', '你玩游戏时遇到过哪些安全问题？如何防范？', '🎮'),
        (12, '网络消费小达人', '学会安全网购，理性消费', '你在网上买过东西吗？分享安全网购的经验！', '🛒'),
        (13, '识别钓鱼网站', '学会识别钓鱼链接和网站', '怎么分辨一个网站是否安全？分享你的判断方法！', '🎣'),
        (14, '公共WiFi安全', '了解公共WiFi的风险', '你在公共场所连接WiFi时要注意什么？', '📶'),
        (15, '网络学习好帮手', '善用网络资源学习', '你用过哪些有益的学习网站或App？推荐给大家！', '📚'),
        (16, '短视频安全', '安全刷视频，远离不良内容', '刷短视频时遇到不良内容你会怎么做？', '🎬'),
        (17, '网络交友安全', '安全交友，不轻信陌生人', '网络上有陌生人加你好友你会怎么处理？', '👥'),
        (18, '手机安全指南', '保护手机安全，防范风险', '你的手机做了哪些安全设置？分享一下吧！', '📱'),
        (19, '绿色上网承诺', '制定自己的上网守则', '请写下你的绿色上网承诺书！', '📝'),
        (20, '分享我的收获', '回顾这20天的学习收获', '这20天你学到了什么？最大的收获是什么？', '🎉'),
        (21, '毕业啦！', '完成21天打卡，成为网络安全小达人', '恭喜完成21天打卡！请写下你的感想和对未来的期望！', '🏆'),
    ]
    for day, title, content, question, icon in topics_data:
        DailyTopic.objects.get_or_create(
            day=day,
            defaults={
                'title': title,
                'content': content,
                'question': question,
                'icon': icon,
            }
        )


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def checkin(request):
    """打卡：获取打卡记录 / 提交打卡"""
    if request.method == 'GET':
        records = CheckInRecord.objects.filter(user=request.user).order_by('day')
        serializer = CheckInRecordSerializer(records, many=True)
        return Response(serializer.data)

    # POST - 提交打卡
    serializer = CheckInCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    day = serializer.validated_data['day']

    # === 前置校验：个人信息 + 学号认证 ===
    profile = request.user.profile
    if not profile.nickname or not profile.age or not profile.grade or not profile.gender:
        return Response({'error': '请先完善个人信息再打卡', 'code': 'profile_incomplete'}, status=status.HTTP_400_BAD_REQUEST)
    if profile.auth_status != 'approved':
        return Response({'error': '请先完成学号认证再打卡', 'code': 'auth_required'}, status=status.HTTP_400_BAD_REQUEST)

    # === 校验逻辑 ===

    # 1. 天数范围校验
    if day < 1 or day > 21:
        return Response({'error': '天数必须在1-21之间'}, status=status.HTTP_400_BAD_REQUEST)

    # 2. 当日已打卡校验（一天只能打一次卡）
    today = timezone.localdate()
    if CheckInRecord.objects.filter(user=request.user, date=today).exists():
        return Response({'error': '今天已经打过卡了，明天再来吧～'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. 重复打卡校验
    if CheckInRecord.objects.filter(user=request.user, day=day).exists():
        return Response({'error': f'第{day}天已打卡，不可重复提交'}, status=status.HTTP_400_BAD_REQUEST)

    # 4. 顺序校验：只能按顺序打卡（最多打下一关）
    max_done = CheckInRecord.objects.filter(user=request.user).aggregate(
        m=dj_models.Max('day')
    )['m'] or 0
    if day > max_done + 1:
        return Response({
            'error': f'请先完成第{max_done + 1}天的打卡',
            'current_progress': max_done,
            'next_day': max_done + 1,
        }, status=status.HTTP_400_BAD_REQUEST)

    # 5. 问卷字段校验
    answer = serializer.validated_data.get('answer', '').strip()
    online_duration = serializer.validated_data.get('online_duration', '')
    online_activities = serializer.validated_data.get('online_activities', '')
    online_impact = serializer.validated_data.get('online_impact', '')

    if not online_duration:
        return Response({'error': '请选择今日上网时长'}, status=status.HTTP_400_BAD_REQUEST)
    if not online_activities:
        return Response({'error': '请选择主要上网活动'}, status=status.HTTP_400_BAD_REQUEST)
    if not online_impact.strip():
        return Response({'error': '请填写上网带来的影响'}, status=status.HTTP_400_BAD_REQUEST)
    if len(answer) < 5:
        return Response({'error': '回答内容至少5个字，请认真填写哦～'}, status=status.HTTP_400_BAD_REQUEST)

    # === 采集客户端信息 ===
    ip_address = request.META.get('REMOTE_ADDR', '')
    # 如果有代理，取真实IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_info = serializer.validated_data.get('device_info', '')

    # === 记录入库 ===
    record = CheckInRecord.objects.create(
        user=request.user,
        day=day,
        answer=answer,
        online_duration=online_duration,
        online_activities=online_activities,
        online_impact=online_impact,
        mood=serializer.validated_data.get('mood', '😊'),
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=device_info,
    )

    # === 返回详细响应 ===
    return Response({
        'message': f'✅ 第{day}天打卡成功！',
        'record': CheckInRecordSerializer(record).data,
        'server_feedback': {
            'record_id': record.id,
            'server_time': record.created_at.isoformat(),
            'verified': True,
            'user': request.user.profile.nickname,
            'phone': request.user.profile.phone,
        }
    }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkin_stats(request):
    """获取打卡统计"""
    total = CheckInRecord.objects.filter(user=request.user).count()
    # 连续打卡天数
    records = CheckInRecord.objects.filter(user=request.user).order_by('-day')
    streak = 0
    for i, r in enumerate(records):
        if r.day == 21 - i:
            streak += 1
        else:
            break

    return Response({
        'total_days': total,
        'streak_days': streak,
        'completed': total >= 21,
        'progress': round(total / 21 * 100, 1),
    })


def _normalize_duration(dur_str):
    """将前端传来的时长值归一化为统计用的标准键名"""
    mapping = {
        '少于1小时': ('0-1小时', 0.5),
        '1-2小时': ('1-3小时', 1.5),
        '2-3小时': ('1-3小时', 2.5),
        '超过3小时': ('3-5小时', 4),
        # 兼容旧值
        '0-1小时': ('0-1小时', 0.5),
        '1-3小时': ('1-3小时', 2),
        '3-5小时': ('3-5小时', 4),
        '5小时以上': ('5小时以上', 6),
    }
    dur_str = dur_str.strip() if dur_str else ''
    return mapping.get(dur_str, (dur_str, 0))


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_stats(request):
    """上网数据统计 - 时长/用途/超标/周报"""
    records = CheckInRecord.objects.filter(user=request.user).order_by('day')

    # 1. 上网时长统计
    duration_map = {'0-1小时': 0, '1-3小时': 0, '3-5小时': 0, '5小时以上': 0}
    duration_trend = []  # 每天时长趋势
    for r in records:
        raw_dur = r.online_duration.strip() if r.online_duration else ''
        dur_key, hours = _normalize_duration(raw_dur)
        duration_map[dur_key] = duration_map.get(dur_key, 0) + 1
        duration_trend.append({
            'day': r.day,
            'title': DailyTopic.objects.get(day=r.day).title if DailyTopic.objects.filter(day=r.day).exists() else f'第{r.day}天',
            'duration': raw_dur or '-',
            'hours': hours,
        })

    total_days = max(len(records), 1)
    duration_distribution = [
        {'label': '0-1小时', 'count': duration_map['0-1小时'], 'percent': round(duration_map['0-1小时'] / total_days * 100, 1)},
        {'label': '1-3小时', 'count': duration_map['1-3小时'], 'percent': round(duration_map['1-3小时'] / total_days * 100, 1)},
        {'label': '3-5小时', 'count': duration_map['3-5小时'], 'percent': round(duration_map['3-5小时'] / total_days * 100, 1)},
        {'label': '5小时以上', 'count': duration_map['5小时以上'], 'percent': round(duration_map['5小时以上'] / total_days * 100, 1)},
    ]

    # 2. 上网用途占比
    activity_map = {}
    for r in records:
        if r.online_activities:
            for act in r.online_activities.replace('，', ',').split(','):
                act = act.strip()
                if act:
                    activity_map[act] = activity_map.get(act, 0) + 1

    activity_total = sum(activity_map.values()) or 1
    activity_breakdown = sorted([
        {'name': k, 'count': v, 'percent': round(v / activity_total * 100, 1)}
        for k, v in activity_map.items()
    ], key=lambda x: x['count'], reverse=True)

    # 3. 超标天数统计（>3小时视为超标）
    excessive_days = duration_map.get('3-5小时', 0) + duration_map.get('5小时以上', 0)
    healthy_days = duration_map.get('0-1小时', 0) + duration_map.get('1-3小时', 0)
    excessive_rate = round(excessive_days / total_days * 100, 1) if total_days > 0 else 0

    # 4. 按周分组（21天 = 3周）
    weeks = []
    for w in range(3):
        start = w * 7 + 1
        end = start + 6
        week_records = [r for r in records if start <= r.day <= end]
        week_dur = {'0-1小时': 0, '1-3小时': 0, '3-5小时': 0, '5小时以上': 0}
        for r in week_records:
            raw_dur = r.online_duration.strip() if r.online_duration else ''
            dur_key, _ = _normalize_duration(raw_dur)
            week_dur[dur_key] = week_dur.get(dur_key, 0) + 1

        week_excessive = week_dur.get('3-5小时', 0) + week_dur.get('5小时以上', 0)
        week_total = len(week_records)

        weeks.append({
            'week': w + 1,
            'label': f'第{w+1}周',
            'range': f'D{start}-D{end}',
            'total_days': week_total,
            'excessive_days': week_excessive,
            'healthy_days': week_total - week_excessive,
            'excessive_rate': round(week_excessive / week_total * 100, 1) if week_total > 0 else 0,
        })

    # 5. 生成周报摘要
    total_excessive = excessive_days
    top_activity = activity_breakdown[0]['name'] if activity_breakdown else '暂无数据'
    top_activity_pct = activity_breakdown[0]['percent'] if activity_breakdown else 0
    most_common_duration = max(duration_distribution, key=lambda x: x['count'])
    current_week = weeks[-1] if weeks else None

    report = {
        'total_days': total_days,
        'total_excessive_days': total_excessive,
        'excessive_rate': excessive_rate,
        'healthy_rate': round(healthy_days / total_days * 100, 1) if total_days > 0 else 0,
        'top_activity': top_activity,
        'top_activity_percent': top_activity_pct,
        'most_common_duration': most_common_duration['label'],
        'most_common_duration_percent': most_common_duration['percent'],
        'score': max(0, 100 - excessive_rate - (5 if total_excessive > 7 else 0) - (3 if top_activity in ['玩游戏', '刷短视频'] else 0)),
        'advice': _generate_advice(total_excessive, excessive_rate, top_activity, most_common_duration['label']),
    }

    return Response({
        'duration_distribution': duration_distribution,
        'duration_trend': duration_trend,
        'activity_breakdown': activity_breakdown,
        'excessive_days': excessive_days,
        'healthy_days': healthy_days,
        'excessive_rate': excessive_rate,
        'weeks': weeks,
        'report': report,
    })


def _generate_advice(total_excessive, excessive_rate, top_activity, most_duration):
    """根据数据生成建议"""
    tips = []
    if excessive_rate > 50:
        tips.append('你的上网时间偏长，建议每天控制在上限3小时以内')
    elif excessive_rate > 30:
        tips.append('注意控制上网时间，适当做些户外活动')
    else:
        tips.append('上网时间控制得不错，继续保持')

    if top_activity == '玩游戏':
        tips.append('游戏时间较多，建议增加学习和阅读时间')
    elif top_activity == '刷短视频':
        tips.append('刷视频时间较长，尝试用一些时间学习新知识')
    elif top_activity == '学习查资料':
        tips.append('学习为主的上网习惯很好，注意劳逸结合')

    if most_duration in ['3-5小时', '5小时以上']:
        tips.append('建议使用番茄工作法：每上网30分钟休息5分钟')
    else:
        tips.append('保持规律的上网节奏，形成好习惯')

    return tips


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def messages_view(request):
    """留言板：获取留言 / 发布留言"""
    if request.method == 'GET':
        msgs = Message.objects.all().prefetch_related('replies__user__profile', 'likes').order_by('-created_at')[:100]
        serializer = MessageSerializer(msgs, many=True, context={'request': request})
        return Response(serializer.data)

    # POST
    serializer = MessageCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    msg = Message.objects.create(
        user=request.user,
        content=serializer.validated_data['content'],
    )
    return Response(MessageSerializer(msg, context={'request': request}).data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_message(request, message_id):
    """回复留言"""
    try:
        msg = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': '留言不存在'}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': '回复内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    reply = Reply.objects.create(message=msg, user=request.user, content=content)
    return Response(ReplySerializer(reply).data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_message(request, message_id):
    """点赞 / 取消点赞留言"""
    try:
        msg = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': '留言不存在'}, status=status.HTTP_404_NOT_FOUND)

    if msg.likes.filter(id=request.user.id).exists():
        msg.likes.remove(request.user)
        return Response({'liked': False, 'like_count': msg.likes.count()})
    else:
        msg.likes.add(request.user)
        return Response({'liked': True, 'like_count': msg.likes.count()})


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notifications_view(request):
    """系统通知"""
    if request.method == 'GET':
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
        data = [{
            'id': n.id, 'title': n.title, 'content': n.content,
            'n_type': n.n_type, 'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        } for n in notifs]
        return Response({
            'notifications': data,
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
        })

    # POST: mark read
    nid = request.data.get('id')
    if nid:
        Notification.objects.filter(id=nid, user=request.user).update(is_read=True)
        return Response({'ok': True})
    # mark all read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'ok': True})


def create_notification(user, title, content, n_type='system'):
    """创建系统通知的工具函数"""
    return Notification.objects.create(user=user, title=title, content=content, n_type=n_type)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_questions(request):
    """获取今日测评题目（随机抽5题）"""
    import random

    # 获取用户当前打卡进度确定天数
    max_day = CheckInRecord.objects.filter(user=request.user).count() + 1
    day = int(request.GET.get('day', max_day))
    day = max(1, min(day, 21))

    questions = list(QuizQuestion.objects.filter(day=day))
    if len(questions) < 5:
        questions = list(QuizQuestion.objects.filter(day__lte=day).order_by('?')[:5])

    # 随机抽取最多5题
    if len(questions) > 5:
        questions = random.sample(questions, 5)

    data = [{
        'id': q.id,
        'q_type': q.q_type,
        'question': q.question,
        'options': {
            'A': q.option_a,
            'B': q.option_b,
            'C': q.option_c,
            'D': q.option_d,
        },
    } for q in questions]

    return Response({'questions': data, 'day': day, 'total': len(data)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_submit(request):
    """提交测评答案，返回评分并保存记录"""
    answers = request.data.get('answers', [])  # [{id: 1, answer: 'A'}, ...]
    day = request.data.get('day', 0)
    if not answers:
        return Response({'error': '请完成答题'}, status=status.HTTP_400_BAD_REQUEST)

    correct_count = 0
    results = []
    answers_detail = []
    for item in answers:
        try:
            q = QuizQuestion.objects.get(id=item['id'])
            is_correct = q.answer == item.get('answer', '')
            if is_correct:
                correct_count += 1
            results.append({
                'id': q.id,
                'question': q.question,
                'q_type': q.q_type,
                'user_answer': item.get('answer', ''),
                'correct_answer': q.answer,
                'is_correct': is_correct,
                'explanation': q.explanation,
            })
            answers_detail.append({
                'question_id': q.id,
                'user_answer': item.get('answer', ''),
                'is_correct': is_correct,
            })
        except QuizQuestion.DoesNotExist:
            pass

    total = len(answers)
    score = round(correct_count / total * 100) if total > 0 else 0

    QuizResult.objects.create(
        user=request.user,
        day=day,
        score=score,
        correct_count=correct_count,
        total_count=total,
        answers=answers_detail,
    )

    return Response({
        'total': total,
        'correct': correct_count,
        'score': score,
        'results': results,
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_history(request):
    """获取用户答题历史记录和得分趋势"""
    results = QuizResult.objects.filter(user=request.user).order_by('day', 'created_at')

    history = []
    for r in results:
        history.append({
            'id': r.id,
            'day': r.day,
            'score': r.score,
            'correct_count': r.correct_count,
            'total_count': r.total_count,
            'created_at': r.created_at.isoformat(),
            'answers': r.answers,
        })

    scores_by_day = {}
    for r in results:
        if r.day not in scores_by_day or r.score > scores_by_day[r.day]['score']:
            scores_by_day[r.day] = {
                'day': r.day,
                'score': r.score,
                'correct_count': r.correct_count,
                'total_count': r.total_count,
            }

    trend = sorted(scores_by_day.values(), key=lambda x: x['day'])

    total_quizzes = len(results)
    avg_score = round(sum(r.score for r in results) / total_quizzes) if total_quizzes > 0 else 0
    max_score = max(r.score for r in results) if results else 0

    return Response({
        'history': history,
        'trend': trend,
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'max_score': max_score,
    })


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_auth_review(request):
    """管理员审核实名认证申请"""
    if not request.user.is_staff:
        return Response({'error': '没有权限'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        status_filter = request.GET.get('status', '')
        profiles = UserProfile.objects.all()
        if status_filter:
            profiles = profiles.filter(auth_status=status_filter)
        profiles = profiles.order_by('-auth_time', 'auth_status')

        data = []
        for p in profiles:
            data.append({
                'id': p.id,
                'user_id': p.user.id,
                'username': p.user.username,
                'phone': p.phone,
                'nickname': p.nickname,
                'real_name': p.real_name,
                'school': p.school,
                'class_name': p.class_name,
                'student_id': p.student_id,
                'auth_status': p.auth_status,
                'auth_status_text': dict(UserProfile.auth_status.field.choices).get(p.auth_status, p.auth_status),
                'auth_reason': p.auth_reason,
                'auth_time': p.auth_time.isoformat() if p.auth_time else None,
                'auth_operator': p.auth_operator.username if p.auth_operator else None,
                'created_at': p.created_at.isoformat(),
            })
        return Response(data)

    # POST - 审核操作
    data = request.data
    profile_id = data.get('profile_id')
    action = data.get('action')
    reason = data.get('reason', '')

    try:
        profile = UserProfile.objects.get(id=profile_id)
    except UserProfile.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    if action == 'approve':
        profile.auth_status = 'approved'
        profile.auth_reason = reason
        profile.auth_time = timezone.now()
        profile.auth_operator = request.user
        profile.save()

        Notification.objects.create(
            user=profile.user,
            title='实名认证审核通过',
            content='恭喜您！实名认证已通过审核',
            n_type='auth',
        )
        return Response({'message': '审核通过', 'status': 'approved'})

    elif action == 'reject':
        profile.auth_status = 'rejected'
        profile.auth_reason = reason
        profile.auth_time = timezone.now()
        profile.auth_operator = request.user
        profile.save()

        Notification.objects.create(
            user=profile.user,
            title='实名认证审核未通过',
            content=f'您的实名认证申请未通过，原因：{reason}',
            n_type='auth',
        )
        return Response({'message': '已拒绝', 'status': 'rejected'})

    return Response({'error': '无效操作'}, status=status.HTTP_400_BAD_REQUEST)
