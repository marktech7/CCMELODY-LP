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
"""
Package to test the openlp.core.projectors.pjlink base package part 2.
"""
from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.constants import E_NETWORK, PJLINK_PREFIX, PJLINK_SUFFIX, QSOCKET_STATE, \
    S_CONNECTED, S_NOT_CONNECTED
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

    # ------------ Test PJLink._underscore_send_command ----------
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'write')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_network_error(self, mock_log, mock_reset, mock_state, mock_disconnect, mock_write,
                                              mock_change_status):
        """
        Test _underscore_send_command when possible network error occured
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = [call('({ip}) _send_command(): -1 received - '
                                  'disconnecting from host'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) _send_command(data="None")'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): send_queue: ['{data}\\r']".format(ip=self.pjlink.name,
                                                                                           data=test_command.strip())),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Getting normal queued packet'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Sending "{data}"'.format(ip=self.pjlink.name,
                                                                                  data=test_command.strip()))
                           ]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        mock_write.return_value = -1
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer, \
                patch.object(self.pjlink, 'waitForBytesWritten') as mock_waitBytes:
            mock_waitBytes.return_value = True
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_change_status.called_with(E_NETWORK, 'Error while sending data to projector')
            assert not self.pjlink.send_queue, 'Send queue should be empty'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert mock_timer.start.called, 'Timer should have been called'
            assert not mock_reset.called, 'reset_information() should not should have been called'
            assert mock_disconnect.called, 'disconnect_from_host() should have been called'
            assert self.pjlink.send_busy, 'send_busy should be True'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_no_data(self, mock_log, mock_reset, mock_state):
        """
        Test _underscore_send_command with no data to send
        """
        # GIVEN: Test object
        log_error_calls = []
        log_warning_calls = [call('({ip}) _send_command(): Nothing to send - returning'.format(ip=self.pjlink.name))]
        log_debug_calls = []
        mock_state.return_value = S_CONNECTED
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer:
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert not self.pjlink.send_queue, 'Send queue should be empty'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert not mock_timer.called, 'Timer should not have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'write')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_normal_send(self, mock_log, mock_reset, mock_state, mock_disconnect, mock_write):
        """
        Test _underscore_send_command using normal queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) _send_command(data="None")'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): send_queue: ['{data}\\r']".format(ip=self.pjlink.name,
                                                                                           data=test_command.strip())),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Getting normal queued packet'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Sending "{data}"'.format(ip=self.pjlink.name,
                                                                                  data=test_command.strip()))
                           ]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        mock_write.return_value = len(test_command)
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer, \
                patch.object(self.pjlink, 'waitForBytesWritten') as mock_waitBytes:
            mock_waitBytes.return_value = True
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert not self.pjlink.send_queue, 'Send queue should be empty'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert mock_timer.start.called, 'Timer should have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert not mock_disconnect.called, 'disconnect_from_host() should not have been called'
            assert self.pjlink.send_busy, 'send_busy flag should be True'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_not_connected(self, mock_log, mock_reset, mock_state, mock_disconnect):
        """
        Test _underscore_send_command when not connected
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = [call('({ip}) _send_command() Not connected - abort'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) _send_command(data="None")'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): send_queue: ['%1CLSS ?\\r']".format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Connection status: S_OK'.format(ip=self.pjlink.name))]
        mock_state.return_value = S_NOT_CONNECTED
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch here since pjlink does not have socket_timer until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer:
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert self.pjlink.send_queue == [test_command], 'Send queue should have one entry'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert not mock_timer.called, 'Timer should not have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert mock_disconnect.called, 'disconnect_from_host() should have been called'
            assert not self.pjlink.send_busy, 'send_busy flag should be False'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'write')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_priority_send(self, mock_log, mock_reset, mock_state, mock_disconnect, mock_write):
        """
        Test _underscore_send_command with priority queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) _send_command(data="{data}")'.format(ip=self.pjlink.name,
                                                                             data=test_command.strip())),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): send_queue: []'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Priority packet - '
                                'adding to priority queue'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Getting priority queued packet'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Sending "{data}"'.format(ip=self.pjlink.name,
                                                                                  data=test_command.strip()))
                           ]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        mock_write.return_value = len(test_command)
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer, \
                patch.object(self.pjlink, 'waitForBytesWritten') as mock_waitBytes:
            mock_waitBytes.return_value = True
            self.pjlink._send_command(data=test_command)

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert not self.pjlink.send_queue, 'Send queue should be empty'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert mock_timer.start.called, 'Timer should have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert not mock_disconnect.called, 'disconnect_from_host() should not have been called'
            assert self.pjlink.send_busy, 'send_busy flag should be True'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'write')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'disconnect_from_host')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_priority_send_with_normal_queue(self, mock_log, mock_reset, mock_state,
                                                                mock_disconnect, mock_write):
        """
        Test _underscore_send_command with priority queue when normal queue active
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) _send_command(data="{data}")'.format(ip=self.pjlink.name,
                                                                             data=test_command.strip())),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): send_queue: ['{data}\\r']".format(ip=self.pjlink.name,
                                                                                           data=test_command.strip())),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Priority packet - '
                                'adding to priority queue'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Getting priority queued packet'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Sending "{data}"'.format(ip=self.pjlink.name,
                                                                                  data=test_command.strip()))
                           ]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        mock_write.return_value = len(test_command)
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer, \
                patch.object(self.pjlink, 'waitForBytesWritten') as mock_waitBytes:
            mock_waitBytes.return_value = True
            self.pjlink._send_command(data=test_command)

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert self.pjlink.send_queue, 'Send queue should have one entry'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert mock_timer.start.called, 'Timer should have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert not mock_disconnect.called, 'disconnect_from_host() should not have been called'
            assert self.pjlink.send_busy, 'send_busy flag should be True'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_send_busy_normal_queue(self, mock_log, mock_reset, mock_state):
        """
        Test _underscore_send_command send_busy flag with normal queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) _send_command(data="None")'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): priority_queue: []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): send_queue: ['{data}\\r']".format(ip=self.pjlink.name,
                                                                                           data=test_command.strip())),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Still busy, returning'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Priority queue = []'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): Normal queue = "
                                "['{data}\\r']".format(ip=self.pjlink.name, data=test_command.strip()))]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_busy = True
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer:
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert self.pjlink.send_queue, 'Send queue should have one entry'
            assert not self.pjlink.priority_queue, 'Priority queue should be empty'
            assert not mock_timer.start.called, 'Timer should not have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert self.pjlink.send_busy, 'send_busy flag should be True'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_local_send_command_send_busy_priority_queue(self, mock_log, mock_reset, mock_state):
        """
        Test _underscore_send_command send_busy flag with priority queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) _send_command(data="None")'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): priority_queue: "
                                "['{data}\\r']".format(ip=self.pjlink.name,
                                                       data=test_command.strip())),
                           call('({ip}) _send_command(): send_queue: []'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Connection status: S_CONNECTED'.format(ip=self.pjlink.name)),
                           call('({ip}) _send_command(): Still busy, returning'.format(ip=self.pjlink.name)),
                           call("({ip}) _send_command(): Priority queue = "
                                "['{data}\\r']".format(ip=self.pjlink.name, data=test_command.strip())),
                           call('({ip}) _send_command(): Normal queue = []'.format(ip=self.pjlink.name))
                           ]

        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_busy = True
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = [test_command]

        # WHEN: _send_command called with no data and queue's emtpy
        # Patch some attributes here since they are not available until after instantiation
        with patch.object(self.pjlink, 'socket_timer') as mock_timer:
            self.pjlink._send_command()

            # THEN:
            mock_log.error.assert_has_calls(log_error_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.debug.assert_has_calls(log_debug_calls)
            assert not self.pjlink.send_queue, 'Send queue should be empty'
            assert self.pjlink.priority_queue, 'Priority queue should have one entry'
            assert not mock_timer.start.called, 'Timer should not have been called'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert self.pjlink.send_busy, 'send_busy flag should be True'

    # ------------ Test PJLink.send_command ----------
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_add_normal_command(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test send_command adding normal queue item
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) send_command(): Building cmd="CLSS" opts="?" '.format(ip=self.pjlink.name)),
                           call('({ip}) send_command(): Adding to normal queue'.format(ip=self.pjlink.name))]
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]

        # Patch here since pjlink does not have priority or send queue's until instantiated
        with patch.object(self.pjlink, 'send_queue') as mock_send, \
                patch.object(self.pjlink, 'priority_queue') as mock_priority:

            # WHEN: send_command called with valid normal command
            self.pjlink.send_command(cmd='CLSS')

            # THEN:
            mock_send.append.called_with(test_command)
            mock_priority.append.called is False
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.error.assert_has_calls(log_error_calls)
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_add_priority_command(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test _send_command adding priority queue item
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) send_command(): Building cmd="CLSS" opts="?" '.format(ip=self.pjlink.name)),
                           call('({ip}) send_command(): Adding to priority queue'.format(ip=self.pjlink.name))]
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]

        # Patch here since pjlink does not have priority or send queue's until instantiated
        with patch.object(self.pjlink, 'send_queue') as mock_send, \
                patch.object(self.pjlink, 'priority_queue') as mock_priority:

            # WHEN: send_command called with valid priority command
            self.pjlink.send_command(cmd='CLSS', priority=True)

            # THEN:
            mock_log.debug.assert_has_calls(log_debug_calls)
            mock_log.warning.assert_has_calls(log_warning_calls)
            mock_log.error.assert_has_calls(log_error_calls)
            mock_priority.append.assert_called_with(test_command)
            assert not mock_send.append.called, 'send_queue should not have changed'
            assert not mock_reset.called, 'reset_information() should not have been called'
            assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_duplicate_normal_command(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test send_command with duplicate item for normal queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = [call('({ip}) send_command(): Already in normal queue - '
                                  'skipping'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) send_command(cmd="CLSS" opts="?" salt="None" '
                                'priority=False'.format(ip=self.pjlink.name)),
                           call('({ip}) send_command(): Building cmd="CLSS" opts="?" '.format(ip=self.pjlink.name))]
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: send_command called with same command in normal queue
        self.pjlink.send_command(cmd='CLSS')

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert self.pjlink.send_queue == [test_command], 'Send queue should have one entry'
        assert not self.pjlink.priority_queue, 'Priority queue should be empty'
        assert not mock_reset.called, 'reset_information() should not have been called'
        assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_duplicate_priority_command(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test send_command with duplicate item for priority queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = []
        log_warning_calls = [call('({ip}) send_command(): Already in priority queue - '
                                  'skipping'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) send_command(cmd="CLSS" opts="?" salt="None" '
                                'priority=True'.format(ip=self.pjlink.name)),
                           call('({ip}) send_command(): Building cmd="CLSS" opts="?" '.format(ip=self.pjlink.name))]
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = [test_command]

        # WHEN: send_command called with same command in priority queue
        self.pjlink.send_command(cmd='CLSS', priority=True)

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert not self.pjlink.send_queue, 'Send queue should be empty'
        assert self.pjlink.priority_queue == [test_command], 'Priority queue should have one entry'
        assert not mock_reset.called, 'reset_information() should not have been called'
        assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_invalid_command_empty_queues(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test send_command with invalid command
        """
        # GIVEN: Test object
        log_error_calls = [call('({ip}) send_command(): Invalid command requested - '
                                'ignoring.'.format(ip=self.pjlink.name))]
        log_warning_calls = []
        log_debug_calls = []
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = []

        # WHEN: send_command with invalid command
        self.pjlink.send_command(cmd='DONTCARE')

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert not self.pjlink.send_queue, 'Send queue should be empty'
        assert not self.pjlink.priority_queue, 'Priority queue should be empty'
        assert not mock_reset.called, 'reset_information() should not have been called'
        assert not mock_send_command.called, '_underscore_send_command() should not have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_invalid_command_normal_queue(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test _send_command with invalid command for normal queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = [call('({ip}) send_command(): Invalid command requested - '
                                'ignoring.'.format(ip=self.pjlink.name))]
        log_warning_calls = []
        log_debug_calls = []
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_queue = [test_command]
        self.pjlink.priority_queue = []

        # WHEN: send_command with invalid command
        self.pjlink.send_command(cmd='DONTCARE')

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert self.pjlink.send_queue, 'Send queue should have one entry'
        assert not self.pjlink.priority_queue, 'Priority queue should be empty'
        assert not mock_reset.called, 'reset_information() should not have been called'
        assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_invalid_command_priority_queue(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test _send_command with invalid command for priority queue
        """
        # GIVEN: Test object
        test_command = '{prefix}{clss}CLSS ?{suff}'.format(prefix=PJLINK_PREFIX,
                                                           clss=self.pjlink.pjlink_class,
                                                           suff=PJLINK_SUFFIX)
        log_error_calls = [call('({ip}) send_command(): Invalid command requested - '
                                'ignoring.'.format(ip=self.pjlink.name))]
        log_warning_calls = []
        log_debug_calls = []
        mock_state.return_value = QSOCKET_STATE[S_CONNECTED]
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = [test_command]

        # WHEN: send_command with invalid command
        self.pjlink.send_command(cmd='DONTCARE', priority=True)

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert not self.pjlink.send_queue, 'Send queue should be empty'
        assert self.pjlink.priority_queue, 'Priority queue should have one entry'
        assert not mock_reset.called, 'reset_information() should not have been called'
        assert mock_send_command.called, '_underscore_send_command() should have been called'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'state')
    @patch.object(openlp.core.projectors.pjlink.PJLink, 'reset_information')
    @patch.object(openlp.core.projectors.pjlink.PJLink, '_send_command')
    @patch.object(openlp.core.projectors.pjlink, 'log')
    def test_send_command_not_connected(self, mock_log, mock_send_command, mock_reset, mock_state):
        """
        Test send_command when not connected
        """
        # GIVEN: Test object
        log_error_calls = []
        log_warning_calls = [call('({ip}) send_command(): Not connected - returning'.format(ip=self.pjlink.name))]
        log_debug_calls = []
        mock_state.return_value = S_NOT_CONNECTED
        self.pjlink.send_queue = []
        self.pjlink.priority_queue = []

        # WHEN: send_command called when not connected
        self.pjlink.send_command(cmd=None)

        # THEN:
        mock_log.debug.assert_has_calls(log_debug_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.error.assert_has_calls(log_error_calls)
        assert not self.pjlink.send_queue, 'Send queue should be empty'
        assert not self.pjlink.priority_queue, 'Priority queue should be empty'
        assert mock_reset.called, 'reset_information() should have been called'
        assert not mock_send_command.called, '_underscore_send_command() should not have been called'
