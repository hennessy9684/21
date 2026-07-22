from django.test import TestCase
from django.contrib.auth.models import User
from day21.models import UserProfile, DailyTopic, CheckInRecord, QuizQuestion, QuizResult, VerificationCode


# ====================================================================
# 1. 认证测试
# ====================================================================
class AuthTests(TestCase):
    """登录 / 注册相关 API 测试"""

    def setUp(self):
        self.phone = '13900000001'
        self.password = '123456'
        self.user = User.objects.create_user(username=self.phone, password=self.password)
        UserProfile.objects.create(
            user=self.user,
            phone=self.phone,
            nickname='测试用户',
            age=15,
            grade='高一',
            gender='男',
            role='student',
            auth_status='approved',
        )

    # ---------- 登录 ----------
    def test_login_success(self):
        """正确凭据登录，返回 200 且含 user 字段"""
        resp = self.client.post(
            '/api/login/',
            {'phone': self.phone, 'password': self.password},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('user', data)
        self.assertIn('token', data)

    def test_login_wrong_password(self):
        """错误密码返回 400 且含 error"""
        resp = self.client.post(
            '/api/login/',
            {'phone': self.phone, 'password': 'wrong_pass'},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    def test_login_nonexistent_user(self):
        """未注册手机号返回 400"""
        resp = self.client.post(
            '/api/login/',
            {'phone': '13900000002', 'password': self.password},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    # ---------- 注册 ----------
    def test_register(self):
        """POST /api/register/ 注册新用户，返回 200 且含 user 字段"""
        VerificationCode.objects.create(
            phone='13900000003',
            code='888888',
            purpose='register',
            is_used=False,
        )
        resp = self.client.post(
            '/api/register/',
            {
                'phone': '13900000003',
                'code': '888888',
                'password': 'newpass123',
                'nickname': '新用户',
            },
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('user', data)
        self.assertIn('token', data)


# ====================================================================
# 2. 打卡测试
# ====================================================================
class CheckInTests(TestCase):
    """打卡相关 API 测试"""

    def setUp(self):
        self.phone = '13900000001'
        self.password = '123456'

        self.user = User.objects.create_user(username=self.phone, password=self.password)
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone=self.phone,
            nickname='测试用户',
            age=15,
            grade='高一',
            gender='男',
            role='student',
            auth_status='approved',
        )

        # 通过 API 登录获取 token，后续请求使用 token 认证
        login_resp = self.client.post(
            '/api/login/',
            {'phone': self.phone, 'password': self.password},
            content_type='application/json',
        )
        self.token = login_resp.json()['token']

    def _auth_headers(self):
        return {'HTTP_AUTHORIZATION': f'Token {self.token}'}

    def test_unauthenticated(self):
        """未登录用户 POST /api/checkin/ 返回 401"""
        resp = self.client.post(
            '/api/checkin/',
            {
                'day': 1,
                'answer': '测试回答内容足够长',
                'online_duration': '1-2小时',
                'online_activities': '学习查资料',
                'online_impact': '学到了很多网络知识',
            },
            content_type='application/json',
            # 不带 token，模拟未登录
        )
        self.assertIn(resp.status_code, [401, 403])

    def test_checkin_success(self):
        """登录后提交正常打卡数据返回 200"""
        resp = self.client.post(
            '/api/checkin/',
            {
                'day': 1,
                'answer': '测试回答内容足够长',
                'online_duration': '1-2小时',
                'online_activities': '学习查资料',
                'online_impact': '学到了很多网络知识',
            },
            content_type='application/json',
            **self._auth_headers(),
        )
        self.assertIn(resp.status_code, [200, 201])

    def test_checkin_invalid_day(self):
        """day 超出 1-21 返回 400"""
        resp = self.client.post(
            '/api/checkin/',
            {
                'day': 99,
                'answer': '测试回答内容足够长',
                'online_duration': '1-2小时',
                'online_activities': '学习查资料',
                'online_impact': '学到了很多网络知识',
            },
            content_type='application/json',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 400)

    def test_checkin_stats(self):
        """打卡后 GET /api/checkin-stats/ 返回正确统计"""
        # 先打一次卡
        self.client.post(
            '/api/checkin/',
            {
                'day': 1,
                'answer': '测试回答内容足够长',
                'online_duration': '1-2小时',
                'online_activities': '学习查资料',
                'online_impact': '学到了很多网络知识',
            },
            content_type='application/json',
            **self._auth_headers(),
        )
        resp = self.client.get(
            '/api/checkin/stats/',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('total_days', data)
        self.assertEqual(data['total_days'], 1)
        self.assertIn('completed', data)
        self.assertFalse(data['completed'])


# ====================================================================
# 3. 答题测试
# ====================================================================
class QuizTests(TestCase):
    """答题测评相关 API 测试"""

    def setUp(self):
        self.phone = '13900000001'
        self.password = '123456'

        self.user = User.objects.create_user(username=self.phone, password=self.password)
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone=self.phone,
            nickname='测试用户',
            age=15,
            grade='高一',
            gender='男',
            role='student',
            auth_status='approved',
        )

        # 通过 API 登录获取 token
        login_resp = self.client.post(
            '/api/login/',
            {'phone': self.phone, 'password': self.password},
            content_type='application/json',
        )
        self.token = login_resp.json()['token']

        # 创建几条题目
        self.q1 = QuizQuestion.objects.create(
            q_type='choice',
            day=1,
            question='上网时下列哪种行为最安全？',
            option_a='使用复杂密码并定期更换',
            option_b='所有网站用相同密码',
            option_c='把密码告诉好朋友',
            option_d='不使用密码',
            answer='A',
            explanation='使用复杂且唯一的密码是保障账户安全的基本措施。',
        )
        self.q2 = QuizQuestion.objects.create(
            q_type='choice',
            day=1,
            question='收到陌生人发来的链接应该怎么做？',
            option_a='直接点击查看',
            option_b='不点击，先确认来源',
            option_c='转发给朋友',
            option_d='下载附件',
            answer='B',
            explanation='不随意点击不明链接是防范网络诈骗的基本常识。',
        )
        self.q3 = QuizQuestion.objects.create(
            q_type='true_false',
            day=1,
            question='在公共 Wi-Fi 上进行网银操作是安全的。',
            option_a='正确',
            option_b='错误',
            answer='B',
            explanation='公共 Wi-Fi 缺乏足够的安全保障，不建议进行敏感操作。',
        )

    def _auth_headers(self):
        return {'HTTP_AUTHORIZATION': f'Token {self.token}'}

    def test_quiz_questions(self):
        """创建 QuizQuestion 后 GET /api/quiz-questions/ 返回题目列表"""
        resp = self.client.get(
            '/api/quiz/questions/',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('questions', data)
        self.assertGreater(len(data['questions']), 0)

    def test_quiz_submit(self):
        """正确答题返回 200"""
        resp = self.client.post(
            '/api/quiz/submit/',
            {
                'day': 1,
                'answers': [
                    {'id': self.q1.id, 'answer': 'A'},
                    {'id': self.q2.id, 'answer': 'B'},
                    {'id': self.q3.id, 'answer': 'B'},
                ],
            },
            content_type='application/json',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['score'], 100)
        self.assertEqual(data['correct'], 3)
        self.assertEqual(data['total'], 3)
