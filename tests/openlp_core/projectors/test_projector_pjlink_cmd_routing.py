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
Package to test the openlp.core.projectors.pjlink command routing.
"""

from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import PJLINK_PREFIX
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkRouting(TestCase):
    """
    Tests for the PJLink module command routing
    """
    def setUp(self):
        """
        Setup test environment
        """
        self.pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        """
        Reset test environment
        """
        del(self.pjlink)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'process_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_projector_get_data_invalid_version(self, mock_log, mock_process_cmd):
        """
        Test projector received valid command invalid version
        """
        # GIVEN: Test object
        log_warning_text = [call('({ip}) _send_command(): Nothing to send - returning'.format(ip=self.pjlink.name)),
                            call('({ip}) get_data() Command reply version does not match '
                                 'a valid command version'.format(ip=self.pjlink.name))]
        log_debug_text = [call('({ip}) get_data(buffer="{pre}XCLSS=X"'.format(ip=self.pjlink.name, pre=PJLINK_PREFIX)),
                          call('({ip}) get_data(): Checking new data "{pre}XCLSS=X"'.format(ip=self.pjlink.name,
                                                                                            pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() header="{pre}XCLSS" data="X"'.format(ip=self.pjlink.name,
                                                                                       pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() version="X" cmd="CLSS" data="X"'.format(ip=self.pjlink.name)),
                          call('({ip}) Cleaning buffer - msg = "get_data() Command reply version does '
                               'not match a valid command version"'.format(ip=self.pjlink.name)),
                          call('({ip}) Finished cleaning buffer - 0 bytes dropped'.format(ip=self.pjlink.name))]
        # WHEN: get_data called with an unknown command
        self.pjlink.get_data(buff='{prefix}XCLSS=X'.format(prefix=PJLINK_PREFIX))

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (mock_process_cmd.call_count == 0), 'process_command should not have been called'

    @patch.object(openlp.core.projectors.pjlinkcommands, 'process_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_projector_get_data_unknown_command(self, mock_log, mock_process_cmd):
        """
        Test projector receiving invalid command
        """
        # GIVEN: Test object
        log_warning_text = [call('({ip}) _send_command(): Nothing to send - '
                                 'returning'.format(ip=self.pjlink.name)),
                            call('({ip}) get_data(): Invalid packet - '
                                 'unknown command "UNKN"'.format(ip=self.pjlink.name))]
        log_debug_text = [call('({ip}) get_data(buffer="{pre}1UNKN=Huh?"'.format(ip=self.pjlink.name,
                                                                                 pre=PJLINK_PREFIX)),
                          call('({ip}) get_data(): Checking new data "{pre}1UNKN=Huh?"'.format(ip=self.pjlink.name,
                                                                                               pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() header="{pre}1UNKN" data="Huh?"'.format(ip=self.pjlink.name,
                                                                                          pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() version="1" cmd="UNKN" data="Huh?"'.format(ip=self.pjlink.name)),
                          call('({ip}) Cleaning buffer - msg = "get_data(): Invalid packet - '
                               'unknown command "UNKN""'.format(ip=self.pjlink.name)),
                          call('({ip}) Finished cleaning buffer - 0 bytes dropped'.format(ip=self.pjlink.name))]

        # WHEN: get_data called with an unknown command
        self.pjlink.get_data(buff='{prefix}1UNKN=Huh?'.format(prefix=PJLINK_PREFIX))

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (mock_process_cmd.call_count == 0), 'process_command should not have been called'

    @patch.object(openlp.core.projectors.pjlinkcommands, 'process_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_projector_get_data_version_mismatch(self, mock_log, mock_process_cmd):
        """
        Test projector received valid command with command version higher than projector
        """
        # GIVEN: Test object
        log_warning_text = [call('({ip}) _send_command(): Nothing to send - returning'.format(ip=self.pjlink.name)),
                            call('({ip}) get_data(): Projector returned class reply higher than projector '
                                 'stated class'.format(ip=self.pjlink.name))]

        log_debug_text = [call('({ip}) get_data(buffer="{pre}2ACKN=X"'.format(ip=self.pjlink.name,
                                                                              pre=PJLINK_PREFIX)),
                          call('({ip}) get_data(): Checking new data "{pre}2ACKN=X"'.format(ip=self.pjlink.name,
                                                                                            pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() header="{pre}2ACKN" data="X"'.format(ip=self.pjlink.name,
                                                                                       pre=PJLINK_PREFIX)),
                          call('({ip}) get_data() version="2" cmd="ACKN" data="X"'.format(ip=self.pjlink.name))]
        self.pjlink.pjlink_class = '1'

        # WHEN: get_data called with an unknown command
        self.pjlink.get_data(buff='{prefix}2ACKN=X'.format(prefix=PJLINK_PREFIX))

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (mock_process_cmd.call_count == 0), 'process_command should not have been called'
