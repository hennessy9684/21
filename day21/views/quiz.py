import random

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import UserProfile, CheckInRecord, QuizQuestion, QuizResult, Notification


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
