from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Message, Reply, Notification
from ..serializers import (
    MessageSerializer, MessageCreateSerializer, ReplySerializer,
)


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def messages_view(request):
    """留言板：获取留言（分页）/ 发布留言"""
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 50)

        qs = Message.objects.all().prefetch_related('replies__user__profile', 'likes').order_by('-created_at')
        total = qs.count()

        offset = (page - 1) * page_size
        msgs = qs[offset:offset + page_size]

        serializer = MessageSerializer(msgs, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total,
        })

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
    """系统通知（分页）"""
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 50)

        qs = Notification.objects.filter(user=request.user).order_by('-created_at')
        total = qs.count()
        unread_count = qs.filter(is_read=False).count()

        offset = (page - 1) * page_size
        notifs = qs[offset:offset + page_size]

        data = [{
            'id': n.id, 'title': n.title, 'content': n.content,
            'n_type': n.n_type, 'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        } for n in notifs]

        return Response({
            'results': data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total,
            'unread_count': unread_count,
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
