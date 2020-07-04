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
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import E_ERROR, E_WARN, PJLINK_ERST_DATA, PJLINK_ERST_STATUS, S_OK


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_ackn(mock_log, pjlink):
    """
    Test ackn command (empty test)
    """
    # GIVEN: Test setup
    log_debug_text = [call('({ip}) Processing command "ACKN" with data "0"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for ACKN'.format(ip=pjlink.name))]

    # WHEN: Called with setting shutter closed and mute on
    process_command(projector=pjlink, cmd='ACKN', data='0')

    # THEN: Shutter should be closed and mute should be True
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_audio_muted(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt status shutter unchanged and mute on
    """
    # GIVEN: Test setup
    log_warning_text = []
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "21"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name)),
                      call('({ip}) Setting speaker to muted'.format(ip=pjlink.name))]
    pjlink.shutter = True
    pjlink.mute = False

    # WHEN: Called with setting shutter closed and mute on
    process_command(projector=pjlink, cmd='AVMT', data='21')

    # THEN: Shutter should be closed and mute should be True
    assert pjlink.shutter, 'Shutter should not have changed'
    assert pjlink.mute, 'Audio should be off'
    assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
    mock_log.warning.assert_has_calls(log_warning_text)
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_bad_data(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt bad data fail
    """
    # GIVEN: Test object
    log_warning_text = [call('({ip}) Invalid av mute response: 36'.format(ip=pjlink.name))]
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "36"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name))]
    pjlink.shutter = True
    pjlink.mute = True

    # WHEN: Called with an invalid setting
    process_command(projector=pjlink, cmd='AVMT', data='36')

    # THEN: Shutter should be closed and mute should be True
    assert pjlink.shutter, 'Shutter should changed'
    assert pjlink.mute, 'Audio should not have changed'
    assert not mock_UpdateIcons.emit.called, 'Update icons should NOT have been called'
    mock_log.warning.assert_has_calls(log_warning_text)
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_closed_muted(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt status shutter closed and mute off
    """
    # GIVEN: Test object
    log_warning_text = []
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "31"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name)),
                      call('({ip}) Setting shutter to closed'.format(ip=pjlink.name)),
                      call('({ip}) Setting speaker to muted'.format(ip=pjlink.name))]
    pjlink.shutter = False
    pjlink.mute = False

    # WHEN: Called with setting shutter to closed and mute on
    process_command(projector=pjlink, cmd='AVMT', data='31')

    # THEN: Shutter should be closed and mute should be True
    assert pjlink.shutter, 'Shutter should have been set to closed'
    assert pjlink.mute, 'Audio should be muted'
    assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
    mock_log.warning.assert_has_calls(log_warning_text)
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_open_unmuted(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt status shutter open and mute off
    """
    # GIVEN: Test object
    log_warning_text = []
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "30"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name)),
                      call('({ip}) Setting shutter to open'.format(ip=pjlink.name)),
                      call('({ip}) Setting speaker to normal'.format(ip=pjlink.name))]
    pjlink.shutter = True
    pjlink.mute = True

    # WHEN: Called with setting shutter to closed and mute on
    process_command(projector=pjlink, cmd='AVMT', data='30')

    # THEN: Shutter should be closed and mute should be True
    assert not pjlink.shutter, 'Shutter should have been set to off'
    assert not pjlink.mute, 'Audio should be on'
    assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
    mock_log.warning.assert_has_calls(log_warning_text)
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_shutter_closed(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt status shutter closed and audio unchanged
    """
    # GIVEN: Test object
    log_warning_text = []
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "11"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name)),
                      call('({ip}) Setting shutter to closed'.format(ip=pjlink.name))]
    pjlink.shutter = False
    pjlink.mute = True

    # WHEN: Called with setting shutter closed and mute off
    process_command(projector=pjlink, cmd='AVMT', data='11')

    # THEN: Shutter should be True and mute should be False
    assert pjlink.shutter, 'Shutter should have been set to closed'
    assert pjlink.mute, 'Audio should not have changed'
    assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
    mock_log.warning.assert_has_calls(log_warning_text)
    mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons')
@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_avmt_status_timer_check_delete(mock_log, mock_UpdateIcons, pjlink):
    """
    Test avmt deletes callback in projector.status_timer_check
    """
    # GIVEN: Test object
    log_warning_text = []
    log_debug_text = [call('({ip}) Processing command "AVMT" with data "11"'.format(ip=pjlink.name)),
                      call('({ip}) Calling function for AVMT'.format(ip=pjlink.name)),
                      call('({ip}) Setting shutter to closed'.format(ip=pjlink.name))]
    pjlink.shutter = False
    pjlink.mute = True
    pjlink.status_timer_checks = {'AVMT': pjlink.get_av_mute_status}

    # WHEN: Called with setting shutter closed and mute off
    with patch.object(pjlink, 'status_timer') as mock_status_timer:
        process_command(projector=pjlink, cmd='AVMT', data='11')

        # THEN: Shutter should be True and mute should be False
        assert pjlink.shutter, 'Shutter should have been set to closed'
        assert pjlink.mute, 'Audio should not have changed'
        assert mock_UpdateIcons.emit.called, 'Update icons should have been called'
        assert 'AVMT' not in pjlink.status_timer_checks, 'Status timer list should not have AVMT callback'
        assert mock_status_timer.stop.called, 'Projector status_timer.stop() should have been called'
        mock_log.warning.assert_has_calls(log_warning_text)
        mock_log.debug.assert_has_calls(log_debug_text)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_1(mock_log, pjlink):
    """
    Test CLSS request returns non-standard reply 1
    """
    # GIVEN: Test object
    log_error_calls = []
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "1"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=pjlink.name))]

    # WHEN: Process non-standard reply
    process_command(projector=pjlink, cmd='CLSS', data='1')

    # THEN: Projector class should be set with proper value
    assert '1' == pjlink.pjlink_class, 'Should have set class=1'
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_2(mock_log, pjlink):
    """
    Test CLSS request returns non-standard reply 1
    """
    # GIVEN: Test object
    log_error_calls = []
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "2"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "2"'.format(ip=pjlink.name))]

    # WHEN: Process non-standard reply
    process_command(projector=pjlink, cmd='CLSS', data='2')

    # THEN: Projector class should be set with proper value
    assert '2' == pjlink.pjlink_class, 'Should have set class=2'
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_invalid_nan(mock_log, pjlink):
    """
    Test CLSS reply has no class number
    """
    # GIVEN: Test setup
    log_warning_calls = [call('({ip}) NAN CLSS version reply "Z" - '
                              'defaulting to class "1"'.format(ip=pjlink.name))]
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Z"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=pjlink.name))]

    # WHEN: Process invalid reply
    process_command(projector=pjlink, cmd='CLSS', data='Z')

    # THEN: Projector class should be set with default value
    assert pjlink.pjlink_class == '1', 'Invalid NaN class reply should have set class=1'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_invalid_no_version(mock_log, pjlink):
    """
    Test CLSS reply has no class number
    """
    # GIVEN: Test object
    log_warning_calls = [call('({ip}) No numbers found in class version reply "Invalid" '
                              '- defaulting to class "1"'.format(ip=pjlink.name))]
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Invalid"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=pjlink.name))]

    # WHEN: Process invalid reply
    process_command(projector=pjlink, cmd='CLSS', data='Invalid')

    # THEN: Projector class should be set with default value
    assert pjlink.pjlink_class == '1', 'Invalid class reply should have set class=1'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_nonstandard_reply_1(mock_log, pjlink):
    """
    Test CLSS request returns non-standard reply 1
    """
    # GIVEN: Test object
    log_error_calls = []
    log_warning_calls = [call('({ip}) Non-standard CLSS reply: "Class 1"'.format(ip=pjlink.name))]
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Class 1"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "1"'.format(ip=pjlink.name))]

    # WHEN: Process non-standard reply
    process_command(projector=pjlink, cmd='CLSS', data='Class 1')

    # THEN: Projector class should be set with proper value
    assert '1' == pjlink.pjlink_class, 'Non-standard class reply should have set class=1'
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_clss_nonstandard_reply_2(mock_log, pjlink):
    """
    Test CLSS request returns non-standard reply 1
    """
    # GIVEN: Test object
    log_warning_calls = [call('({ip}) Non-standard CLSS reply: "Version2"'.format(ip=pjlink.name))]
    log_debug_calls = [call('({ip}) Processing command "CLSS" with data "Version2"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for CLSS'.format(ip=pjlink.name)),
                       call('({ip}) Setting pjlink_class for this projector to "2"'.format(ip=pjlink.name))]

    # WHEN: Process non-standard reply
    process_command(projector=pjlink, cmd='CLSS', data='Version2')

    # THEN: Projector class should be set with proper value
    assert '2' == pjlink.pjlink_class, 'Non-standard class reply should have set class=1'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_all_error(mock_log, pjlink):
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
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=pjlink.name,
                                                                                        chk=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match chk_value
    assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_ERROR'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_all_ok(mock_log, pjlink):
    """
    Test to verify pjlink.projector_errors is set to None when no errors
    """
    # GIVEN: Test object
    chk_data = '0' * PJLINK_ERST_DATA['DATA_LENGTH']
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=pjlink.name,
                                                                                        chk=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]

    # WHEN: process_erst with no errors
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should be None
    assert pjlink.projector_errors is None, 'projector_errors should have been set to None'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_all_warn(mock_log, pjlink):
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
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{chk}"'.format(ip=pjlink.name,
                                                                                        chk=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match chk_value
    assert pjlink.projector_errors == chk_test, 'Projector errors should be all E_WARN'
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_data_invalid_length(mock_log, pjlink):
    """
    Test test_projector_process_erst_data_invalid_length
    """
    # GIVEN: Test object
    chk_data = '0' * (PJLINK_ERST_DATA['DATA_LENGTH'] + 1)
    log_warn_calls = [call('({ip}) Invalid error status response "{data}": '
                           'length != {chk}'.format(ip=pjlink.name,
                                                    data=chk_data, chk=PJLINK_ERST_DATA['DATA_LENGTH']))]
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]
    pjlink.projector_errors = None

    # WHEN: process_erst called with invalid data (too many values
    process_command(pjlink, cmd='ERST', data=chk_data)

    # THEN: pjlink.projector_errors should be empty and warning logged
    assert not pjlink.projector_errors, 'There should be no errors'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_data_invalid_nan(mock_log, pjlink):
    """
    Test ERST called with invalid data
    """
    # GIVEN: Test object
    chk_data = 'Z' + ('0' * (PJLINK_ERST_DATA['DATA_LENGTH'] - 1))
    log_warn_calls = [call('({ip}) Invalid error status response "{data}"'.format(ip=pjlink.name,
                                                                                  data=chk_data))]
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]
    pjlink.projector_errors = None

    # WHEN: process_erst called with invalid data (too many values
    process_command(pjlink, cmd='ERST', data=chk_data)

    # THEN: pjlink.projector_errors should be empty and warning logged
    assert not pjlink.projector_errors, 'There should be no errors'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_erst_warn_cover_only(mock_log, pjlink):
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
    log_debug_calls = [call('({ip}) Processing command "ERST" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for ERST'.format(ip=pjlink.name))]
    pjlink.projector_errors = None

    # WHEN: process_erst with status set to WARN
    process_command(projector=pjlink, cmd='ERST', data=chk_data)

    # THEN: PJLink instance errors should match only cover warning
    assert 1 == len(pjlink.projector_errors), 'There should only be 1 error listed in projector_errors'
    assert 'Cover' in pjlink.projector_errors, '"Cover" should be the only error listed'
    assert pjlink.projector_errors['Cover'] == E_WARN, '"Cover" should have E_WARN listed as error'
    assert chk_test == pjlink.projector_errors, 'projector_errors should match test errors'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_inf1(mock_log, pjlink):
    """
    Test saving INF1 data (manufacturer)
    """
    # GIVEN: Test object
    chk_data = 'TEst INformation MultiCase'
    log_warn_calls = []
    log_debug_calls = [call('({ip}) Processing command "INF1" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for INF1'.format(ip=pjlink.name)),
                       call('({ip}) Setting projector manufacturer data to '
                            '"{data}"'.format(ip=pjlink.name, data=chk_data))]
    pjlink.manufacturer = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INF1', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.manufacturer == chk_data, 'Test data should have been saved'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_inf2(mock_log, pjlink):
    """
    Test saving INF2 data (model)
    """
    # GIVEN: Test object
    chk_data = 'TEst moDEl MultiCase'
    log_warn_calls = []
    log_debug_calls = [call('({ip}) Processing command "INF2" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for INF2'.format(ip=pjlink.name)),
                       call('({ip}) Setting projector model to "{data}"'.format(ip=pjlink.name,
                                                                                data=chk_data))]
    pjlink.model = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INF2', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.model == chk_data, 'Test data should have been saved'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_projector_info(mock_log, pjlink):
    """
    Test saving INF2 data (model)
    """
    # GIVEN: Test object
    chk_data = 'TEst ExtrANEous MultiCase INformatoin that MFGR might Set'
    log_warn_calls = []
    log_debug_calls = [call('({ip}) Processing command "INFO" with data "{data}"'.format(ip=pjlink.name,
                                                                                         data=chk_data)),
                       call('({ip}) Calling function for INFO'.format(ip=pjlink.name)),
                       call('({ip}) Setting projector other_info to "{data}"'.format(ip=pjlink.name,
                                                                                     data=chk_data))]
    pjlink.other_info = None

    # WHEN: process_inf called with test data
    process_command(projector=pjlink, cmd='INFO', data=chk_data)

    # THEN: Data should be saved
    assert pjlink.other_info == chk_data, 'Test data should have been saved'
    mock_log.warning.assert_has_calls(log_warn_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
