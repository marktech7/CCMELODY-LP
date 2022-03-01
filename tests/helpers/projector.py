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
Help classes/functions for PJLink Projector tests
"""

from unittest.mock import MagicMock
from PyQt5 import QtNetwork

from openlp.core.projectors.constants import S_OK, S_NOT_CONNECTED
from openlp.core.projectors.db import Projector
from tests.resources.projector.data import TEST1_DATA


class FakeProjector(object):
    """
    Helper test class
    """
    def __init__(self, port=4352, name="Faker"):
        self.link = self
        self.entry = self
        self.name = name
        self.pin = None
        self.port = port


class FakePJLinkUDP(object):
    """
    Helper test class
    """
    def __init__(self, *args, **kwargs):
        pass

    def check_settings(self, *args, **kwargs):
        pass


class FakePJLink(object):
    """
    Helper class with signals and methods mocked
    """
    def __init__(self, projector=None, *args, **kwargs):
        # Signal mocks
        self.projectorStatus = MagicMock()
        self.projectorAuthentication = MagicMock()
        self.projectorNoAuthentication = MagicMock()
        self.projectorReceivedData = MagicMock()
        self.projectorUpdateIcons = MagicMock()

        # Method mocks
        self.changeStatus = MagicMock()
        self.connect_to_host = MagicMock()
        self.disconnect_from_host = MagicMock()
        self.poll_timer = MagicMock()
        self.set_power_off = MagicMock()
        self.set_power_on = MagicMock()
        self.set_shutter_closed = MagicMock()
        self.set_shutter_open = MagicMock()
        self.socket_timer = MagicMock()
        self.status_timer = MagicMock()
        self.state = MagicMock()

        # Some tests that may include what it thinks are ProjectorItem()
        # If ProjectorItem() is called, will probably overwrite these - OK
        self.link = self
        self.pjlink = self

        # Normal entries from PJLink
        self.entry = Projector(**TEST1_DATA) if projector is None else projector
        self.ip = self.entry.ip
        self.qhost = QtNetwork.QHostAddress(self.ip)
        self.location = self.entry.location
        self.mac_adx = self.entry.mac_adx
        self.name = self.entry.name
        self.notes = self.entry.notes
        self.pin = self.entry.pin
        self.port = int(self.entry.port)
        self.pjlink_class = "1" if self.entry.pjlink_class is None else self.entry.pjlink_class
        self.poll_time = 20000 if 'poll_time' not in kwargs else kwargs['poll_time'] * 1000
        self.socket_timeout = 5000 if 'socket_timeout' not in kwargs else kwargs['socket_timeout'] * 1000
        self.no_poll = 'no_poll' in kwargs
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        self.send_queue = []
        self.priority_queue = []
        self.send_busy = False
        self.status_timer_checks = {}  # Keep track of events for the status timer
        # Default mock return values
