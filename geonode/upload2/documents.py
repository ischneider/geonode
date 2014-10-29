from geonode.upload2.apps import IngestApp
from django import forms
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from modeltranslation.forms import TranslationModelForm
from geonode.documents.models import Document

class DocumentIngestApp(IngestApp):
    name = 'documents'

    def validate(self, file_group):
        '''determine whether a file_group has all the required files'''
        return []

    def get_configuration_form(self, file_group, form_data=None):
        '''get a form for required configuration'''
        return DocumentForm(form_data)

    def configure(self, upload_task, form):
        '''configure the task from the form'''
        raise Exception('implement me')

    def ingest(self, file_group):
        '''perform any initial work'''
        pass

    def publish(self, file_group):
        raise Exception('implement me')


class DocumentForm(TranslationModelForm):
    model = Document
    resource = forms.CharField(required=False, label=_("Link to"),
    widget=TextInput(attrs={'name': 'q',
                            'id': 'resource'}))
    class Meta:
        model = Document
        fields = ['resource']