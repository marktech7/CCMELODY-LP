# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest import TestCase
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import E_ERROR, E_WARN, PJLINK_ERST_DATA, PJLINK_ERST_STATUS, S_OK
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkCommands(TestCase):
    """
    Tests PJLink commands part 1
    """
    def setUp(self):
        """
        Initial test setup
        """
        self.pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        """
        Test reset
        """
        del(self.pjlink)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_audio_muted(self, mock_log, mock_UpdateIcons):
        """
        Test avmt status shutter unchanged and mute on
        """
        # GIVEN: Test setup
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "21"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting speaker to muted'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = True
        self.pjlink.mute = False

        # WHEN: Called with setting shutter closed and mute on
        process_command(projector=self.pjlink, cmd='AVMT', data='21')

        # THEN: Shutter should be closed and mute should be True
        assert self.pjlink.shutter, 'Shutter should not have changed'
        assert self.pjlink.mute, 'Audio should be off'
        assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_bad_data(self, mock_log, mock_UpdateIcons):
        """
        Test avmt bad data fail
        """
        # GIVEN: Test object
        log_warning_text = [call('({ip}) Invalid av mute response: 36'.format(ip=self.pjlink.name))]
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "36"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = True
        self.pjlink.mute = True

        # WHEN: Called with an invalid setting
        process_command(projector=self.pjlink, cmd='AVMT', data='36')

        # THEN: Shutter should be closed and mute should be True
        assert self.pjlink.shutter, 'Shutter should changed'
        assert self.pjlink.mute, 'Audio should not have changed'
        assert not mock_UpdateIcons.emit.called, 'Update icons should NOT have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_closed_muted(self, mock_log, mock_UpdateIcons):
        """
        Test avmt status shutter closed and mute off
        """
        # GIVEN: Test object
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "31"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting shutter to closed'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting speaker to muted'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = False
        self.pjlink.mute = False

        # WHEN: Called with setting shutter to closed and mute on
        process_command(projector=self.pjlink, cmd='AVMT', data='31')

        # THEN: Shutter should be closed and mute should be True
        assert self.pjlink.shutter, 'Shutter should have been set to closed'
        assert self.pjlink.mute, 'Audio should be muted'
        assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_open_unmuted(self, mock_log, mock_UpdateIcons):
        """
        Test avmt status shutter open and mute off
        """
        # GIVEN: Test object
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "30"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting shutter to open'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting speaker to normal'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = True
        self.pjlink.mute = True

        # WHEN: Called with setting shutter to closed and mute on
        process_command(projector=self.pjlink, cmd='AVMT', data='30')

        # THEN: Shutter should be closed and mute should be True
        assert not self.pjlink.shutter, 'Shutter should have been set to off'
        assert not self.pjlink.mute, 'Audio should be on'
        assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_shutter_closed(self, mock_log, mock_UpdateIcons):
        """
        Test avmt status shutter closed and audio unchanged
        """
        # GIVEN: Test object
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "11"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting shutter to closed'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = False
        self.pjlink.mute = True

        # WHEN: Called with setting shutter closed and mute off
        process_command(projector=self.pjlink, cmd='AVMT', data='11')

        # THEN: Shutter should be True and mute should be False
        assert self.pjlink.shutter, 'Shutter should have been set to closed'
        assert self.pjlink.mute, 'Audio should not have changed'
        assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_avmt_status_timer_check_delete(self, mock_log, mock_UpdateIcons):
        """
        Test avmt deletes callback in projector.status_timer_check
        """
        # GIVEN: Test object
        log_warning_text = []
        log_debug_text = [call('({ip}) Processing command "AVMT" with data "11"'.format(ip=self.pjlink.name)),
                          call('({ip}) Calling function for AVMT'.format(ip=self.pjlink.name)),
                          call('({ip}) Setting shutter to closed'.format(ip=self.pjlink.name))]
        self.pjlink.shutter = False
        self.pjlink.mute = True
        self.pjlink.status_timer_checks = {'AVMT': self.pjlink.get_av_mute_status}

        # WHEN: Called with setting shutter closed and mute off
        with patch.object(self.pjlink, 'status_timer') as mock_status_timer:
            process_command(projector=self.pjlink, cmd='AVMT', data='11')

            # THEN: Shutter should be True and mute should be False
            assert self.pjlink.shutter, 'Shutter should have been set to closed'
            assert self.pjlink.mute, 'Audio should not have changed'
            assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
            assert 'AVMT' not in self.pjlink.status_timer_checks, 'Status timer list should not have AVMT callback'
            assert mock_status_timer.stop.called, 'Projector status_timer.stop() should have been called'
            mock_log.warning.assert_has_calls(log_warning_text)
            mock_log.debug.assert_has_calls(log_debug_text)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_1(self, mock_log):
        """
        Test CLSS request returns non-standard reply 1
        """
        # GIVEN: Test object
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "1"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=self.pjlink.name))]

        # WHEN: Process non-standard reply
        process_command(projector=self.pjlink, cmd='CLSS', data='1')

        # THEN: Projector class should be set with proper value
        assert '1' == self.pjlink.pjlink_class, 'Should have set class=1'
        mock_log.error.assert_has_calls(log_error_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_2(self, mock_log):
        """
        Test CLSS request returns non-standard reply 1
        """
        # GIVEN: Test object
        log_error_calls = []
        log_warning_calls = []
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "2"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "2"'.format(ip=self.pjlink.name))]

        # WHEN: Process non-standard reply
        process_command(projector=self.pjlink, cmd='CLSS', data='2')

        # THEN: Projector class should be set with proper value
        assert '2' == self.pjlink.pjlink_class, 'Should have set class=2'
        mock_log.error.assert_has_calls(log_error_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_invalid_nan(self, mock_log):
        """
        Test CLSS reply has no class number
        """
        # GIVEN: Test setup
        log_warning_calls = [call('({ip}) NAN CLSS version reply "Z" - '
                                  'defaulting to class "1"'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Z"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=self.pjlink.name))]

        # WHEN: Process invalid reply
        process_command(projector=self.pjlink, cmd='CLSS', data='Z')

        # THEN: Projector class should be set with default value
        assert self.pjlink.pjlink_class == '1', 'Invalid NaN class reply should have set class=1'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_invalid_no_version(self, mock_log):
        """
        Test CLSS reply has no class number
        """
        # GIVEN: Test object
        log_warning_calls = [call('({ip}) No numbers found in class version reply "Invalid" '
                                  '- defaulting to class "1"'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Invalid"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=self.pjlink.name))]

        # WHEN: Process invalid reply
        process_command(projector=self.pjlink, cmd='CLSS', data='Invalid')

        # THEN: Projector class should be set with default value
        assert self.pjlink.pjlink_class == '1', 'Invalid class reply should have set class=1'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_nonstandard_reply_1(self, mock_log):
        """
        Test CLSS request returns non-standard reply 1
        """
        # GIVEN: Test object
        log_error_calls = []
        log_warning_calls = [call('({ip}) Non-standard CLSS reply: "Class 1"'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Class 1"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=self.pjlink.name))]

        # WHEN: Process non-standard reply
        process_command(projector=self.pjlink, cmd='CLSS', data='Class 1')

        # THEN: Projector class should be set with proper value
        assert '1' == self.pjlink.pjlink_class, 'Non-standard class reply should have set class=1'
        mock_log.error.assert_has_calls(log_error_calls)
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_clss_nonstandard_reply_2(self, mock_log):
        """
        Test CLSS request returns non-standard reply 1
        """
        # GIVEN: Test object
        log_warning_calls = [call('({ip}) Non-standard CLSS reply: "Version2"'.format(ip=self.pjlink.name))]
        log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Version2"'.format(ip=self.pjlink.name)),
                           call('({ip}) Calling function for CLSS'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting pjlink_class for this projector to "2"'.format(ip=self.pjlink.name))]

        # WHEN: Process non-standard reply
        process_command(projector=self.pjlink, cmd='CLSS', data='Version2')

        # THEN: Projector class should be set with proper value
        assert '2' == self.pjlink.pjlink_class, 'Non-standard class reply should have set class=1'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_all_error(self, mock_log):
        """
        Test test_projector_process_erst_all_error
        """
        # GIVEN: Test object
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_ERROR],
                                                                  lamp=PJLINK_ERST_STATUS[E_ERROR],
                                                                  temp=PJLINK_ERST_STATUS[E_ERROR],
                                                                  cover=PJLINK_ERST_STATUS[E_ERROR],
                                                                  filt=PJLINK_ERST_STATUS[E_ERROR],
                                                                  other=PJLINK_ERST_STATUS[E_ERROR])
        chk_test = {'Fan': E_ERROR,
                    'Lamp': E_ERROR,
                    'Temperature': E_ERROR,
                    'Cover': E_ERROR,
                    'Filter': E_ERROR,
                    'Other': E_ERROR}
        log_warning_calls = []
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=self.pjlink.name,
                                                                                            chk=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]
        self.pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        process_command(projector=self.pjlink, cmd='ERST', data=chk_data)

        # THEN: PJLink instance errors should match chk_value
        assert self.pjlink.projector_errors == chk_test, 'Projector errors should be all E_ERROR'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_all_ok(self, mock_log):
        """
        Test to verify pjlink.projector_errors is set to None when no errors
        """
        # GIVEN: Test object
        chk_data = '0' * PJLINK_ERST_DATA['DATA_LENGTH']
        log_warning_calls = []
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=self.pjlink.name,
                                                                                            chk=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]

        # WHEN: process_erst with no errors
        process_command(projector=self.pjlink, cmd='ERST', data=chk_data)

        # THEN: PJLink instance errors should be None
        assert self.pjlink.projector_errors is None, 'projector_errors should have been set to None'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_all_warn(self, mock_log):
        """
        Test test_projector_process_erst_all_error
        """
        # GIVEN: Test object
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[E_WARN],
                                                                  lamp=PJLINK_ERST_STATUS[E_WARN],
                                                                  temp=PJLINK_ERST_STATUS[E_WARN],
                                                                  cover=PJLINK_ERST_STATUS[E_WARN],
                                                                  filt=PJLINK_ERST_STATUS[E_WARN],
                                                                  other=PJLINK_ERST_STATUS[E_WARN])
        chk_test = {'Fan': E_WARN,
                    'Lamp': E_WARN,
                    'Temperature': E_WARN,
                    'Cover': E_WARN,
                    'Filter': E_WARN,
                    'Other': E_WARN}
        log_warning_calls = []
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=self.pjlink.name,
                                                                                            chk=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]
        self.pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        process_command(projector=self.pjlink, cmd='ERST', data=chk_data)

        # THEN: PJLink instance errors should match chk_value
        assert self.pjlink.projector_errors == chk_test, 'Projector errors should be all E_WARN'
        mock_log.warning.assert_has_calls(log_warning_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_data_invalid_length(self, mock_log):
        """
        Test test_projector_process_erst_data_invalid_length
        """
        # GIVEN: Test object
        chk_data = '0' * (PJLINK_ERST_DATA['DATA_LENGTH'] + 1)
        log_warn_calls = [call('({ip}) Invalid error status response "{data}": '
                               'length != {chk}'.format(ip=self.pjlink.name,
                                                        data=chk_data, chk=PJLINK_ERST_DATA['DATA_LENGTH']))]
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]
        self.pjlink.projector_errors = None

        # WHEN: process_erst called with invalid data (too many values
        process_command(self.pjlink, cmd='ERST', data=chk_data)

        # THEN: pjlink.projector_errors should be empty and warning logged
        assert not self.pjlink.projector_errors, 'There should be no errors'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_data_invalid_nan(self, mock_log):
        """
        Test ERST called with invalid data
        """
        # GIVEN: Test object
        chk_data = 'Z' + ('0' * (PJLINK_ERST_DATA['DATA_LENGTH'] - 1))
        log_warn_calls = [call('({ip}) Invalid error status response "{data}"'.format(ip=self.pjlink.name,
                                                                                      data=chk_data))]
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]
        self.pjlink.projector_errors = None

        # WHEN: process_erst called with invalid data (too many values
        process_command(self.pjlink, cmd='ERST', data=chk_data)

        # THEN: pjlink.projector_errors should be empty and warning logged
        assert not self.pjlink.projector_errors, 'There should be no errors'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_erst_warn_cover_only(self, mock_log):
        """
        Test test_projector_process_erst_warn_cover_only
        """
        # GIVEN: Test object
        chk_data = '{fan}{lamp}{temp}{cover}{filt}{other}'.format(fan=PJLINK_ERST_STATUS[S_OK],
                                                                  lamp=PJLINK_ERST_STATUS[S_OK],
                                                                  temp=PJLINK_ERST_STATUS[S_OK],
                                                                  cover=PJLINK_ERST_STATUS[E_WARN],
                                                                  filt=PJLINK_ERST_STATUS[S_OK],
                                                                  other=PJLINK_ERST_STATUS[S_OK])
        chk_test = {'Cover': E_WARN}
        log_warn_calls = []
        log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for ERST'.format(ip=self.pjlink.name))]
        self.pjlink.projector_errors = None

        # WHEN: process_erst with status set to WARN
        process_command(projector=self.pjlink, cmd='ERST', data=chk_data)

        # THEN: PJLink instance errors should match only cover warning
        assert 1 == len(self.pjlink.projector_errors), 'There should only be 1 error listed in projector_errors'
        assert 'Cover' in self.pjlink.projector_errors, '"Cover" should be the only error listed'
        assert self.pjlink.projector_errors['Cover'] == E_WARN, '"Cover" should have E_WARN listed as error'
        assert chk_test == self.pjlink.projector_errors, 'projector_errors should match test errors'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_inf1(self, mock_log):
        """
        Test saving INF1 data (manufacturer)
        """
        # GIVEN: Test object
        chk_data = 'TEst INformation MultiCase'
        log_warn_calls = []
        log_debug_calls = [call('({ip}) Processing command "INF1" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for INF1'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting projector manufacturer data to '
                                '"{data}"'.format(ip=self.pjlink.name, data=chk_data))]
        self.pjlink.manufacturer = None

        # WHEN: process_inf called with test data
        process_command(projector=self.pjlink, cmd='INF1', data=chk_data)

        # THEN: Data should be saved
        assert self.pjlink.manufacturer == chk_data, 'Test data should have been saved'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_inf2(self, mock_log):
        """
        Test saving INF2 data (model)
        """
        # GIVEN: Test object
        chk_data = 'TEst moDEl MultiCase'
        log_warn_calls = []
        log_debug_calls = [call('({ip}) Processing command "INF2" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for INF2'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting projector model to "{data}"'.format(ip=self.pjlink.name,
                                                                                    data=chk_data))]
        self.pjlink.model = None

        # WHEN: process_inf called with test data
        process_command(projector=self.pjlink, cmd='INF2', data=chk_data)

        # THEN: Data should be saved
        assert self.pjlink.model == chk_data, 'Test data should have been saved'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)

    @patch.object(openlp.core.projectors.pjlinkcommands, 'log')
    def test_projector_info(self, mock_log):
        """
        Test saving INF2 data (model)
        """
        # GIVEN: Test object
        chk_data = 'TEst ExtrANEous MultiCase INformatoin that MFGR might Set'
        log_warn_calls = []
        log_debug_calls = [call('({ip}) Processing command "INFO" with data "{data}"'.format(ip=self.pjlink.name,
                                                                                             data=chk_data)),
                           call('({ip}) Calling function for INFO'.format(ip=self.pjlink.name)),
                           call('({ip}) Setting projector other_info to "{data}"'.format(ip=self.pjlink.name,
                                                                                         data=chk_data))]
        self.pjlink.other_info = None

        # WHEN: process_inf called with test data
        process_command(projector=self.pjlink, cmd='INFO', data=chk_data)

        # THEN: Data should be saved
        assert self.pjlink.other_info == chk_data, 'Test data should have been saved'
        mock_log.warning.assert_has_calls(log_warn_calls)
        mock_log.debug.assert_has_calls(log_debug_calls)
