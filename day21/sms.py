"""
阿里云「短信认证」服务模块
专为个人开发者设计，无需企业资质、无需申请签名和模板。
使用前只需：
1. 阿里云账号完成个人实名认证
2. 开通号码认证服务中的「短信认证」功能
3. 在控制台获取赠送的签名和模板CODE
4. 创建 AccessKey
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class AliyunSMS:
    """阿里云短信认证服务封装（个人开发者可用）"""

    def __init__(self):
        self.access_key_id = settings.SMS_ACCESS_KEY_ID
        self.access_key_secret = settings.SMS_ACCESS_KEY_SECRET
        self.sign_name = settings.SMS_SIGN_NAME
        self.template_code = settings.SMS_TEMPLATE_CODE

    def send_verify_code(self, phone: str, code: str) -> bool:
        """发送短信验证码（使用短信认证API，个人用户可用）"""
        if not all([self.access_key_id, self.access_key_secret, self.sign_name, self.template_code]):
            logger.warning('短信服务未配置完整，跳过真实发送。code=%s phone=%s', code, phone)
            return False

        try:
            from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
            from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
            from alibabacloud_tea_openapi import models as open_api_models

            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
            )
            config.endpoint = 'dypnsapi.aliyuncs.com'
            client = DypnsapiClient(config)

            request = dypnsapi_models.SendSmsVerifyCodeRequest(
                phone_number=phone,
                sign_name=self.sign_name,
                template_code=self.template_code,
                template_param=json.dumps({'code': code, 'min': '5'}),
                code_length=6,
            )
            response = client.send_sms_verify_code(request)

            if response.body.code == 'OK':
                logger.info('短信发送成功 phone=%s', phone)
                return True
            else:
                logger.error('短信发送失败 phone=%s code=%s message=%s',
                             phone, response.body.code, response.body.message)
                return False

        except Exception as e:
            logger.error('短信发送异常 phone=%s error=%s', phone, e)
            return False


# 单例
_sms_client = None


def get_sms_client() -> AliyunSMS:
    global _sms_client
    if _sms_client is None:
        _sms_client = AliyunSMS()
    return _sms_client
