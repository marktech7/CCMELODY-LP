# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2028-2022 OpenLP Developers                              #
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
from openlp.core.common.enum import PluginStatus


# Search options tests
def test_bibles_search_options_returns_list(flask_client, settings):
    """
    Test a list is returned when a plugin's search options are requested.

    Returns an empty list here because the plugin is mocked so there are no options.
    """
    # GIVEN: A mocked plugin
    mock_plugin_manager = MagicMock()
    mock_plugin_manager.get_plugin_by_name.return_value = MagicMock()
    Registry().register('plugin_manager', mock_plugin_manager)

    # WHEN: Search options are requested
    res = flask_client.get('/api/v2/plugins/bibles/search-options').get_json()

    # THEN: A empty list should be returned
    assert res == []


def test_bibles_set_search_options_sets_bible_version(flask_client, settings):
    """
    Test that a search option post request sends the correct values to the plugin,
    and returns the correct status code.
    """
    # GIVEN: A mocked bible plugin
    mock_plugin_manager = MagicMock()
    mock_bible_plugin = MagicMock()
    mock_bible_plugin.status = PluginStatus.Active
    mock_bible_plugin.media_item = MagicMock(set_search_option=MagicMock(return_value=True))
    mock_plugin_manager.get_plugin_by_name.return_value = mock_bible_plugin
    Registry().register('plugin_manager', mock_plugin_manager)

    # WHEN: The primary bible is requested to change via the api
    res = flask_client.post('/api/v2/plugins/bibles/search-options', json=dict(option='primary bible', value='foo'))

    # THEN: Returns correct status code and sends correct values to plugin.
    assert res.status_code == 204
    mock_bible_plugin.media_item.set_search_option.assert_called_once_with('primary bible', 'foo')


def test_plugin_set_search_option_aborts_if_no_option(flask_client, settings):
    Registry().register('plugin_manager', MagicMock())
    res = flask_client.post('/api/v2/plugins/songs/search-options')
    assert res.status_code == 400


def test_plugin_set_search_option_aborts_if_invalid_option(flask_client, settings):
    Registry().register('plugin_manager', MagicMock())
    res1 = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option=['']))
    res2 = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option={1: '', 2: ''}))
    assert res1.status_code == 400
    assert res2.status_code == 400


def test_plugin_search_options_returns_no_search_options(flask_client, settings):
    Registry().register('plugin_manager', MagicMock())
    res = flask_client.get('/api/v2/plugins/songs/search-options')
    assert res.status_code == 200


def test_plugin_set_search_option_returns_plugin_exception(flask_client, settings):
    Registry().register('plugin_manager', MagicMock())
    res = flask_client.post('/api/v2/plugins/songs/search-options', json=dict(option=''))
    assert res.status_code == 400
