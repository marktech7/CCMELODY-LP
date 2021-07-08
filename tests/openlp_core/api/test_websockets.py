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
from openlp.core.api.websocketspollermanager import WebSocketPollerManager
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.api.websocketspoll import WebSocketPoller
from openlp.core.api.websockets import WebSocketWorker, WebSocketServer
from openlp.core.common.registry import Registry


@pytest.fixture
def poller(settings):
    poll = WebSocketPoller()
    yield poll


@pytest.fixture
def worker(settings):
    worker = WebSocketWorker()
    yield worker


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
def test_poller_manager(mocked_run_thread, MockWebSocketWorker, registry):
    """
    Test if the poller manager is registered inside Registry when web server is required
    """

    # GIVEN: A new websocketServer and mocked Registry, server is not required
    Registry().set_flag('no_web_server', False)
    # WHEN: I start the server
    WebSocketServer()

    # THEN: the WebSocketPollerRegister should be registered
    assert isinstance(Registry().get('poller_manager'), WebSocketPollerManager)


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_poller_manager_serverstart_not_required(mocked_run_thread, MockWebSocketWorker, registry):
    """
    Test the starting of the WebSockets Poller Manager if web server is not required
    """
    # GIVEN: A new httpserver and the server is not required
    Registry().set_flag('no_web_server', True)
    # WHEN: I start the server
    WebSocketServer()

    # THEN: the WebSocketPollerRegister should be registered
    assert isinstance(Registry().get('poller_manager'), WebSocketPollerManager)


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_serverstart_not_required(mocked_run_thread, MockWebSocketWorker, registry):
    """
    Test the starting of the WebSockets Server with the disabled flag set off
    """
    # GIVEN: A new httpserver and the server is not required
    Registry().set_flag('no_web_server', True)
    # WHEN: I start the server
    WebSocketServer()

    # THEN: the api environment should have been created
    assert mocked_run_thread.call_count == 0, 'The qthread should not have been called'
    assert MockWebSocketWorker.call_count == 0, 'The http thread should not have been called'


def test_poller_get_state(poller, settings):
    """
    Test the get_state function returns the correct JSON
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
    poll_json = poller.get_state()
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


def test_poller_get_state_if_changed(poller, settings):
    """
    Test the get_state_if_changed function returns None if the state has not changed
    """
    # GIVEN: the system is configured with a set of data
    poller._previous = {}
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
    # WHEN: The poller polls twice
    poll_json = poller.get_state_if_changed()
    poll_json2 = poller.get_state_if_changed()
    # THEN: The get_state_if_changed function should return None on the second call because the state has not changed
    assert poll_json is not None, 'The first get_state_if_changed function call should have not returned None'
    assert poll_json2 is None, 'The second get_state_if_changed function should return None'


@patch('openlp.core.api.websockets.serve')
@patch('openlp.core.api.websockets.asyncio')
@patch('openlp.core.api.websockets.log')
def test_worker_start(mocked_log, mocked_asyncio, mocked_serve, worker, settings):
    """
    Test the start function of the worker
    """
    # GIVEN: A mocked serve function and event loop
    mocked_serve.return_value = 'server_thing'
    event_loop = MagicMock()
    mocked_asyncio.new_event_loop.return_value = event_loop
    # WHEN: The start function is called
    worker.start()
    # THEN: No error occurs
    mocked_serve.assert_called_once()
    event_loop.run_until_complete.assert_called_once_with('server_thing')
    event_loop.run_forever.assert_called_once_with()
    mocked_log.exception.assert_not_called()
    # Because run_forever is mocked, it doesn't stall the thread so close will be called immediately
    event_loop.close.assert_called_once_with()


@patch('openlp.core.api.websockets.serve')
@patch('openlp.core.api.websockets.asyncio')
@patch('openlp.core.api.websockets.log')
def test_worker_start_fail(mocked_log, mocked_asyncio, mocked_serve, worker, settings):
    """
    Test the start function of the worker handles a error nicely
    """
    # GIVEN: A mocked serve function and event loop. run_until_complete returns a error
    mocked_serve.return_value = 'server_thing'
    event_loop = MagicMock()
    mocked_asyncio.new_event_loop.return_value = event_loop
    event_loop.run_until_complete.side_effect = Exception()
    # WHEN: The start function is called
    worker.start()
    # THEN: An exception is logged but is handled and the event_loop is closed
    mocked_serve.assert_called_once()
    event_loop.run_until_complete.assert_called_once_with('server_thing')
    event_loop.run_forever.assert_not_called()
    mocked_log.exception.assert_called_once()
    event_loop.close.assert_called_once_with()


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_poller_manager_add_sub_item(mocked_run_thread, MockWebSocketWorker, poller, settings):
    """
    Test if WebSocketPollerManager's add_sub_item adds item to WebSocketPoll
    """
    # GIVEN: A test sub key, a test dictionary and mocked program state
    test_key = 'test'
    test_dict = {
        'test1': 2,
        'test2': 'A test',
        'test3': [4]
    }
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
    Registry().set_flag('no_web_server', False)

    # WHEN: I start the server, add a item using add_sub_item, and poll the state
    WebSocketServer()
    Registry().get('poller_manager').add_sub_item('test', test_dict)
    poll_json = poller.get_state()

    # THEN: the poll_json should contain inserted dictionary
    assert poll_json['results'][test_key] == test_dict


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_poller_manager_remove_sub_item(mocked_run_thread, MockWebSocketWorker, poller, settings):
    """
    Test if WebSocketPollerManager's remove_sub_item removes item from WebSocketPoll
    """
    # GIVEN: A test sub key, a test dictionary and mocked program state
    test_key = 'test'
    test_dict = {
        'test1': 2,
        'test2': 'A test',
        'test3': [4]
    }
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
    Registry().set_flag('no_web_server', False)

    # WHEN: I start the server, add a item using add_sub_item, remove same item
    # using and remove_sub_item, and poll the state
    WebSocketServer()
    Registry().get('poller_manager').add_sub_item('test', test_dict)
    Registry().get('poller_manager').remove_sub_item('test')
    poll_json = poller.get_state()

    # THEN: the poll_json should not contain inserted dictionary
    assert test_key not in poll_json['results']


@patch('openlp.core.api.websockets.WebSocketWorker')
@patch('openlp.core.api.websockets.run_thread')
def test_poller_manager_cannot_replace_native_item(mocked_run_thread, MockWebSocketWorker, poller, settings):
    """
    Test if WebSocketPollerManager's add_sub_item doesn't replace native poll items
    """
    # GIVEN: A test sub key, a test dictionary and mocked program state
    test_key = 'item'
    test_dict = {
        'test1': 2,
        'test2': 'A test',
        'test3': [4]
    }
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
    Registry().set_flag('no_web_server', False)

    # WHEN: I start the server, add a item using add_sub_item
    WebSocketServer()
    Registry().get('poller_manager').add_sub_item(test_key, test_dict)
    poll_json = poller.get_state()

    # THEN: the poll_json should not contain inserted dictionary
    assert poll_json['results'][test_key] != test_dict
