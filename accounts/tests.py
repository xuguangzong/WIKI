from django.utils import timezone
from django.test import TestCase, Client, RequestFactory
from accounts.models import WikiUser
from django.urls import reverse
from DjangoWiki.utils import *
from django.conf import settings
from wiki.models import Article, Category


# Create your tests here.


class AccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_account(self):
        site = get_current_site().domain
        user = WikiUser.objects.create_superuser(
            email="2359301733@qq.com",
            username="2359301733",
            password="123qaz456WSX"
        )
        testuser = WikiUser.objects.get(username="2359301733")

        loginresult = self.client.login(
            username="2359301733",
            password="123qaz456WSX"
        )
        self.assertEqual(loginresult, True)  # 判定是否相等

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)
        category = Category()
        category.name = "categoryaaa"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.title = "nicetitleaaa"
        article.body = "nicecontentaaa"
        article.author = user
        article.category = category
        article.type = 'a'
        article.status = 'p'
        article.save()
        response = self.client.get(article.get_admin_url())
        self.assertEqual(response.status_code, 200)

    def test_validate_register(self):
        self.assertEqual(
            0, len(
                WikiUser.objects.filter(email="2359301733@qq.com")
            )
        )
        response = self.client.post(reverse('account:register'), {
            "username": "2359301733",
            "email": "2359301733@qq.com",
            "password1": "123qaz456WSX",
            "password2": "123qaz456WSX",
        })
        self.assertEqual(
            1, len(
                WikiUser.objects.filter(email="2359301733@qq.com")
            )
        )
        user = WikiUser.objects.filter(email="2359301733@qq.com")[0]
        sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
        path = reverse('accounts:result')
        url = '{path}?type=validation&id={id}&sign={sign}'.format(
            path=path, id=user.id, sign=sign)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username="2359301733", password="123qaz456WSX")
        user = WikiUser.objects.filter(email="2359301733@qq.com")[0]
        user.is_superuser = True
        user.is_staff = True
        user.save()
        delete_sidebar_cache(user.username)
        category = Category()
        category.name = "categoryaaa"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.category = category
        article.title = "nicetitle333"
        article.body = "nicecontentttt"
        article.author = user

        article.type = 'a'
        article.status = 'p'
        article.save()

        response = self.client.get(article.get_admin_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('account:logout'))
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.get(article.get_admin_url())
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.post(reverse('account:login'), {
            'username': 'user1233',
            'password': 'password123'
        })
        self.assertIn(response.status_code, [301, 302, 200])

        response = self.client.get(article.get_admin_url())
        self.assertIn(response.status_code, [301, 302, 200])