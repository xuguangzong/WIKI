from django.forms import widgets
from django.contrib.auth import get_user_model  # 获取user模型对象
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "username", "class": "form-control"})
        self.fields['password'].widget = widgets.TextInput(attrs={'placeholder': "password", "class": "form-control"})


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': "username", "class": "form-control"})
        self.fields['email'].widget = widgets.TextInput(attrs={'placeholder': "email", "class": "form-control"})
        self.fields['password1'].widget = widgets.TextInput(attrs={'placeholder': "password1", "class": "form-control"})
        self.fields['password2'].widget = widgets.TextInput(attrs={'placeholder': "password2", "class": "form-control"})

    def clean_email(self):

        email = self.cleaned_data['email']
        # 判定 这个邮箱存不存在
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("该邮箱已存在")
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")