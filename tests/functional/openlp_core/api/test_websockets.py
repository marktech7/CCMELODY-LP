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
"""
Functional tests to test the Http Server Class.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.api.poll import Poller
from openlp.core.api.websockets import WebSocketServer
from openlp.core.common.registry import Registry


@pytest.fixture
def poller(settings):
    poll = Poller()
    yield poll


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_serverstart(mocked_run_thread, MockWebSocketWorker, registry):
    """
    Test the starting of the WebSockets Server with the disabled flag set on
    """
    # GIVEN: A new httpserver
    # WHEN: I start the server
    Registry().set_flag('no_web_server', False)
    WebSocketServer()

    # THEN: the api environment should have been created
    assert mocked_run_thread.call_count == 1, 'The qthread should have been called once'
    assert MockWebSocketWorker.call_count == 1, 'The http thread should have been called once'


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_serverstart_not_required(mocked_run_thread, MockWebSocketWorker, registry):
    """
    Test the starting of the WebSockets Server with the disabled flag set off
    """
    # GIVEN: A new httpserver and the server is not required
    # WHEN: I start the server
    Registry().set_flag('no_web_server', True)
    WebSocketServer()

    # THEN: the api environment should have been created
    assert mocked_run_thread.call_count == 0, 'The qthread should not have been called'
    assert MockWebSocketWorker.call_count == 0, 'The http thread should not have been called'


def test_poll(poller, settings):
    """
    Test the poll function returns the correct JSON
    """
    # GIVEN: the system is configured with a set of data
    mocked_service_manager = MagicMock()
    mocked_service_manager.service_id = 21
    mocked_live_controller = MagicMock()
    mocked_live_controller.selected_row = 5
    mocked_live_controller.service_item = MagicMock()
    mocked_live_controller.service_item.unique_identifier = '23-34-45'
    mocked_live_controller.blank_screen.isChecked.return_value = True
    mocked_live_controller.theme_screen.isChecked.return_value = False
    mocked_live_controller.desktop_screen.isChecked.return_value = False
    Registry().register('live_controller', mocked_live_controller)
    Registry().register('service_manager', mocked_service_manager)
    # WHEN: The poller polls
    poll_json = poller.poll()
    # THEN: the live json should be generated and match expected results
    assert poll_json['results']['blank'] is True, 'The blank return value should be True'
    assert poll_json['results']['theme'] is False, 'The theme return value should be False'
    assert poll_json['results']['display'] is False, 'The display return value should be False'
    assert poll_json['results']['isSecure'] is False, 'The isSecure return value should be False'
    assert poll_json['results']['twelve'] is True, 'The twelve return value should be True'
    assert poll_json['results']['version'] == 3, 'The version return value should be 3'
    assert poll_json['results']['slide'] == 5, 'The slide return value should be 5'
    assert poll_json['results']['service'] == 21, 'The version return value should be 21'
    assert poll_json['results']['item'] == '23-34-45', 'The item return value should match 23-34-45'
