from django.db import models
from django.urls import reverse
from DjangoWiki.utils import get_current_site
from django.contrib.auth.models import AbstractUser  # 使用django自带的user model 又想有其余的field，可以扩展AbstractUser类


# Create your models here.


class WikiUser(AbstractUser):
    """
    null ：针对数据库，如果 null=True, 表示数据库的该字段可以为空，即在Null字段显示为YES。
    blank ：针对表单，如果 blank=True，表示你的表单填写该字段时可以不填，但是对数据库来说，没有任何影响
    """

    nickname = models.CharField(verbose_name="昵称", max_length=100, blank=True)
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    last_mod_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)
    source = models.CharField(verbose_name="创建来源", max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse('wiki:author_detail', kwargs={'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domain  # 获得站点
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ['-id']  # 返回数据按照id降序
        verbose_name = "用户"  # 给模型起别名
        verbose_name_plural = verbose_name  # 模型的复数形式是什么
        get_latest_by = "id"  # 最近一行记录 按照id排
