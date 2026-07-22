from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils import timezone
from ..models import UserProfile, CheckInRecord, Notification
from django.contrib.auth.models import User
from .decorators import admin_required, super_admin_required, _filter_profiles_by_school


# ═══════════════════════════════════════════════════════════════════════
# 8. Real-name Authentication Review
# ═══════════════════════════════════════════════════════════════════════

@admin_required
def admin_auth_view(request):
    """实名认证审核"""
    if request.method == 'POST':
        action = request.POST.get('action', '')
        profile_id = request.POST.get('profile_id', '')
        reason = request.POST.get('reason', '')

        if profile_id:
            try:
                profile = UserProfile.objects.get(id=int(profile_id))
            except (UserProfile.DoesNotExist, ValueError):
                profile = None

            if profile:
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

        return redirect('admin_auth')

    status_filter = request.GET.get('status', '')
    profiles = _filter_profiles_by_school(request)
    if status_filter:
        profiles = profiles.filter(auth_status=status_filter)
    profiles = profiles.order_by('-auth_time', 'auth_status')

    # 批量查询打卡次数，避免 N+1
    profile_list = list(profiles)
    user_ids = [p.user_id for p in profile_list]
    checkin_counts = {}
    if user_ids:
        counts = (
            CheckInRecord.objects
            .filter(user_id__in=user_ids)
            .values('user_id')
            .annotate(cnt=Count('id'))
        )
        checkin_counts = {c['user_id']: c['cnt'] for c in counts}

    auth_data = []
    for p in profile_list:
        student_id = p.student_id or ''
        total_checkins = checkin_counts.get(p.user_id, 0)
        auth_data.append({
            'profile': p,
            'student_id': student_id,
            'total_checkins': total_checkins,
        })

    pending_count = _filter_profiles_by_school(request).filter(auth_status='pending').count()
    approved_count = _filter_profiles_by_school(request).filter(auth_status='approved').count()
    rejected_count = _filter_profiles_by_school(request).filter(auth_status='rejected').count()
    unverified_count = _filter_profiles_by_school(request).filter(auth_status='unverified').count()

    context = {
        'current_page': 'auth',
        'auth_data': auth_data,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'unverified_count': unverified_count,
    }
    return render(request, 'admin/auth.html', context)


@super_admin_required
def admin_admin_manage(request):
    """管理员管理（仅超级管理员）"""
    # 只有超级管理员才能访问
    user = request.user
    is_super = user.is_authenticated and (user.is_staff or getattr(user.profile, 'role', '') == 'super_admin')
    if not is_super:
        return redirect('admin_dashboard')
    
    admins = UserProfile.objects.filter(role__in=['admin', 'super_admin']).order_by('role', '-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        profile_id = request.POST.get('profile_id', '')
        
        if action == 'add':
            phone = request.POST.get('phone', '').strip()
            nickname = request.POST.get('nickname', '').strip()
            password = request.POST.get('password', '').strip()
            role = request.POST.get('role', 'admin')
            
            if phone and nickname and password:
                if UserProfile.objects.filter(phone=phone).exists():
                    error = '该手机号已注册'
                else:
                    username = f'admin_{phone}'
                    new_user = User.objects.create_user(username=username, password=password)
                    UserProfile.objects.create(
                        user=new_user,
                        phone=phone,
                        nickname=nickname,
                        role=role,
                    )
                    return redirect('admin_admin_manage')
        
        elif action == 'edit':
            if profile_id:
                try:
                    profile = UserProfile.objects.get(id=int(profile_id))
                    # 不允许编辑超级管理员
                    if profile.role == 'super_admin':
                        return redirect('admin_admin_manage')
                    profile.nickname = request.POST.get('nickname', '').strip()
                    new_role = request.POST.get('role', 'admin')
                    # 只能设置为 admin 或 super_admin
                    if new_role in ['admin', 'super_admin']:
                        profile.role = new_role
                    profile.save()
                except UserProfile.DoesNotExist:
                    pass
            return redirect('admin_admin_manage')
        
        elif action == 'delete':
            if profile_id:
                try:
                    profile = UserProfile.objects.get(id=int(profile_id))
                    # 不能删除超级管理员
                    if profile.role != 'super_admin':
                        profile.user.delete()
                except UserProfile.DoesNotExist:
                    pass
            return redirect('admin_admin_manage')
    
    context = {
        'current_page': 'admin_manage',
        'admins': admins,
    }
    return render(request, 'admin/admin_manage.html', context)


# ═══════════════════════════════════════════════════════════════════════
# 11. User Account Management (Super Admin Only)
# ═══════════════════════════════════════════════════════════════════════

@super_admin_required
def admin_toggle_user(request, user_id):
    """启用/禁用用户账号"""
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
        user.is_active = not user.is_active
        user.save()
    except UserProfile.DoesNotExist:
        pass
    return redirect('admin_users')


@super_admin_required
def admin_reset_password(request, user_id):
    """重置用户密码为 123456"""
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
        user.set_password('123456')
        user.save()
    except UserProfile.DoesNotExist:
        pass
    return redirect('admin_users')
