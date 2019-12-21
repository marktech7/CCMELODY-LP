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
Package to test the openlp.core.projectors.pjlink base package part 3.
"""
from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_CLASS, STATUS_CODE, \
    S_NOT_CONNECTED, S_OFF, S_ON, QSOCKET_STATE
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLink module
    """
    def setUp(self):
        """
        Initialize test state(s)
        """
        # Default PJLink instance for tests
        self.pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        """
        Cleanup test state(s)
        """
        del(self.pjlink)

    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_projector_reset_information(self, mock_log):
        """
        Test reset_information() resets all information and stops timers
        """
        # GIVEN: Test object
        log_debug_calls = [call('({ip}) reset_information() connect status is '
                                'S_NOT_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}): Calling poll_timer.stop()'.format(ip=self.pjlink.name)),
                           call('({ip}): Calling socket_timer.stop()'.format(ip=self.pjlink.name)),
                           call('({ip}): Calling status_timer.stop()'.format(ip=self.pjlink.name))]

        # Attributes not available until instantiation, so mock here
        with patch.object(self.pjlink, 'socket_timer') as mock_socket_timer, \
                patch.object(self.pjlink, 'status_timer') as mock_status_timer, \
                patch.object(self.pjlink, 'poll_timer') as mock_poll_timer, \
                patch.object(self.pjlink, 'state') as mock_state:
            mock_state.return_value = QSOCKET_STATE[S_NOT_CONNECTED]
            # Set attributes to something other than None or {} or []
            self.pjlink.fan = True
            self.pjlink.filter_time = True
            self.pjlink.lamp = True
            self.pjlink.mac_adx_received = 'Some random MAC'
            self.pjlink.manufacturer = 'PJLINK'
            self.pjlink.model = '1'
            self.pjlink.model_filter = 'Filter'
            self.pjlink.model_lamp = 'Lamp'
            self.pjlink.mute = True
            self.pjlink.other_info = 'Another Test'
            self.pjlink.pjlink_class = 2
            self.pjlink.pjlink_name = 'OPENLPTEST'
            self.pjlink.power = S_ON
            self.pjlink.projector_errors = {'test1': True, 'test2': False}
            self.pjlink.serial_no = 'Some Number'
            self.pjlink.serial_no_received = 'Some Other Number'
            self.pjlink.sw_version = 'Some Version'
            self.pjlink.sw_version_received = 'Some Other Version'
            self.pjlink.shutter = True
            self.pjlink.source_available = True
            self.pjlink.source = True
            self.pjlink.status_timer_checks = {'test1': object(), 'test2': object()}
            self.pjlink.send_busy = False
            self.pjlink.send_queue = ['test1', 'test2']
            self.pjlink.priority_queue = ['test1', 'test2']

            # WHEN: reset_information() is called
            self.pjlink.reset_information()

            # THEN: All information should be reset and timers stopped
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert self.pjlink.fan is None, 'fan should be None'
            assert self.pjlink.filter_time is None, 'filter_time should be None'
            assert self.pjlink.lamp is None, 'lamp should be None'
            assert self.pjlink.mac_adx_received is None, 'mac_adx_received should be None'
            assert self.pjlink.manufacturer is None, 'manufacturer should be None'
            assert self.pjlink.model is None, 'model should be None'
            assert self.pjlink.model_filter is None, 'model_filter should be None'
            assert self.pjlink.model_lamp is None, 'model_lamp should be None'
            assert not self.pjlink.mute, 'mute should be False'
            assert self.pjlink.other_info is None, 'other should be None'
            assert self.pjlink.pjlink_class == PJLINK_CLASS, 'pjlink_class should be {cls}'.format(cls=PJLINK_CLASS)
            assert self.pjlink.pjlink_name is None, 'pjlink_name should be None'
            assert self.pjlink.power == S_OFF, 'power should be {data}'.format(data=STATUS_CODE[S_OFF])
            assert self.pjlink.projector_errors == {}, 'projector_errors should be an empty dict'
            assert self.pjlink.serial_no is None, 'serial_no should be None'
            assert self.pjlink.serial_no_received is None, 'serial_no_received should be None'
            assert self.pjlink.sw_version is None, 'sw_version should be None'
            assert self.pjlink.sw_version_received is None, 'sw_version_received should be None'
            assert not self.pjlink.shutter, 'shutter should be False'
            assert self.pjlink.source_available is None, 'source_available should be None'
            assert self.pjlink.source is None, 'source should be None'
            assert self.pjlink.status_timer_checks == {}, 'status_timer_checks should be an empty dict'
            assert not self.pjlink.send_busy, 'send_busy should be False'
            assert self.pjlink.send_queue == [], 'send_queue should be an empty list'
            assert self.pjlink.priority_queue == [], 'priority_queue should be an empty list'
            assert mock_socket_timer.stop.called, 'socket_timer.stop() should have been called'
            assert mock_status_timer.stop.called, 'status_timer.stop() should have been called'
            assert mock_poll_timer.stop.called, 'poll_timer.stop() should have been called'
