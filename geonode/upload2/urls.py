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
from django.conf.urls import patterns, url
from geonode.upload2.views import UploadDetail
from geonode.upload2.views import PendingFileGroups

urlpatterns = patterns('geonode.upload2.views',
                       url(r'^new/$', 'upload', name='upload_new'),
                       url(r'^(?P<slug>([a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12}?))$',
                           UploadDetail.as_view(), name='upload_detail'),
                       url(r'^group/(?P<id>\d+)$', 'upload_group_configure', name='upload_group_configure'),
                       url(r'^group/(?P<id>\d+)/ingest$', 'upload_group_ingest', name='upload_group_ingest'),
                       url(r'^pending', PendingFileGroups.as_view(), name='upload_pending'),
                       )
