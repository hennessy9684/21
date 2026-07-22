from django.db import models as dj_models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import UserProfile, DailyTopic, CheckInRecord
from ..serializers import (
    DailyTopicSerializer, CheckInRecordSerializer, CheckInCreateSerializer,
)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def daily_topics(request):
    """获取21天打卡主题（部署前请先执行 python manage.py seed_topics 初始化）"""
    topics = DailyTopic.objects.all().order_by('day')
    serializer = DailyTopicSerializer(topics, many=True)
    return Response(serializer.data)


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

    # 预取所有 DailyTopic，避免循环内 N+1 查询
    topics_map = {t.day: t.title for t in DailyTopic.objects.all()}

    # 1. 上网时长统计
    duration_map = {'0-1小时': 0, '1-3小时': 0, '3-5小时': 0, '5小时以上': 0}
    duration_trend = []  # 每天时长趋势
    for r in records:
        raw_dur = r.online_duration.strip() if r.online_duration else ''
        dur_key, hours = _normalize_duration(raw_dur)
        duration_map[dur_key] = duration_map.get(dur_key, 0) + 1
        duration_trend.append({
            'day': r.day,
            'title': topics_map.get(r.day, f'第{r.day}天'),
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
