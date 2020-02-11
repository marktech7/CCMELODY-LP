# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
import pytest
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry


def test_retrieve_live_item(flask_client):
    pytest.skip()
    res = flask_client.get('/api/v2/controller/live-item').get_json()
    assert len(res) == 0


def test_controller_set_requires_login(settings, flask_client):
    settings.setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/controller/show', json=dict())
    settings.setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_controller_set_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/controller/show')
    assert res.status_code == 405


def test_controller_set_calls_live_controller(flask_client, settings):
    fake_live_controller = MagicMock()
    Registry().register('live_controller', fake_live_controller)
    res = flask_client.post('/api/v2/controller/show', json=dict(id=400))
    assert res.status_code == 204
    fake_live_controller.slidecontroller_live_set.emit.assert_called_once_with([400])


def test_controller_direction_requires_login(flask_client, settings):
    settings.setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/controller/progress', json=dict())
    settings.setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_controller_direction_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/controller/progress')
    assert res.status_code == 405


def test_controller_direction_does_fails_on_wrong_data(flask_client, settings):
    res = flask_client.post('/api/v2/controller/progress', json=dict(action='foo'))
    assert res.status_code == 400


def test_controller_direction_calls_service_manager(flask_client, settings):
    fake_live_controller = MagicMock()
    Registry().register('live_controller', fake_live_controller)
    res = flask_client.post('/api/v2/controller/progress', json=dict(action='next'))
    assert res.status_code == 204
    fake_live_controller.slidecontroller_live_next.emit.assert_called_once()
