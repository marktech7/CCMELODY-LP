# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
Package to test the openlp.core.lib.projector.pjlink base package.
"""
from unittest import TestCase
from unittest.mock import call, patch, MagicMock

from openlp.core.lib.projector.pjlink import PJLink
from openlp.core.lib.projector.constants import E_PARAMETER, ERROR_STRING, S_ON, S_CONNECTED

from tests.resources.projector.data import TEST_PIN, TEST_SALT, TEST_CONNECT_AUTHENTICATE, TEST_HASH

pjlink_test = PJLink(name='test', ip='127.0.0.1', pin=TEST_PIN, no_poll=True)


class TestPJLinkBase(TestCase):
    """
    Tests for the PJLink module
    """
    @patch.object(pjlink_test, 'readyRead')
    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch('openlp.core.common.qmd5_hash')
    def test_authenticated_connection_call(self,
                                           mock_qmd5_hash,
                                           mock_waitForReadyRead,
                                           mock_send_command,
                                           mock_readyRead):
        """
        Ticket 92187: Fix for projector connect with PJLink authentication exception.
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Calling check_login with authentication request:
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: Should have called qmd5_hash
        self.assertTrue(mock_qmd5_hash.called_with(TEST_SALT,
                                                   "Connection request should have been called with TEST_SALT"))
        self.assertTrue(mock_qmd5_hash.called_with(TEST_PIN,
                                                   "Connection request should have been called with TEST_PIN"))

    @patch.object(pjlink_test, 'change_status')
    def test_status_change(self, mock_change_status):
        """
        Test process_command call with ERR2 (Parameter) status
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: process_command is called with "ERR2" status from projector
        pjlink.process_command('POWR', 'ERR2')

        # THEN: change_status should have called change_status with E_UNDEFINED
        #       as first parameter
        mock_change_status.called_with(E_PARAMETER,
                                       'change_status should have been called with "{}"'.format(
                                           ERROR_STRING[E_PARAMETER]))

    @patch.object(pjlink_test, 'send_command')
    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch.object(pjlink_test, 'projectorAuthentication')
    @patch.object(pjlink_test, 'timer')
    @patch.object(pjlink_test, 'socket_timer')
    def test_bug_1593882_no_pin_authenticated_connection(self,
                                                         mock_socket_timer,
                                                         mock_timer,
                                                         mock_authentication,
                                                         mock_ready_read,
                                                         mock_send_command):
        """
        Test bug 1593882 no pin and authenticated request exception
        """
        # GIVEN: Test object and mocks
        pjlink = pjlink_test
        pjlink.pin = None
        mock_ready_read.return_value = True

        # WHEN: call with authentication request and pin not set
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: 'No Authentication' signal should have been sent
        mock_authentication.emit.assert_called_with(pjlink.ip)

    @patch.object(pjlink_test, 'waitForReadyRead')
    @patch.object(pjlink_test, 'state')
    @patch.object(pjlink_test, '_send_command')
    @patch.object(pjlink_test, 'timer')
    @patch.object(pjlink_test, 'socket_timer')
    def test_bug_1593883_pjlink_authentication(self,
                                               mock_socket_timer,
                                               mock_timer,
                                               mock_send_command,
                                               mock_state,
                                               mock_waitForReadyRead):
        """
        Test bugfix 1593883 pjlink authentication
        """
        # GIVEN: Test object and data
        pjlink = pjlink_test
        pjlink.pin = TEST_PIN
        mock_state.return_value = pjlink.ConnectedState
        mock_waitForReadyRead.return_value = True

        # WHEN: Athenticated connection is called
        pjlink.check_login(data=TEST_CONNECT_AUTHENTICATE)

        # THEN: send_command should have the proper authentication
        self.assertEqual("{test}".format(test=mock_send_command.call_args),
                         "call(data='{hash}%1CLSS ?\\r')".format(hash=TEST_HASH))

    @patch.object(pjlink_test, 'disconnect_from_host')
    def test_socket_abort(self, mock_disconnect):
        """
        Test PJLink.socket_abort calls disconnect_from_host
        """
        # GIVEN: Test object
        pjlink = pjlink_test

        # WHEN: Calling socket_abort
        pjlink.socket_abort()

        # THEN: disconnect_from_host should be called
        self.assertTrue(mock_disconnect.called, 'Should have called disconnect_from_host')

    def test_poll_loop_not_connected(self):
        """
        Test PJLink.poll_loop not connected return
        """
        # GIVEN: Test object and mocks
        pjlink = pjlink_test
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.state.return_value = False
        pjlink.ConnectedState = True

        # WHEN: PJLink.poll_loop called
        pjlink.poll_loop()

        # THEN: poll_loop should exit without calling any other method
        self.assertFalse(pjlink.timer.called, 'Should have returned without calling any other method')

    @patch.object(pjlink_test, 'send_command')
    def test_poll_loop_start(self, mock_send_command):
        """
        Test PJLink.poll_loop makes correct calls
        """
        # GIVEN: test object and test data
        pjlink = pjlink_test
        pjlink.state = MagicMock()
        pjlink.timer = MagicMock()
        pjlink.timer.interval = MagicMock()
        pjlink.timer.setInterval = MagicMock()
        pjlink.timer.start = MagicMock()
        pjlink.poll_time = 20
        pjlink.power = S_ON
        pjlink.source_available = None
        pjlink.other_info = None
        pjlink.manufacturer = None
        pjlink.model = None
        pjlink.pjlink_name = None
        pjlink.ConnectedState = S_CONNECTED
        pjlink.timer.interval.return_value = 10
        pjlink.state.return_value = S_CONNECTED
        call_list = [
            call('POWR', queue=True),
            call('ERST', queue=True),
            call('LAMP', queue=True),
            call('AVMT', queue=True),
            call('INPT', queue=True),
            call('INST', queue=True),
            call('INFO', queue=True),
            call('INF1', queue=True),
            call('INF2', queue=True),
            call('NAME', queue=True),
        ]

        # WHEN: PJLink.poll_loop is called
        pjlink.poll_loop()

        # THEN: proper calls were made to retrieve projector data
        # First, call to update the timer with the next interval
        self.assertTrue(pjlink.timer.setInterval.called, 'Should have updated the timer')
        # Next, should have called the timer to start
        self.assertTrue(pjlink.timer.start.called, 'Should have started the timer')
        # Finally, should have called send_command with a list of projetctor status checks
        mock_send_command.assert_has_calls(call_list, 'Should have queued projector queries')
