# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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

from zeroconf import ServiceInfo, Zeroconf, Error, NonUniqueNameException

from openlp.core.common import get_network_interfaces
from openlp.core.common.i18n import UiStrings
from openlp.core.common.registry import Registry
from openlp.core.threading import ThreadWorker, run_thread


def _get_error_message(exc):
    """
    Zeroconf doesn't have error messages, so we have to make up our own
    """
    error_message = UiStrings().ZeroconfErrorIntro + '\n\n'
    if isinstance(exc, NonUniqueNameException):
        error_message += UiStrings().ZeroconfNonUniqueError
    else:
        error_message += UiStrings().ZeroconfGenericError
    return error_message


class ZeroconfWorker(ThreadWorker):
    """
    This thread worker runs a Zeroconf service
    """
    ip_address = None
    http_port = 4316
    ws_port = 4317
    _can_run = False

    def __init__(self, addresses, http_port=4316, ws_port=4317):
        """
        Create the worker for the Zeroconf service
        """
        super().__init__()
        self.addresses = addresses
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
        addresses = [socket.inet_aton(addr) for addr in self.addresses]
        http_info = ServiceInfo('_http._tcp.local.', 'OpenLP._http._tcp.local.',
                                addresses=addresses, port=self.http_port, properties={})
        ws_info = ServiceInfo('_ws._tcp.local.', 'OpenLP._ws._tcp.local.',
                              addresses=addresses, port=self.ws_port, properties={})
        zc = None
        try:
            zc = Zeroconf()
            zc.register_service(http_info)
            zc.register_service(ws_info)
            self._can_run = True
            while self.can_run():
                sleep(0.1)
        except Error as e:
            self.error.emit('Cannot start Zeroconf service', _get_error_message(e))
        except OSError as e:
            self.error.emit('Cannot start Zeroconf service', str(e))
        finally:
            if zc is not None:
                zc.unregister_all_services()
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
    http_port = Registry().get('settings_thread').value('api/port')
    ws_port = Registry().get('settings_thread').value('api/websocket port')
    worker = ZeroconfWorker([iface['ip'] for iface in get_network_interfaces().values()], http_port, ws_port)
    run_thread(worker, 'api_zeroconf')
