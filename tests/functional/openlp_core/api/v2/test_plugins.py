# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry


# Search options tests
def test_bibles_search_options_returns_bibles_list(flask_client, settings):
    Registry().register('bible_plugin', MagicMock())
    res = flask_client.get('/api/v2/plugins/bibles/search-options').get_json()
    assert res.get('primary') == ""
    assert type(res.get('bibles')) is list


def test_bibles_set_search_options_sets_bible_version(flask_client, settings):
    Registry().register('bible_plugin', MagicMock())
    res = flask_client.post('/api/v2/plugins/bibles/search-options', json=dict(option='foo'))
    assert res.status_code == 204
    assert Registry().get('settings').value('bibles/primary bible') == 'foo'


def test_plugin_set_search_option_aborts_if_no_option(flask_client, settings):
    res = flask_client.post('/api/v2/plugins/songs/search-options')
    assert res.status_code == 400


def test_plugin_set_search_option_aborts_if_invalid_option(flask_client, settings):
    res1 = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option=['']))
    res2 = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option={1: '', 2: ''}))
    assert res1.status_code == 400
    assert res2.status_code == 400


def test_plugin_search_options_returns_plugin_exception(flask_client, settings):
    res = flask_client.get('/api/v2/plugins/songs/search-options')
    assert res.status_code == 501


def test_plugin_set_search_option_returns_plugin_exception(flask_client, settings):
    res = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option=''))
    assert res.status_code == 501
