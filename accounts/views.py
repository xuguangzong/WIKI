import logging
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import logout, login, get_user_model, REDIRECT_FIELD_NAME
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, RedirectView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm, RegisterForm
from DjangoWiki.utils import get_current_site, send_email, get_md5, cache

# Create your views here.
logger = logging.getLogger(__name__)


class RegisterView(FormView):
    """
    展示对象列表（比如所有用户，所有文章）- ListView

    展示某个对象的详细信息（比如用户资料，比如文章详情) - DetailView

    通过表单创建某个对象（比如创建用户，新建文章）- CreateView

    通过表单更新某个对象信息（比如修改密码，修改文字内容）- UpdateView

    用户填写表单后转到某个完成页面 - FormView

    删除某个对象 - DeleteView
    """
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

    def form_valid(self, form):
        if form.is_valid():  # 校验字段是否都正确，例如长度，空值等
            # 当你通过表单获取你的模型数据，但是需要给模型里null=False字段添加一些非表单的数据，该方法会非常有用。
            # 如果你指定commit=False，那么save方法不会理解将表单数据存储到数据库，而是给你返回一个当前对象。
            # 这时你可以添加表单以外的额外数据，再一起存储
            user = form.save(commit=False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)
            site = get_current_site().domain
            sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            if settings.DEBUG:  # 开发环境下
                site = '127.0.0.1:8000'
            path = reverse('account:result')
            url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
                site=site, path=path, id=user.id, sign=sign)

            content = """
                        <p>请点击下面链接验证您的邮箱</p>

                            <a href="{url}" rel="bookmark">{url}</a>

                            <br />
                            如果上面链接无法打开，请将此链接复制至浏览器。
                            {url}
                        """.format(url=url)
            send_email(
                emailto=[user.email],
                title='验证您的电子邮箱',
                content=content
            )

            url = reverse('account:result') + '?type=register&id=' + str(user.id)

            return HttpResponseRedirect(url)
        else:
            return self.render_to_response({'form': form})


class LogoutView(RedirectView):
    url = '/login/'

    #  不是每个装饰器都能直接运用在类方法上，需要使用method_decorator这个装饰器的装饰器方法将装饰器运用在类方法上

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        cache.clear()  # 清除缓存
        logout(request)  # 清除session，退出登录
        return super(LogoutView, self).get(request, *args, **kwargs)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'account/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME  # 重定向的name，默认为next.

    @method_decorator(sensitive_post_parameters('password'))  # 脱敏处理，保护变量，多个装饰器放在第一个
    @method_decorator(csrf_protect)  # csrf保护，csrf_exempt是全局需要，唯独这个不需要， csrf_protect是全局不需要，唯独这个需要
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        redirect_to = self.request.GET.get(self.redirect_field_name)

        if not redirect_to:
            redirect_to = '/'
        kwargs['redirect_to'] = redirect_to

        return super(LoginView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            if cache and cache is not None:
                cache.clear()
            logger.info(self.redirect_field_name)
            login(self.request, form.get_user())  # 保持状态，写入session
            return super(LoginView, self).form_valid(form)
        else:
            return self.render_to_response({'form': form})

    def get_success_url(self):

        redirect_to = self.request.POST.get(self.redirect_field_name)
        # 如果url是安全重定向(即不会指向其他主机并使用安全方案)，则返回True。空 url 总是返回 False
        # 如果在 ALLOWED_HOSTS中 提供了指向另一个主机的URL，则该URL被认为是安全的
        # 如果参数 require_https 为True，则使用 http 方案的URL被视为不安全
        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = self.success_url
        return redirect_to


def account_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')
    # django get_object_or_404 是django shortcuts模块里面一个比较简便的方法，
    # 特别是用django get来操作数据库的时候，可以帮 我们少写一些代码，加快开发速度。
    # get_object_or_404的介绍： 我们原来调用django 的get方法，如果查询的对象不存在的话，会抛出一个DoesNotExist的异常，
    # 现在我们调用django get_object_or_404方法，它会默认的调用django 的get方法， 如果查询的对象不存在的话，会抛出一个Http404的异常
    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)

    if user.is_active:
        return HttpResponseRedirect('/')

    if type and type in ['register', 'validation']:

        if type == 'register':
            content = '''
                        恭喜您注册成功，验证邮件已经发送到您 {email} 的邮箱，请验证您的邮箱后登录本站。
                        '''.format(email=user.email)
            title = "注册成功"

        else:

            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()

            user.is_active = True
            user.save()

            content = '''
            恭喜您已经成功完成邮箱验证，现在可以使用您的账号登录本站。
            '''
            title = '验证成功'
        return render(request, 'account/result.html', {'title': title, 'content': content})
