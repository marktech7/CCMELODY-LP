# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################

import requests

from openlp.core.common import Settings, registry
from openlp.core.lib.db import Manager
from openlp.plugins.remotesync.lib.backends.synchronizer import Synchronizer
from openlp.plugins.songs.lib.db import init_schema, Song


class WebServiceSynchronizer(Synchronizer):
    baseurl = 'http://localhost:8000/'
    auth_token = 'afd9a4aa979534edf0015f7379cd6d61a52f9e10'

    def __init__(self, *args, **kwargs):
        port = kwargs['port']
        address = kwargs['address']
        self.auth_token = kwargs['auth_token']
        self.base_url = '{}:{}/'.format(address, port)
        self.manager = registry.Registry().get('songs_manager')
        registry.Registry().register('remote_synchronizer', self)

    @staticmethod
    def _handle(response, expected_status_code=200):
        if response.status_code != expected_status_code:
            print('whoops got {} expected {}'.format(response.status_code, expected_status_code))
        return response

    def _get(self, url):
        return self._handle(requests.get(url, headers={'Authorization': 'access_token {}'.format(self.auth_token)}),
                            200)

    def _post(self, url, data, return_code):
        return self._handle(requests.post(url, headers={'Authorization': 'access_token {}'.format(self.auth_token)},
                                          json=data), return_code)

    def _put(self, url, data):
        return self._handle(requests.put(url, headers={'Authorization': 'access_token {}'.format(self.auth_token)},
                                         data=data))

    def _delete(self, url):
        return self._handle(requests.delete(url, headers={'Authorization': 'access_token {}'.format(self.auth_token)}))

    def check_connection(self):
        return False

    def send_song(self, song):
        self._post('http://localhost:8000/songs/', song, 201)

    def receive_songs(self):
        self._get('http://localhost:8000/songs/')

    def send_all_songs(self):
        for song in self.manager.get_all_objects(Song):
            self._post('http://localhost:8000/songs/', self.open_lyrics.song_to_xml(song), 201)
