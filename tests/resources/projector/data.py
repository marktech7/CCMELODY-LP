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
The :mod:`tests.resources.projector.data file contains test data
"""

from unittest.mock import MagicMock
from PyQt5 import QtNetwork
from openlp.core.projectors.constants import S_OK, S_NOT_CONNECTED

# Test data
TEST_DB_PJLINK1 = 'projector_pjlink1.sqlite'

TEST_DB = 'openlp-test-projectordb.sqlite'

TEST_SALT = '498e4a67'

TEST_PIN = 'JBMIAProjectorLink'

TEST_HASH = '5d8409bc1c3fa39749434aa3a5c38682'

TEST_CONNECT_AUTHENTICATE = 'PJLink 1 {salt}'.format(salt=TEST_SALT)

TEST1_DATA = dict(id=1,
                  ip='111.111.111.111',
                  port='1111',
                  pin='1111',
                  name='___TEST_ONE___',
                  location='location one',
                  notes='notes one',
                  serial_no='Serial Number 1',
                  sw_version='Version 1',
                  model_filter='Filter type 1',
                  model_lamp='Lamp type 1',
                  mac_adx='11:11:11:11:11:11')

TEST2_DATA = dict(id=2,
                  ip='222.222.222.222',
                  port='2222',
                  pin='2222',
                  name='___TEST_TWO___',
                  location='location two',
                  notes='notes one',
                  serial_no='Serial Number 2',
                  sw_version='Version 2',
                  model_filter='Filter type 2',
                  model_lamp='Lamp type 2',
                  mac_adx='22:22:22:22:22:22')

TEST3_DATA = dict(id=3,
                  ip='333.333.333.333',
                  port='3333',
                  pin='3333',
                  name='___TEST_THREE___',
                  location='location three',
                  notes='notes one',
                  serial_no='Serial Number 3',
                  sw_version='Version 3',
                  model_filter='Filter type 3',
                  model_lamp='Lamp type 3',
                  mac_adx='33:33:33:33:33:33')

TEST_VIDEO_CODES = {
    '11': 'RGB 1',
    '12': 'RGB 2',
    '13': 'RGB 3',
    '14': 'RGB 4',
    '15': 'RGB 5',
    '16': 'RGB 6',
    '17': 'RGB 7',
    '18': 'RGB 8',
    '19': 'RGB 9',
    '1A': 'RGB A',
    '1B': 'RGB B',
    '1C': 'RGB C',
    '1D': 'RGB D',
    '1E': 'RGB E',
    '1F': 'RGB F',
    '1G': 'RGB G',
    '1H': 'RGB H',
    '1I': 'RGB I',
    '1J': 'RGB J',
    '1K': 'RGB K',
    '1L': 'RGB L',
    '1M': 'RGB M',
    '1N': 'RGB N',
    '1O': 'RGB O',
    '1P': 'RGB P',
    '1Q': 'RGB Q',
    '1R': 'RGB R',
    '1S': 'RGB S',
    '1T': 'RGB T',
    '1U': 'RGB U',
    '1V': 'RGB V',
    '1W': 'RGB W',
    '1X': 'RGB X',
    '1Y': 'RGB Y',
    '1Z': 'RGB Z',
    '21': 'Video 1',
    '22': 'Video 2',
    '23': 'Video 3',
    '24': 'Video 4',
    '25': 'Video 5',
    '26': 'Video 6',
    '27': 'Video 7',
    '28': 'Video 8',
    '29': 'Video 9',
    '2A': 'Video A',
    '2B': 'Video B',
    '2C': 'Video C',
    '2D': 'Video D',
    '2E': 'Video E',
    '2F': 'Video F',
    '2G': 'Video G',
    '2H': 'Video H',
    '2I': 'Video I',
    '2J': 'Video J',
    '2K': 'Video K',
    '2L': 'Video L',
    '2M': 'Video M',
    '2N': 'Video N',
    '2O': 'Video O',
    '2P': 'Video P',
    '2Q': 'Video Q',
    '2R': 'Video R',
    '2S': 'Video S',
    '2T': 'Video T',
    '2U': 'Video U',
    '2V': 'Video V',
    '2W': 'Video W',
    '2X': 'Video X',
    '2Y': 'Video Y',
    '2Z': 'Video Z',
    '31': 'Digital 1',
    '32': 'Digital 2',
    '33': 'Digital 3',
    '34': 'Digital 4',
    '35': 'Digital 5',
    '36': 'Digital 6',
    '37': 'Digital 7',
    '38': 'Digital 8',
    '39': 'Digital 9',
    '3A': 'Digital A',
    '3B': 'Digital B',
    '3C': 'Digital C',
    '3D': 'Digital D',
    '3E': 'Digital E',
    '3F': 'Digital F',
    '3G': 'Digital G',
    '3H': 'Digital H',
    '3I': 'Digital I',
    '3J': 'Digital J',
    '3K': 'Digital K',
    '3L': 'Digital L',
    '3M': 'Digital M',
    '3N': 'Digital N',
    '3O': 'Digital O',
    '3P': 'Digital P',
    '3Q': 'Digital Q',
    '3R': 'Digital R',
    '3S': 'Digital S',
    '3T': 'Digital T',
    '3U': 'Digital U',
    '3V': 'Digital V',
    '3W': 'Digital W',
    '3X': 'Digital X',
    '3Y': 'Digital Y',
    '3Z': 'Digital Z',
    '41': 'Storage 1',
    '42': 'Storage 2',
    '43': 'Storage 3',
    '44': 'Storage 4',
    '45': 'Storage 5',
    '46': 'Storage 6',
    '47': 'Storage 7',
    '48': 'Storage 8',
    '49': 'Storage 9',
    '4A': 'Storage A',
    '4B': 'Storage B',
    '4C': 'Storage C',
    '4D': 'Storage D',
    '4E': 'Storage E',
    '4F': 'Storage F',
    '4G': 'Storage G',
    '4H': 'Storage H',
    '4I': 'Storage I',
    '4J': 'Storage J',
    '4K': 'Storage K',
    '4L': 'Storage L',
    '4M': 'Storage M',
    '4N': 'Storage N',
    '4O': 'Storage O',
    '4P': 'Storage P',
    '4Q': 'Storage Q',
    '4R': 'Storage R',
    '4S': 'Storage S',
    '4T': 'Storage T',
    '4U': 'Storage U',
    '4V': 'Storage V',
    '4W': 'Storage W',
    '4X': 'Storage X',
    '4Y': 'Storage Y',
    '4Z': 'Storage Z',
    '51': 'Network 1',
    '52': 'Network 2',
    '53': 'Network 3',
    '54': 'Network 4',
    '55': 'Network 5',
    '56': 'Network 6',
    '57': 'Network 7',
    '58': 'Network 8',
    '59': 'Network 9',
    '5A': 'Network A',
    '5B': 'Network B',
    '5C': 'Network C',
    '5D': 'Network D',
    '5E': 'Network E',
    '5F': 'Network F',
    '5G': 'Network G',
    '5H': 'Network H',
    '5I': 'Network I',
    '5J': 'Network J',
    '5K': 'Network K',
    '5L': 'Network L',
    '5M': 'Network M',
    '5N': 'Network N',
    '5O': 'Network O',
    '5P': 'Network P',
    '5Q': 'Network Q',
    '5R': 'Network R',
    '5S': 'Network S',
    '5T': 'Network T',
    '5U': 'Network U',
    '5V': 'Network V',
    '5W': 'Network W',
    '5X': 'Network X',
    '5Y': 'Network Y',
    '5Z': 'Network Z',
    '61': 'Internal 1',
    '62': 'Internal 2',
    '63': 'Internal 3',
    '64': 'Internal 4',
    '65': 'Internal 5',
    '66': 'Internal 6',
    '67': 'Internal 7',
    '68': 'Internal 8',
    '69': 'Internal 9',
    '6A': 'Internal A',
    '6B': 'Internal B',
    '6C': 'Internal C',
    '6D': 'Internal D',
    '6E': 'Internal E',
    '6F': 'Internal F',
    '6G': 'Internal G',
    '6H': 'Internal H',
    '6I': 'Internal I',
    '6J': 'Internal J',
    '6K': 'Internal K',
    '6L': 'Internal L',
    '6M': 'Internal M',
    '6N': 'Internal N',
    '6O': 'Internal O',
    '6P': 'Internal P',
    '6Q': 'Internal Q',
    '6R': 'Internal R',
    '6S': 'Internal S',
    '6T': 'Internal T',
    '6U': 'Internal U',
    '6V': 'Internal V',
    '6W': 'Internal W',
    '6X': 'Internal X',
    '6Y': 'Internal Y',
    '6Z': 'Internal Z'
}


class FakeProjector(object):
    """
    Helper test class
    """
    def __init__(self, port=4352, name="Faker"):
        self.link = self
        self.port = port
        self.name = name


class FakePJLink(object):
    def __init__(self, projector=None, *args, **kwargs):
        # Method/signals mocks
        self.changeStatus = MagicMock()
        self.poll_timer = MagicMock()
        self.projectorStatus = MagicMock()
        self.projectorAuthentication = MagicMock()
        self.projectorNoAuthentication = MagicMock()
        self.projectorReceivedData = MagicMock()
        self.projectorUpdateIcons = MagicMock()
        self.set_shutter_closed = MagicMock()
        self.socket_timer = MagicMock()
        self.status_timer = MagicMock()
        self.state = MagicMock()

        # Some tests that may include what it thinks are ProjectorItem()
        # If ProjectorItem() is called, will probably overwrite these - OK
        self.link = self
        self.pjlink = self

        # Normal entries from PJLink
        self.entry = TEST1_DATA if projector is None else projector
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


class FakePJLinkUDP(object):
    """
    Helper test class
    """
    def __init__(self, *args, **kwargs):
        pass

    def check_settings(self, *args, **kwargs):
        pass
