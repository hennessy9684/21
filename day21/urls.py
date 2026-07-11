from django.urls import path
from . import views

urlpatterns = [
    # 认证
    path('send-code/', views.send_code, name='send_code'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('achievements/', views.achievements, name='achievements'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('quiz/questions/', views.quiz_questions, name='quiz_questions'),
    path('quiz/submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    path('auth/submit/', views.submit_auth, name='submit_auth'),
    path('admin/auth-review/', views.admin_auth_review, name='admin_auth_review'),

    # 打卡
    path('topics/', views.daily_topics, name='daily_topics'),
    path('checkin/', views.checkin, name='checkin'),
    path('checkin/stats/', views.checkin_stats, name='checkin_stats'),
    path('usage-stats/', views.usage_stats, name='usage_stats'),

    # 留言
    path('messages/', views.messages_view, name='messages'),
    path('messages/<int:message_id>/reply/', views.reply_message, name='reply_message'),
    path('messages/<int:message_id>/like/', views.like_message, name='like_message'),
]
