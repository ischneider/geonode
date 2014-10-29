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
    '''Configuration of how to process a FileGroup'''
    # @todo - need to solidify/encapsulate JSON API
    configuration = jsonfield.JSONField()
    status = models.TextField(null=True)


class FileGroup(models.Model):
    '''A set of files that will result in one resource object'''
    upload = models.ForeignKey(Upload, null=True)
    # @todo - need to solidify/encapsulate JSON API
    name = models.TextField(null=True, blank=True)
    files = jsonfield.JSONField()
    app = models.TextField(null=True)
    task = models.ForeignKey(UploadTask, null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def has_all_files_needed(self):
        '''check if all files needed are present'''



class UploadTaskResult(models.Model):
    status = models.TextField()
    result = jsonfield.JSONField()


def _visit_file(collect, dirname, names):
    spatial_files = files.scan_files(names)
    # @todo eventually make extensible for other apps
    full_paths = lambda p: [ path.join(dirname, f) for f in p ]
    unrecognized = set(names)
    for sf in spatial_files:
        unrecognized.difference_update(sf.all_files())
        data = {
            'type' : sf.file_type.name,
            'base_file' : path.join(dirname, sf.base_file),
            'auxillary_files' : full_paths(sf.auxillary_files),
            'sld_files' : full_paths(sf.sld_files),
            'xml_files' : full_paths(sf.xml_files)
        }
        collect.append(FileGroup(app='layers', files=data, name=sf.base_file))
    for f in unrecognized:
        data =  {
            'type' : 'data',
            'base_file' : path.join(dirname, f)
        }
        collect.append(FileGroup(app='documents', files=data, name=f))
    return collect


def scan_files(upload):
    found = []
    path.walk(upload.get_upload_path(), _visit_file, found)
    return found