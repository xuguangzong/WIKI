from haystack.forms import SearchForm
from django import forms
import logging

logger = logging.getLogger(__name__)


class WikiSearchForm(SearchForm):
    querydata = forms.CharField(required=True)

    def search(self):
        datas = super(WikiSearchForm, self).search()
        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['querydata']:
            logger.info(self.cleaned_data['querydata'])
        return datas
