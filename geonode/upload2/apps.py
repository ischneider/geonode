_apps = {}

class IngestApp(object):

    def validate(self, file_group):
        '''determine whether a file_group has all the required files
        :return: list of description of missing files
        '''
        raise Exception('implement me')

    def get_configuration_form(self, file_group, form_data=None):
        '''get a form for required configuration'''
        raise Exception('implement me')

    def get_configuration_template(self, file_group):
        return 'upload2/config_template.html'

    def configure(self, upload_task, form):
        '''configure the task from the form, don't save'''
        raise Exception('implement me')

    def ingest(self, file_group):
        '''perform any initial work'''
        pass

    def publish(self, file_group):
        raise Exception('implement me')


def get_app(name):
    if len(_apps) == 0:
        # @todo real registry
        from geonode.upload2.layers import LayerIngestApp
        from geonode.upload2.documents import DocumentIngestApp
        _apps.update([(clz.name, clz()) for clz in (DocumentIngestApp, LayerIngestApp)])
    return _apps[name]


