"""DjangoBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^wiki/', include('wiki.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from DjangoWiki.sitemap import StaticViewSitemap, ArticleSiteMap, CategorySiteMap, TagSiteMap, UserSiteMap
from DjangoWiki.feeds import DjangoWikiFeed
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls.static import static
from DjangoWiki.admin_site import admin_site
from django.urls import include, path

sitemaps = {

    'wiki': ArticleSiteMap,
    'Category': CategorySiteMap,
    'Tag': TagSiteMap,
    'User': UserSiteMap,
    'static': StaticViewSitemap
}

handler404 = 'wiki.views.page_not_found_view'
handler500 = 'wiki.views.server_error_view'
handle403 = 'wiki.views.permission_denied_view'
urlpatterns = [
    url(r'^admin/', admin_site.urls),
    url(r'', include('wiki.urls', namespace='wiki')),
    url(r'mdeditor/', include('mdeditor.urls')),
    url(r'', include('comments.urls', namespace='comment')),
    url(r'', include('accounts.urls', namespace='account')),
    url(r'', include('oauth.urls', namespace='oauth')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^feed/$', DjangoWikiFeed()),
    url(r'^rss/$', DjangoWikiFeed()),
    url(r'^search', include('haystack.urls'), name='search'),
    url(r'', include('servermanager.urls', namespace='servermanager')),
    url(r'', include('owntracks.urls', namespace='owntracks'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
