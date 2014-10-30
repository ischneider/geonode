_apps = {}

def async(func):
    func.async = True
    return func

class IngestApp(object):
    ''' Implement app specific ingestion logic.

    Lifecycle functions init, configure, ingest and publish are functions
    called if present. If using the async decorator, these operations should
    be queued.

    `init`: if present, will be called with an file_group when a FileGroup is valid

    `configure`: takes user input from a form and stores it in the UploadTask

    `ingest`: if present, takes a file_group and performs initial work,
              should not create a model

    `publish`: if present, perform an additional step

    `done`: create a model

    IngestApp must be stateless.
    '''

    def validate(self, file_group):
        '''determine whether a file_group has all the required files
        :return: list of description of missing files
        '''
        return []

    def get_configuration_form(self, file_group, form_data=None):
        '''get a form for required configuration'''
        raise Exception('implement me')

    def get_configuration_template(self, file_group):
        return 'upload2/config_template.html'

    def configure(self, upload_task, form):
        '''configure the task from the form, don't save'''
        #@todo this can have a default implementation
        raise Exception('implement me')

    def done(self, file_group):
        #@todo this can have a default implementation
        raise Exception('implement me')


def get_app(name):
    if len(_apps) == 0:
        # @todo real registry
        from geonode.upload2.layers import LayerIngestApp
        from geonode.upload2.documents import DocumentIngestApp
        _apps.update([(clz.name, clz()) for clz in (DocumentIngestApp, LayerIngestApp)])
    return _apps[name]


