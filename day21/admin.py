from django.contrib import admin
from django.db.models import Count, Max
from django.shortcuts import render
from .models import UserProfile, DailyTopic, CheckInRecord, Message, VerificationCode


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['phone', 'nickname', 'age', 'created_at']
    search_fields = ['phone', 'nickname']
    list_per_page = 30


@admin.register(DailyTopic)
class DailyTopicAdmin(admin.ModelAdmin):
    list_display = ['day', 'title', 'icon', 'checkin_count']
    list_editable = ['title']

    def checkin_count(self, obj):
        return CheckInRecord.objects.filter(day=obj.day).count()
    checkin_count.short_description = '打卡人数'


@admin.register(CheckInRecord)
class CheckInRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'day', 'mood', 'date', 'is_completed', 'ip_address', 'created_at']
    list_filter = ['is_completed', 'day', 'date']
    search_fields = ['user__username', 'ip_address', 'answer']
    list_per_page = 50
    readonly_fields = ['ip_address', 'user_agent', 'device_info', 'created_at']

    fieldsets = (
        ('打卡信息', {
            'fields': ('user', 'day', 'answer', 'mood', 'is_completed')
        }),
        ('时间信息', {
            'fields': ('date', 'created_at')
        }),
        ('客户端信息', {
            'fields': ('ip_address', 'user_agent', 'device_info'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'created_at']
    list_per_page = 50

    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = '留言内容'


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['phone', 'code', 'purpose', 'is_used', 'created_at']
    list_filter = ['is_used', 'purpose']


def report_view(request):
    """管理员打卡报表"""

    # 总统计
    total_users = UserProfile.objects.count()
    total_checkins = CheckInRecord.objects.count()
    completed_users = UserProfile.objects.filter(
        user__checkins__day=21
    ).distinct().count()
    active_today = CheckInRecord.objects.filter(
        date__date=__import__('datetime').date.today()
    ).count()

    # 每日打卡统计
    daily_stats = []
    for day in range(1, 22):
        count = CheckInRecord.objects.filter(day=day).count()
        daily_stats.append({'day': day, 'count': count})

    # 用户打卡排名
    user_ranking = UserProfile.objects.annotate(
        checkin_count=Count('user__checkins'),
        max_day=Max('user__checkins__day'),
    ).order_by('-checkin_count')[:30]

    # 打卡完成率
    completion_rate = round(total_checkins / (total_users * 21) * 100, 1) if total_users > 0 else 0

    # 参与用户列表
    participants = UserProfile.objects.annotate(
        checkin_count=Count('user__checkins'),
    ).order_by('-checkin_count')

    # 今日打卡用户
    today = __import__('datetime').date.today()
    today_checkins = CheckInRecord.objects.filter(
        date=__import__('datetime').date.today()
    ).select_related('user__profile').order_by('-created_at')[:20]

    context = {
        'title': '打卡活动报表',
        'total_users': total_users,
        'total_checkins': total_checkins,
        'completed_users': completed_users,
        'active_today': active_today,
        'daily_stats': daily_stats,
        'user_ranking': user_ranking,
        'completion_rate': completion_rate,
        'participants': participants,
        'today_checkins': today_checkins,
    }
    return render(request, 'admin/report.html', context)
