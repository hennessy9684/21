from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import UserProfile, CheckInRecord, Notification
from ..serializers import UserProfileSerializer
from .checkin import _normalize_duration


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
@api_view(['GET'])
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
