from wiki.documents import ElapsedTimeDocument, ArticleDocumentManager

from django.core.management.base import BaseCommand
from wiki.models import Article


# TODO 参数化
class Command(BaseCommand):
    help = 'build search index'

    def handle(self, *args, **options):
        manager = ArticleDocumentManager()
        manager.delete_index()
        manager.rebuild()

        manager = ElapsedTimeDocument()
        manager.init()
