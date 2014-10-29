from geonode.upload2.apps import IngestApp

class LayerIngestApp(IngestApp):
    name = 'layers'

    def validate(self, file_group):
        '''determine whether a file_group has all the required files'''
        return []

    def get_configuration_form(self, file_group):
        '''get a form for required configuration'''
        raise Exception('implement me')

    def configure(self, upload_task, form):
        '''configure the task from the form'''
        raise Exception('implement me')

    def ingest(self, file_group):
        '''perform any initial work'''
        pass

    def publish(self, file_group):
        raise Exception('implement me')