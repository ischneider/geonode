import os
from geonode.upload2.apps import IngestApp
from django import forms
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from modeltranslation.forms import TranslationModelForm
from geonode.documents.models import Document
from geonode.documents.forms import DocumentCreateForm
from django.core.files import File


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
        upload_task.state['form'] = form.cleaned_data

    def ingest(self, file_group, user):
        form_data = file_group.task.state['form']
        doc = Document(
            title=form_data['title'], 
            doc_file=File(open(os.path.join(file_group.upload.get_upload_path(),file_group.main_file))),
            owner = user
            )
        doc.save()
        file_group.task.status = 'done'
        file_group.task.save()
        return doc.get_absolute_url()


class DocumentForm(TranslationModelForm):
    title = forms.CharField(required=True, label=_("Title"))
    resource = forms.CharField(required=False, label=_("Link to"),
    widget=TextInput(attrs={'name': 'q',
                            'id': 'resource',
                            'placeholder':'This does not work - needs JS',
                            'size' : 60}))
    class Meta:
        model = Document
        fields = ['resource']