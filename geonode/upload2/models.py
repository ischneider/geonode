#########################################################################
#
# Copyright (C) 2014 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from datetime import datetime
from os import path
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db import models
import jsonfield
from geonode.upload import files
from geonode.upload2 import apps


upload_fs = FileSystemStorage(location=path.join(settings.MEDIA_ROOT, 'uploads'))


class ProcessException(Exception):
    pass


class Upload(models.Model):
    '''Represents a transfer of files either by direct user upload or another
       process'''
    uuid = models.CharField(max_length=36, unique=True, default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='junk')
    date = models.DateTimeField('date', default=datetime.now)
    name = models.TextField(null=True, blank=True)
    path = models.FilePathField(allow_files=False, allow_folders=True)

    def get_upload_path(self, child=None):
        uuid = str(self.uuid)
        if child is None:
            child = uuid
        else:
            child = path.join(uuid, child)
        return upload_fs.path(child)

    def save(self, *args, **kw):
        self.path = self.get_upload_path()
        models.Model.save(self, *args, **kw)

    def delete_files(self):
        pass


class UploadTask(models.Model):
    '''Configuration and state of processing a FileGroup'''
    configuration = jsonfield.JSONField()
    'app specific configuration'
    state = jsonfield.JSONField()
    'intermediate user input - mutable form data, etc'
    step = models.TextField(default='initial')
    'represents current state: initial, configure, ingest, publish, done'
    status = models.TextField(default='ready')
    'one of ready, queued, error'
    progress = models.TextField(null=True)
    'hold some app specific state of progress - descriptive'


class FileGroup(models.Model):
    '''A set of files that will result in one resource object'''
    upload = models.ForeignKey(Upload, null=True)
    name = models.TextField(null=True, blank=True)
    files = jsonfield.JSONField()
    '''object with `type`(a subtype of the app), `main_file`(the main file), and
    an optional other `object` with properties being lists of files. Arbitrary
    app specific config could also be stored here. Paths are relative to the
    upload root.
    for example:
        { type : 'shapefile', main_file : 'foo.shp',
          other : {
            dbf_file : [ 'foo.dbf' ],
            ...
          }
          ...
        }
    }
    '''
    app = models.TextField(null=True)
    task = models.ForeignKey(UploadTask, null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def has_all_files_needed(self):
        '''check if all files needed are present'''

    @property
    def main_file(self):
        return self.files.get('main_file', None)

    @property
    def app_file_type(self):
        return self.files.get('type', 'Unknown')

    @property
    def all_files(self, subtype=None):
        others = self.files.get('other', {})
        if subtype:
            return others.get(subtype, [])
        else:
            return reduce(lambda a,b: a.extend(b) or a, others.values(),
                          filter(None,[self.main_file]))


class _FileGroupBuilder(object):

    def __init__(self, basedir):
        self.basedir = basedir if basedir[-1] == path.sep else basedir + path.sep
        self.found = []

    def _visit_file(self, ignore, dirname, names):
        # @todo delegate fully to app
        spatial_files = files.scan_files(names)
        # @todo eventually make extensible for other apps
        relative_path = dirname.replace(self.basedir, '')
        full_paths = lambda p: [ path.join(relative_path, f) for f in p ]
        unrecognized = set(names)
        for sf in spatial_files:
            unrecognized.difference_update(sf.all_files())
            data = {
                'type' : sf.file_type.name,
                'main_file' : path.join(relative_path, sf.base_file),
                'other' : {
                    'auxillary_files' : full_paths(sf.auxillary_files),
                    'sld_files' : full_paths(sf.sld_files),
                    'xml_files' : full_paths(sf.xml_files)
                }
            }
            self.found.append(FileGroup(app='layers', files=data, name=sf.base_file))
        for f in unrecognized:
            data =  {
                'type' : 'data',
                'main_file' : path.join(relative_path, f)
            }
            self.found.append(FileGroup(app='documents', files=data, name=f))
        return self.found


def scan_files(upload):
    builder = _FileGroupBuilder(upload.get_upload_path())
    path.walk(builder.basedir, builder._visit_file, None)
    return builder.found


def get_pending_uploads(user):
    return FileGroup.objects.filter(upload__user=user, task__status='pending')


def process(file_group):
    task = file_group.task
    if task.status != 'ready':
        raise ProcessException('task is not ready')
    if task.state == 'done':
        raise ProcessException('task is done')
    app = apps.get_app(file_group.app)
    #@todo
