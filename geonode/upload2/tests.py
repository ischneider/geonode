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
from geonode.upload2.models import _visit_file
from geonode.upload2.models import Upload
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


def test_scanning():
    found = _visit_file([], 'place', ['a.shp','a.DBF','x.doc'])
    def get(name):
        for f in found:
            if f.files['base_file'].startswith(name):
                return f
    assert len(found) == 2
    assert get('place/a').files['base_file'] == 'place/a.shp'


class ViewTests(TestCase):

    fixtures = ['bobby']

    def setUp(self):
        self.user = 'bobby'
        self.pwd = 'bob'
        self.layer_upload_url = reverse('upload_new')
        self.client = Client()

    def login(self):
        self.client.login(username=self.user, password=self.pwd)

    def upload(self, payload):
        resp = self.client.post(self.layer_upload_url, payload)
        self.assertEqual(resp.status_code, 302)
        return resp

    def test_upload(self):
        self.login()
        self.upload({
            'somefile' : open('README', 'rb')
        })
        upload = Upload.objects.latest('id')
