from django.test import Client, RequestFactory, TestCase
from wiki.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.urls import reverse
import datetime
from DjangoWiki.utils import *


class DjangoWikiTest(TestCase):
    def setUp(self):
        pass

    def test_utils(self):
        md5 = get_md5('test')
        self.assertIsNotNone(md5)
        c = CommonMarkdown.get_markdown('''
        # Title1

        ```python
        import os
        ```


        [ddd](http://www.baidu.com)


        ''')
        self.assertIsNotNone(c)
        d = {
            'd': 'key1',
            'd2': 'key2'
        }
        data = parse_dict_to_url(d)
        self.assertIsNotNone(data)
        render = WikiMarkDownRenderer()
        s = render.autolink('http://www.baidu.com')
        self.assertTrue(s.find('nofollow') > 0)
        s = render.link('http://www.baidu.com', 'test', 'test')
        self.assertTrue(s.find('nofollow') > 0)
