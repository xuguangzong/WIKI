from django.contrib.syndication.views import Feed
from wiki.models import Article
from django.conf import settings
from django.utils.feedgenerator import Rss201rev2Feed
from DjangoWiki.utils import CommonMarkdown
from django.contrib.auth import get_user_model
from datetime import datetime


class DjangoWikiFeed(Feed):
    """
    其实就是一种聚合阅读，这样可以用feedly等工具来订阅你喜欢的网站，
    这样他们的网站更新了之后你就可以通过feedly这种工具来阅读更新的内容，
    而不用跑到网站上面去查看。
    """
    feed_type = Rss201rev2Feed

    description = '小生爱吃窝窝头.'
    title = "小生爱吃窝窝头. "
    link = "/feed/"

    def author_name(self):
        return get_user_model().objects.first().nickname

    def author_link(self):
        return get_user_model().objects.first().get_absolute_url()

    def items(self):
        return Article.objects.filter(type='a', status='p').order_by('-pub_time')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return CommonMarkdown.get_markdown(item.body)

    def feed_copyright(self):
        now = datetime.now()
        return "Copyright© {year} 小生爱吃窝窝头".format(year=now.year)

    def item_link(self, item):
        return item.get_absolute_url()

    def item_guid(self, item):
        return
