"""创建测试用户（学校=11，密码=123456）"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from day21.models import UserProfile


class Command(BaseCommand):
    help = '创建学校为11的测试用户'

    def add_arguments(self, parser):
        parser.add_argument('--phone', default='13900001111', help='手机号')
        parser.add_argument('--password', default='123456', help='密码')
        parser.add_argument('--school', default='11', help='学校')
        parser.add_argument('--nickname', default='测试同学', help='昵称')

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']
        school = options['school']
        nickname = options['nickname']

        # 删除旧账号（如存在）
        User.objects.filter(username=f'test_{phone}').delete()
        UserProfile.objects.filter(phone=phone).delete()

        # 创建新账号
        u = User.objects.create_user(username=f'test_{phone}', password=password)
        UserProfile.objects.create(
            user=u,
            phone=phone,
            nickname=nickname,
            school=school,
            role='user',
            auth_status='approved',
            age=15,
            grade='初三',
            gender='男',
        )

        self.stdout.write(self.style.SUCCESS(
            f'创建成功！\n'
            f'  手机号: {phone}\n'
            f'  密码: {password}\n'
            f'  学校: {school}\n'
            f'  昵称: {nickname}'
        ))
