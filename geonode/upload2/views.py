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
import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic import ListView
from geonode.upload2.apps import get_app
from geonode.upload2.models import Upload
from geonode.upload2.models import UploadTask
from geonode.upload2.models import FileGroup
from geonode.upload2.models import scan_files
from geonode.upload2.models import get_pending_uploads
from geonode.utils import json_response
import logging

logger = logging.getLogger(__name__)


#@todo view to update an upload?
# like if a user forgets a file
# only possible if incomplete FileGroup?

#@todo view to update FileGroup
# assign from one to another (this SLD goes with this layer)
# ignore
# change app



@login_required
def upload(req):
    if req.method == 'GET' or len(req.FILES) == 0:
        return render_to_response('upload2/new_upload.html', RequestContext(req,{
            'pending': get_pending_uploads(req.user).count()
        }))

    upload = Upload(user=req.user)
    try:
        received = _receive_files(upload, req.FILES.getlist('files'))
        # @todo implement upload size limit? and provide client check
        # @todo unpacking be done asynchronously?
        _unpack_files(received)
    except:
        logger.exception("snap")
        # @todo could there be a reason to keep?
        # errors might result from incomplete transfer, so probably delete
        upload.delete_files()
        raise

    # @todo specified permissions should be defaults for FileGroups that can
    # be overridden

    file_groups = scan_files(upload)
    upload.save()
    for f in file_groups:
        f.task = UploadTask.objects.create(status='pending')
        f.upload = upload
        f.save()

    redirect = reverse('upload_detail', kwargs=dict(slug=upload.uuid))
    return HttpResponseRedirect(redirect)


def _receive_files(upload, files):
    '''write a sequence of UploadedFile into the Upload model workspace'''
    paths = []
    os.makedirs(upload.get_upload_path())
    for f in files:
        dest = upload.get_upload_path(f.name)
        paths.append(dest)
        with open(dest, 'wb') as writable:
            for c in f.chunks():
                writable.write(c)
    return paths


def _unpack_files(files):
    '''scan and unpack any archives'''
    # @todo what if a user wants to have an archive be used as a document?
    #       perhaps an option on upload to publish as is?
    # @todo safely unpack archive files (check for bad paths first)
    # @todo what if two archives are uploaded that might contain duplicate names
    #       perhaps if >1 archive, unpack to archive basename subdirectory?
    return files


def _redirect(req, default):
    return HttpResponseRedirect(_redirect_next(req, default))


def _redirect_next(req, default):
    return req.GET.get('next', default)


class UploadDetail(DetailView):
    model = Upload
    slug_field = 'uuid'


class PendingFileGroups(ListView):
    model = FileGroup
    def get_queryset(self):
        return get_pending_uploads(self.request.user)


@login_required
def upload_group_configure(req, id):
    fg = get_object_or_404(FileGroup, pk=id)
    if fg.upload.user != req.user:
        raise PermissionDenied()
    app = get_app(fg.app)
    template = app.get_configuration_template(fg)
    form = app.get_configuration_form(fg, req.POST)
    default_redirect = reverse('upload_pending')
    if req.method == 'POST':
        if form.is_valid():
            app.configure(fg.task, form)
            fg.task.save()
            return _redirect(req, default_redirect)

    return  render_to_response(template, RequestContext(req,{
        'file_group' : fg,
        'form' : form,
        'next' : _redirect_next(req, default_redirect)
    }))


@login_required
def upload_group_ingest(req, id):
    fg = get_object_or_404(FileGroup, pk=id)
    if fg.upload.user != req.user:
        raise PermissionDenied()
    app = get_app(fg.app)
    if getattr(app.ingest, 'async', False):
        tasks.ingest.apply_async(args=[id], queue='upload')
    else:
        return HttpResponseRedirect(app.ingest(fg, fg.upload.user))


@login_required
@require_POST
def queue(req):
    todo

