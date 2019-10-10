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
Package to test the openlp.core.projectors.pjlink command routing.
"""

from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import E_AUTHENTICATION, E_PARAMETER, E_PROJECTOR, E_UNAVAILABLE, E_UNDEFINED, \
    S_DATA_OK, PJLINK_ERRORS, STATUS_MSG
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

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_command(self, mock_log):
        """
        Test process_command receiving command not in function map
        """
        # GIVEN: Test setup
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "1"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=self.pjlink.name))]

        # WHEN: called with valid command and data
        chk = process_command(projector=self.pjlink, cmd='CLSS', data='1')

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk is None), 'process_clss() should have returned None'

    @patch.object(openlp.core.projectors.pjlinkcommands, 'process_clss')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'pjlink_functions')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_command_unknown(self, mock_log, mock_functions, mock_clss):
        """
        Test process_command receiving command not in function map
        """
        # GIVEN: Test setup
        log_warning_text = [call('({ip}) Unable to process command="CLSS" '
                                 '(Future option?)'.format(ip=self.pjlink.name))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "?"'.format(ip=self.pjlink.name))]
        # Fake CLSS command is not in list
        mock_functions.__contains__.return_value = False

        # WHEN: called with unknown command
        process_command(projector=self.pjlink, cmd='CLSS', data='?')

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (mock_functions.__contains__.call_count == 1), 'pjlink_functions should have been accessed only once'
        assert (not mock_clss.called), 'Should not have called process_clss'

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'process_clss')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_data_ok(self, mock_log, mock_clss, mock_send):
        """
        Test process_command calls function and sets appropriate value(s) in projector instance
        """
        # GIVEN: Test setup
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "OK"'.format(ip=self.pjlink.name)),
                          call('({ip}) Command "CLSS" returned OK'.format(ip=self.pjlink.name))
                          ]

        # WHEN: Command called with OK
        chk = process_command(projector=self.pjlink, cmd='CLSS', data='OK')

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.debug.asset_has_calls(log_debug_text)
        mock_send.assert_not_called()
        mock_clss.assert_not_called()
        assert (chk == S_DATA_OK), 'Should have returned S_DATA_OK'

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_pjink_err1(self, mock_log):
        """
        Test rouing when PJLink ERR1 received
        """
        # GIVEN: Test setup
        err_code = E_UNDEFINED
        err_msg = STATUS_MSG[err_code]
        err_str = PJLINK_ERRORS[err_code]

        log_error_text = [call('({ip}) CLSS: {err}'.format(ip=self.pjlink.name, err=err_msg))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "{err}"'.format(ip=self.pjlink.name,
                                                                                           err=err_str))]

        # WHEN: routing called
        chk = process_command(projector=self.pjlink, cmd='CLSS', data=err_str)

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.error.assert_has_calls(log_error_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk == err_code), 'Should have returned {err}'.format(err=PJLINK_ERRORS[err_code])

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_pjink_err2(self, mock_log):
        """
        Test rouing when PJLink ERR2 received
        """
        # GIVEN: Test setup
        err_code = E_PARAMETER
        err_msg = STATUS_MSG[err_code]
        err_str = PJLINK_ERRORS[err_code]

        log_error_text = [call('({ip}) CLSS: {err}'.format(ip=self.pjlink.name, err=err_msg))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "{err}"'.format(ip=self.pjlink.name,
                                                                                           err=err_str))]

        # WHEN: routing called
        chk = process_command(projector=self.pjlink, cmd='CLSS', data=err_str)

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.error.assert_has_calls(log_error_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk == err_code), 'Should have returned {err}'.format(err=PJLINK_ERRORS[err_code])

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_pjink_err3(self, mock_log):
        """
        Test rouing when PJLink ERR3 received
        """
        # GIVEN: Test setup
        err_code = E_UNAVAILABLE
        err_msg = STATUS_MSG[err_code]
        err_str = PJLINK_ERRORS[err_code]

        log_error_text = [call('({ip}) CLSS: {err}'.format(ip=self.pjlink.name, err=err_msg))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "{err}"'.format(ip=self.pjlink.name,
                                                                                           err=err_str))]

        # WHEN: routing called
        chk = process_command(projector=self.pjlink, cmd='CLSS', data=err_str)

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.error.assert_has_calls(log_error_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk == err_code), 'Should have returned {err}'.format(err=PJLINK_ERRORS[err_code])

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_pjink_err4(self, mock_log):
        """
        Test rouing when PJLink ERR4 received
        """
        # GIVEN: Test setup
        err_code = E_PROJECTOR
        err_msg = STATUS_MSG[err_code]
        err_str = PJLINK_ERRORS[err_code]

        log_error_text = [call('({ip}) CLSS: {err}'.format(ip=self.pjlink.name, err=err_msg))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "{err}"'.format(ip=self.pjlink.name,
                                                                                           err=err_str))]

        # WHEN: routing called
        chk = process_command(projector=self.pjlink, cmd='CLSS', data=err_str)

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.error.assert_has_calls(log_error_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk == err_code), 'Should have returned {err}'.format(err=PJLINK_ERRORS[err_code])

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_routing_pjink_errA(self, mock_log):
        """
        Test rouing when PJLink ERRA received
        """
        # GIVEN: Test setup
        err_code = E_AUTHENTICATION
        err_msg = STATUS_MSG[err_code]
        err_str = PJLINK_ERRORS[err_code]

        log_error_text = [call('({ip}) CLSS: {err}'.format(ip=self.pjlink.name, err=err_msg))]
        log_debug_text = [call('({ip}) Processing command "CLSS" with data "{err}"'.format(ip=self.pjlink.name,
                                                                                           err=err_str))]

        # WHEN: routing called
        chk = process_command(projector=self.pjlink, cmd='CLSS', data=err_str)

        # THEN: Appropriate log entries should have been made and methods called/not called
        mock_log.error.assert_has_calls(log_error_text)
        mock_log.debug.assert_has_calls(log_debug_text)
        assert (chk == err_code), 'Should have returned {err}'.format(err=PJLINK_ERRORS[err_code])
