from django.urls import path
from django.conf.urls import url
from .views import LoginView, RegisterView, LogoutView, account_result
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(success_url='/'), name='login', kwargs={'authentication_form': LoginForm}),
    url(r'^register/$', view=RegisterView.as_view(success_url='/'), name='register'),
    url(r'^logout/$', view=LogoutView.as_view(), name='logout'),
    path(r'account/result.html', view=account_result, name='result')
]
