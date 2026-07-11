from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from day21.admin import report_view
from day21.admin_views import (
    admin_index_view, admin_dashboard_view, admin_users_view,
    admin_topics_view, admin_messages_view, admin_announce_view, admin_config_view, admin_quiz_view, admin_auth_view,
    admin_admin_manage, admin_login_view, admin_import_users, admin_export_checkins,
    admin_toggle_user, admin_reset_password
)


def root_redirect(request):
    return redirect('http://localhost:5173/')


urlpatterns = [
    path('', root_redirect),
    # 自定义管理页面 —— 必须在 admin.site.urls 之前
    path('admin/report/', report_view, name='admin_report'),
    path('admin/home/', admin_index_view, name='admin_home'),
    path('manage/signin/', admin_login_view, name='admin_login'),
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('admin/users/', admin_users_view, name='admin_users'),
    path('admin/users/import/', admin_import_users, name='admin_import_users'),
    path('admin/users/<int:user_id>/toggle/', admin_toggle_user, name='admin_toggle_user'),
    path('admin/users/<int:user_id>/reset-password/', admin_reset_password, name='admin_reset_password'),
    path('admin/export/checkins/', admin_export_checkins, name='admin_export_checkins'),
    path('admin/topics/', admin_topics_view, name='admin_topics'),
    path('admin/messages/', admin_messages_view, name='admin_messages'),
    path('admin/announce/', admin_announce_view, name='admin_announce'),
    path('admin/config/', admin_config_view, name='admin_config'),
    path('admin/quiz/', admin_quiz_view, name='admin_quiz'),
    path('admin/auth/', admin_auth_view, name='admin_auth'),
    path('admin/manage/', admin_admin_manage, name='admin_admin_manage'),
    path('admin/', admin.site.urls),
    path('api/', include('day21.urls')),
]
