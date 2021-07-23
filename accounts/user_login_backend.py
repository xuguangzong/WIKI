from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend  # 默认的验证类，作为自定义验证类的父类


class EmailOrUsernameModelBackend(ModelBackend):
    """
    允许使用用户名或邮箱登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):  # 这里的check_password就是把密码加密之后进行验证
                return user
        except get_user_model().DoesNotExist:  # 如果异常就证明用户不存在
            return None

    def get_user(self, username):

        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None
