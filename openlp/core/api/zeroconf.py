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
"""
The :mod:`~openlp.core.api.zeroconf` module runs a Zerconf server so that OpenLP can advertise the
RESTful API for devices on the network to discover.
"""
import socket
from time import sleep

from zeroconf import ServiceInfo, Zeroconf

from openlp.core.common import get_network_interfaces
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.threading import ThreadWorker, run_thread


class ZeroconfWorker(ThreadWorker):
    """
    This thread worker runs a Zeroconf service
    """
    address = None
    http_port = 4316
    ws_port = 4317
    _can_run = False

    def __init__(self, ip_address, http_port=4316, ws_port=4317):
        """
        Create the worker for the Zeroconf service
        """
        super().__init__()
        self.address = socket.inet_aton(ip_address)
        self.http_port = http_port
        self.ws_port = ws_port

    def can_run(self):
        """
        Check if the worker can continue to run. This is mostly so that we can override this method
        and test the class.
        """
        return self._can_run

    def start(self):
        """
        Start the service
        """
        http_info = ServiceInfo('_http._tcp.local.', 'OpenLP._http._tcp.local.',
                                address=self.address, port=self.http_port, properties={})
        ws_info = ServiceInfo('_ws._tcp.local.', 'OpenLP._ws._tcp.local.',
                              address=self.address, port=self.ws_port, properties={})
        zc = Zeroconf()
        zc.register_service(http_info)
        zc.register_service(ws_info)
        self._can_run = True
        while self.can_run():
            sleep(0.1)
        zc.unregister_service(http_info)
        zc.unregister_service(ws_info)
        zc.close()
        self.quit.emit()

    def stop(self):
        """
        Stop the service
        """
        self._can_run = False


def start_zeroconf():
    """
    Start the Zeroconf service
    """
    # When we're running tests, just skip this set up if this flag is set
    if Registry().get_flag('no_web_server'):
        return
    http_port = Settings().value('api/port')
    ws_port = Settings().value('api/websocket port')
    for name, interface in get_network_interfaces().items():
        worker = ZeroconfWorker(interface['ip'], http_port, ws_port)
        run_thread(worker, 'api_zeroconf_{name}'.format(name=name))
