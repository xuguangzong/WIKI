from django.forms import widgets
from django.contrib.auth import get_user_model  # 获取user模型对象
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "用户名", "class": "form-control"})
        self.fields['password'].widget = widgets.PasswordInput(attrs={'placeholder': "密码", "class": "form-control"})


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "用户名", "class": "form-control"})
        self.fields['email'].widget = widgets.EmailInput(attrs={'placeholder': "邮箱", "class": "form-control"})
        self.fields['password1'].widget = widgets.PasswordInput(attrs={'placeholder': "密码", "class": "form-control"})
        self.fields['password2'].widget = widgets.PasswordInput(attrs={'placeholder': "确认密码", "class": "form-control"})

    def clean_email(self):

        email = self.cleaned_data['email']
        # 判定 这个邮箱存不存在
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("该邮箱已存在")
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
