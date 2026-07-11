from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import random


class UserProfile(models.Model):
    """用户资料 - 扩展用户信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('手机号', max_length=11, unique=True)
    nickname = models.CharField('昵称', max_length=50, default='')
    avatar = models.CharField('头像', max_length=200, default='')
    age = models.IntegerField('年龄', default=0)
    grade = models.CharField('年级', max_length=20, default='')
    gender = models.CharField('性别', max_length=10, default='')
    role = models.CharField('角色', max_length=20, default='user', choices=[
        ('user', '普通用户'),
        ('admin', '普通管理员'),
        ('super_admin', '超级管理员'),
    ])
    managed_school = models.CharField('管理学校', max_length=100, blank=True, default='', help_text='普通管理员负责的学校（仅role=admin时有效）')
    
    real_name = models.CharField('真实姓名', max_length=50, blank=True, default='')
    school = models.CharField('学校', max_length=100, blank=True, default='')
    class_name = models.CharField('班级', max_length=50, blank=True, default='')
    id_card = models.CharField('身份证号', max_length=18, blank=True, default='')
    auth_status = models.CharField('实名认证状态', max_length=20, default='unverified', choices=[
        ('unverified', '未认证'),
        ('pending', '审核中'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ])
    auth_reason = models.TextField('审核备注', blank=True, default='')
    auth_time = models.DateTimeField('审核时间', null=True, blank=True)
    auth_operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_operations', verbose_name='审核人')
    
    created_at = models.DateTimeField('注册时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.phone} - {self.nickname}'


class DailyTopic(models.Model):
    """每日打卡主题 - 21天安全用网"""
    day = models.IntegerField('第几天', unique=True)
    title = models.CharField('主题', max_length=200)
    content = models.TextField('内容描述')
    question = models.CharField('打卡问题', max_length=500, default='')
    icon = models.CharField('图标', max_length=50, default='📱')

    class Meta:
        verbose_name = '每日主题'
        verbose_name_plural = '每日主题'
        ordering = ['day']

    def __str__(self):
        return f'第{self.day}天: {self.title}'


class CheckInRecord(models.Model):
    """打卡记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins')
    day = models.IntegerField('第几天')
    date = models.DateField('打卡日期', auto_now_add=True)
    answer = models.TextField('主题回答', blank=True, default='')
    online_duration = models.CharField('今日上网时长', max_length=20, blank=True, default='')
    online_activities = models.TextField('主要上网活动', blank=True, default='')
    online_impact = models.TextField('上网带来影响', blank=True, default='')
    mood = models.CharField('心情', max_length=50, default='😊')
    is_completed = models.BooleanField('已完成', default=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True, default='')
    user_agent = models.TextField('用户代理', blank=True, default='')
    device_info = models.CharField('设备信息', max_length=200, blank=True, default='')
    created_at = models.DateTimeField('打卡时间', auto_now_add=True)

    class Meta:
        verbose_name = '打卡记录'
        verbose_name_plural = '打卡记录'
        unique_together = ['user', 'day']
        ordering = ['-day']


class Message(models.Model):
    """留言板"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField('留言内容')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_messages', blank=True)
    created_at = models.DateTimeField('留言时间', auto_now_add=True)

    class Meta:
        verbose_name = '留言'
        verbose_name_plural = '留言'
        ordering = ['-created_at']

    def like_count(self):
        return self.likes.count()

    def reply_count(self):
        return self.replies.count()

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'


class Reply(models.Model):
    """留言回复"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField('回复内容')
    created_at = models.DateTimeField('回复时间', auto_now_add=True)

    class Meta:
        verbose_name = '回复'
        verbose_name_plural = '回复'
        ordering = ['created_at']

    def __str__(self):
        return f'回复: {self.content[:20]}'


class VerificationCode(models.Model):
    """短信验证码"""
    phone = models.CharField('手机号', max_length=11)
    code = models.CharField('验证码', max_length=6)
    purpose = models.CharField('用途', max_length=20, default='register')  # register / login
    is_used = models.BooleanField('是否已使用', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} - {self.code}'


class Notification(models.Model):
    """系统通知 - 每个用户一条"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    n_type = models.CharField('类型', max_length=20, default='system')  # system/reminder/badge/bug_fix
    is_read = models.BooleanField('已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.title}'


class Announcement(models.Model):
    """系统公告 - 管理员发布的公告（一个公告对应多条通知）"""
    ANNOUNCE_TYPES = [
        ('announcement', '官方公告'),
        ('reminder', '活动提醒'),
        ('system', '系统通知'),
    ]
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    n_type = models.CharField('类型', max_length=20, default='announcement', choices=ANNOUNCE_TYPES)
    target_school = models.CharField('目标学校', max_length=100, blank=True, help_text='为空则发送给所有学校')
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='published_announcements')
    recipient_count = models.IntegerField('接收人数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    """答题测评题库"""
    Q_TYPES = [
        ('choice', '选择题'),
        ('true_false', '判断题'),
    ]
    q_type = models.CharField('题型', max_length=20, default='choice', choices=Q_TYPES)
    day = models.IntegerField('对应天数')
    question = models.TextField('题目')
    option_a = models.CharField('选项A', max_length=200, default='')
    option_b = models.CharField('选项B', max_length=200, default='')
    option_c = models.CharField('选项C', max_length=200, default='', blank=True)
    option_d = models.CharField('选项D', max_length=200, default='', blank=True)
    answer = models.CharField('正确答案', max_length=1)  # A/B or A/B/C/D
    explanation = models.TextField('答案解析', blank=True, default='')

    class Meta:
        verbose_name = '测评题目'
        verbose_name_plural = '测评题目'
        ordering = ['day', 'id']

    def __str__(self):
        return f'第{self.day}天: {self.question[:30]}'


class QuizResult(models.Model):
    """答题测评记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    day = models.IntegerField('对应天数')
    score = models.IntegerField('得分')
    correct_count = models.IntegerField('正确题数')
    total_count = models.IntegerField('总题数')
    answers = models.JSONField('答题详情')  # [{question_id, user_answer, is_correct}, ...]
    created_at = models.DateTimeField('答题时间', auto_now_add=True)

    class Meta:
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        ordering = ['-day', '-created_at']

    def __str__(self):
        return f'{self.user.username} - 第{self.day}天: {self.score}分'
