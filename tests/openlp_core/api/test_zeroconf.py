# -*- coding: utf-8 -*-

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
from unittest.mock import MagicMock, call, patch

from openlp.core.api.zeroconf import ZeroconfWorker, start_zeroconf


@patch('openlp.core.api.zeroconf.socket.inet_aton')
def test_zeroconf_worker_constructor(mocked_inet_aton):
    """Test creating the Zeroconf worker object"""
    # GIVEN: A ZeroconfWorker class and a mocked inet_aton
    mocked_inet_aton.return_value = 'processed_ip'

    # WHEN: An instance of the ZeroconfWorker is created
    worker = ZeroconfWorker('127.0.0.1', 8000, 8001)

    # THEN: The inet_aton function should have been called and the attrs should be set
    mocked_inet_aton.assert_called_once_with('127.0.0.1')
    assert worker.address == 'processed_ip'
    assert worker.http_port == 8000
    assert worker.ws_port == 8001


@patch('openlp.core.api.zeroconf.ServiceInfo')
@patch('openlp.core.api.zeroconf.Zeroconf')
def test_zeroconf_worker_start(MockedZeroconf, MockedServiceInfo):
    """Test the start() method of ZeroconfWorker"""
    # GIVEN: A few mocks and a ZeroconfWorker instance with a mocked can_run method
    mocked_http_info = MagicMock()
    mocked_ws_info = MagicMock()
    mocked_zc = MagicMock()
    MockedServiceInfo.side_effect = [mocked_http_info, mocked_ws_info]
    MockedZeroconf.return_value = mocked_zc
    worker = ZeroconfWorker('127.0.0.1', 8000, 8001)

    # WHEN: The start() method is called
    with patch.object(worker, 'can_run') as mocked_can_run:
        mocked_can_run.side_effect = [True, False]
        worker.start()

    # THEN: The correct calls are made
    assert MockedServiceInfo.call_args_list == [
        call('_http._tcp.local.', 'OpenLP._http._tcp.local.', address=b'\x7f\x00\x00\x01', port=8000, properties={}),
        call('_ws._tcp.local.', 'OpenLP._ws._tcp.local.', address=b'\x7f\x00\x00\x01', port=8001, properties={})
    ]
    assert MockedZeroconf.call_count == 1
    assert mocked_zc.register_service.call_args_list == [call(mocked_http_info), call(mocked_ws_info)]
    assert mocked_can_run.call_count == 2
    assert mocked_zc.unregister_service.call_args_list == [call(mocked_http_info), call(mocked_ws_info)]
    assert mocked_zc.close.call_count == 1


def test_zeroconf_worker_stop():
    """Test that the ZeroconfWorker.stop() method correctly stops the service"""
    # GIVEN: A worker object with _can_run set to True
    worker = ZeroconfWorker('127.0.0.1', 8000, 8001)
    worker._can_run = True

    # WHEN: stop() is called
    worker.stop()

    # THEN: _can_run should be False
    assert worker.can_run() is False


@patch('openlp.core.api.zeroconf.get_network_interfaces')
@patch('openlp.core.api.zeroconf.Registry')
@patch('openlp.core.api.zeroconf.Settings')
@patch('openlp.core.api.zeroconf.ZeroconfWorker')
@patch('openlp.core.api.zeroconf.run_thread')
def test_start_zeroconf(mocked_run_thread, MockedZeroconfWorker, MockedSettings, MockedRegistry,
                        mocked_get_network_interfaces):
    """Test the start_zeroconf() function"""
    # GIVEN: A whole bunch of stuff that's mocked out
    mocked_get_network_interfaces.return_value = {
        'eth0': {
            'ip': '192.168.1.191',
            'broadcast': '192.168.1.255',
            'netmask': '255.255.255.0',
            'prefix': 24,
            'localnet': '192.168.1.0'
        }
    }
    MockedRegistry.return_value.get_flag.return_value = False
    MockedSettings.return_value.value.side_effect = [8000, 8001]
    mocked_worker = MagicMock()
    MockedZeroconfWorker.return_value = mocked_worker

    # WHEN: start_zeroconf() is called
    start_zeroconf()

    # THEN: A worker is added to the list of threads
    mocked_run_thread.assert_called_once_with(mocked_worker, 'api_zeroconf_eth0')
