from django.db import models

# Create your models here.
import logging
from uuslug import slugify  # 能够将中文转化为拼音
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from abc import abstractmethod
from DjangoWiki.utils import get_current_site, cache_decorator, cache
from mdeditor.fields import MDTextField

logger = logging.getLogger(__name__)


class LinkShowType(models.TextChoices):
    I = ('i', '首页')
    L = ('l', '列表页')
    P = ('p', '文章页面')
    A = ('a', '全站')
    S = ('s', '友情链接页面')


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)  # 设置id为自增主键
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)  # 添加字段说明，当内容添加时自动添加当前时间
    last_mod_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)  # 当内容修改时自动修改当前时间

    def save(self, *args, **kwargs):
        """
        重写save方法
        :param args:
        :param kwargs:
        :return:
        """
        is_update_views = isinstance(self, Article) and 'update_fields' in kwargs and kwargs['update_fields'] == [
            'views']
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if 'slug' in self.__dict__:
                slug = getattr(self, 'title') if 'title' in self.__dict__ else getattr(self, 'name')
                setattr(self, 'slug', slugify(slug))
            super().save(*args, **kwargs)

    def get_full_url(self):

        site = get_current_site.domain()
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        """
        abstract = True
        这个属性是定义当前的模型类是不是一个抽象类。
        所谓抽象类是不会生成相应数据库表的。
        一般我们用它来归纳一些公共属性字段，然后继承它的子类能够继承这些字段
        """
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        """
        加上@abc.abstractmethod装饰器后严格控制子类必须实现这个方法
        """
        pass


class Article(BaseModel):
    """
    文章
    """
    STATUS_CHOICES = (
        ('d', '草稿'),  # draft
        ('p', '发表')  # publish
    )

    COMMENT_STATUS = (
        ('o', '打开'),  # open
        ('c', '关闭')  # close
    )
    TYPE = (
        ('a', '文章'),  # article
        ('p', '页面')  # page
    )
    title = models.CharField(verbose_name="标题", max_length=200, unique=True)  # 设置唯一约束
    body = MDTextField()  # 使用Markdown编辑模型中的字段，我们只需TextField将模型的替换为 MDTextField
    pub_time = models.DateTimeField(verbose_name="发布时间", blank=False, null=False, auto_now_add=True)
    status = models.CharField(verbose_name="文章状态", max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField(verbose_name="评论状态", max_length=1, choices=COMMENT_STATUS, default='o')
    type = models.CharField(verbose_name="文章类型", max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField(verbose_name="浏览量", default=0)
    # blank用于表单的认证，被设为blank=False（默认为False）的字段在填写表单时不能为空。
    # null用于规定数据库中的列的非空性
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="作者", blank=False, null=False, on_delete=models.CASCADE)
    article_order = models.IntegerField(verbose_name="排序，数字越大越靠前", blank=False, null=False, default=0)
    category = models.ForeignKey(to="Category", verbose_name="分类", blank=False, null=False, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to="Tag", verbose_name="标签集合", blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-article_order", "-pub_time"]
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('wiki:detailbyid', kwargs={
            'article_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def viewed(self):

        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info('set article comments:{id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True)
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments:{id}'.format(id=self.id))
            return comments

    def get_admin_ur(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    # gt 大于，gte大于等于 lt小于，lte小于等于
    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # 下一篇
        return Article.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # 前一篇
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
    """文章分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    parent_category = models.ForeignKey(
        'self',
        verbose_name="父级分类",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)  # 存储网址字段格式 减号、下划线、字母、数字

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse(
            'wiki:category_detail', kwargs={
                'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """
        递归获得分类目录的父级
        :return:
        """
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """
        获得当前分类目录所有子集
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys


class Tag(BaseModel):
    """文章标签"""
    name = models.CharField('标签名', max_length=30, unique=True)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wiki:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class Links(models.Model):
    """友情链接"""

    name = models.CharField('链接名称', max_length=30, unique=True)
    link = models.URLField('链接地址')  # 带有URL合法性校验的CharField
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField(
        '是否显示', default=True, blank=False, null=False)
    show_type = models.CharField(
        '显示类型',
        max_length=1,
        choices=LinkShowType.choices,
        default=LinkShowType.I)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """侧边栏,可以展示一些html内容"""
    name = models.CharField('标题', max_length=100)
    content = models.TextField("内容")
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField('是否启用', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = '侧边栏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class WikiSettings(models.Model):
    """站点设置"""
    sitename = models.CharField(
        "网站名称",
        max_length=200,
        null=False,
        blank=False,
        default='')
    site_description = models.TextField(
        "网站描述",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    site_seo_description = models.TextField(
        "网站SEO描述", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField(
        "网站关键字",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    article_sub_length = models.IntegerField("文章摘要长度", default=300)
    sidebar_article_count = models.IntegerField("侧边栏文章数目", default=10)
    sidebar_comment_count = models.IntegerField("侧边栏评论数目", default=5)
    show_google_adsense = models.BooleanField('是否显示谷歌广告', default=False)
    google_adsense_codes = models.TextField(
        '广告内容', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField('是否打开网站评论功能', default=True)
    beiancode = models.CharField(
        '备案号',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    analyticscode = models.TextField(
        "网站统计代码",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    show_gongan_code = models.BooleanField(
        '是否显示公安备案号', default=False, null=False)
    gongan_beiancode = models.TextField(
        '公安备案号',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    resource_path = models.CharField(
        "静态文件保存地址",
        max_length=300,
        null=False,
        default='/var/www/resource/')

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if WikiSettings.objects.exclude(id=self.id).count():  # exclude 除了当前id
            raise ValidationError(_('只能有一个配置'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from DjangoWiki.utils import cache
        cache.clear()
