from django.contrib.admin import AdminSite
from DjangoWiki.utils import get_current_site
from django.contrib.sites.admin import SiteAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.sites.models import Site
from DjangoWiki.logentryadmin import LogEntryAdmin
from wiki.admin import *
from accounts.admin import *
from oauth.admin import *
from servermanager.admin import *
from comments.admin import *
from owntracks.admin import *


class DjangoWikiAdminSite(AdminSite):
    """
    重写admin登录界面
    """
    site_header = 'DjangoWiki administration'
    site_title = 'DjangoWiki site admin'

    def __init__(self, name='admin'):
        super().__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser


admin_site = DjangoWikiAdminSite(name='admin')

admin_site.register(Article, ArticlelAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(Links, LinksAdmin)
admin_site.register(SideBar, SideBarAdmin)
admin_site.register(WikiSettings, WikiSettingsAdmin)
admin_site.register(commands, CommandsAdmin)
admin_site.register(EmailSendLog, EmailSendLogAdmin)

admin_site.register(WikiUser, WikiUserAdmin)

admin_site.register(Comment, CommentAdmin)

admin_site.register(OAuthUser, OAuthUserAdmin)
admin_site.register(OAuthConfig, OAuthConfigAdmin)

admin_site.register(OwnTrackLog, OwnTrackLogsAdmin)

admin_site.register(Site, SiteAdmin)

admin_site.register(LogEntry, LogEntryAdmin)
