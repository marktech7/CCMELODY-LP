# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
from openlp.core.projectors.constants import E_NO_AUTHENTICATION, STATUS_CODE, S_AUTHENTICATE, S_CONNECT
from openlp.core.projectors.pjlinkcommands import process_command
from tests.resources.projector.data import TEST_PIN, TEST_SALT


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_authenticate(mock_log, pjlink):
    """
    Test initial connection prompt with authentication
    """
    # GIVEN: Initial mocks and data
    log_error_calls = []
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "1 {data}"'.format(ip=pjlink.name,
                                                                                             data=TEST_SALT)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name)),
                       call('({ip}) PJLINK: Returning {data}'.format(ip=pjlink.name,
                                                                     data=STATUS_CODE[S_AUTHENTICATE]))]

    pjlink.pin = TEST_PIN

    # WHEN: process_pjlink called with no authentication required
    chk = process_command(projector=pjlink, cmd='PJLINK', data='1 {salt}'.format(salt=TEST_SALT))

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == S_AUTHENTICATE, 'Should have returned {data}'.format(data=STATUS_CODE[S_AUTHENTICATE])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_authenticate_pin_not_set_error(mock_log, pjlink):
    """
    Test initial connection prompt with authentication and no pin set
    """
    # GIVEN: Initial mocks and data
    log_error_calls = [call('({ip}) Authenticate connection but no PIN - aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "1 {data}"'.format(ip=pjlink.name,
                                                                                             data=TEST_SALT)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]

    pjlink.pin = None

    # WHEN: process_pjlink called with no authentication required
    chk = process_command(projector=pjlink, cmd='PJLINK', data='1 {salt}'.format(salt=TEST_SALT))

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_authenticate_token_invalid(mock_log, pjlink):
    """
    Test initial connection prompt with authentication and bad token
    """
    # GIVEN: Initial mocks and data
    bad_token = 'abcdefgh'
    log_error_calls = [call('({ip}) Authentication token invalid (not a hexadecimal number) - '
                            'aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data '
                            '"1 {data}"'.format(ip=pjlink.name, data=bad_token)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]
    pjlink.pin = TEST_SALT

    # WHEN: process_pjlink called with bad token
    chk = process_command(projector=pjlink, cmd='PJLINK', data='1 {data}'.format(data=bad_token))

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_authenticate_token_length(mock_log, pjlink):
    """
    Test initial connection prompt with authentication and bad token
    """
    # GIVEN: Initial mocks and data
    bad_token = '1234abcde'  # Length should be 8, this is 9
    log_error_calls = [call('({ip}) Authentication token invalid (size) - '
                            'aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data '
                            '"1 {data}"'.format(ip=pjlink.name, data=bad_token)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]
    pjlink.pin = TEST_SALT

    # WHEN: process_pjlink called with bad token
    chk = process_command(projector=pjlink, cmd='PJLINK', data='1 {data}'.format(data=bad_token))

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_authenticate_token_missing(mock_log, pjlink):
    """
    Test initial connection prompt with authentication and missing token
    """
    # GIVEN: Initial mocks and data
    log_error_calls = [call('({ip}) Authenticated connection but not enough info - '
                            'aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "1"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]

    pjlink.pin = TEST_SALT

    # WHEN: process_pjlink called with bad token
    chk = process_command(projector=pjlink, cmd='PJLINK', data='1')

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_normal(mock_log, pjlink):
    """
    Test processing PJLINK initial prompt
    """
    # GIVEN: Mocks and data
    log_error_calls = []
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "0"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name)),
                       call('({ip}) PJLINK: Returning {data}'.format(ip=pjlink.name,
                                                                     data=STATUS_CODE[S_CONNECT]))]

    pjlink.pin = None

    # WHEN: process_pjlink called with no authentication required
    chk = process_command(projector=pjlink, cmd='PJLINK', data="0")

    # THEN: proper processing should have occured
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == S_CONNECT, 'Should have returned {data}'.format(data=STATUS_CODE[S_CONNECT])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_normal_pin_set_error(mock_log, pjlink):
    """
    Test process_pjlinnk called with no authentication but pin is set
    """
    # GIVEN: Initial mocks and data
    log_error_calls = [call('({ip}) Normal connection but PIN set - '
                            'aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data "0"'.format(ip=pjlink.name)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]
    pjlink.pin = TEST_PIN

    # WHEN: process_pjlink called with invalid authentication scheme
    chk = process_command(projector=pjlink, cmd='PJLINK', data='0')

    # THEN: Proper calls should be made
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])


@patch.object(openlp.core.projectors.pjlinkcommands, 'log')
def test_process_pjlink_normal_with_token(mock_log, pjlink):
    """
    Test process_pjlinnk called with no authentication but pin is set
    """
    # GIVEN: Initial mocks and data
    log_error_calls = [call('({ip}) Normal connection with extra information - '
                            'aborting'.format(ip=pjlink.name))]
    log_warning_calls = []
    log_debug_calls = [call('({ip}) Processing command "PJLINK" with data '
                            '"0 {data}"'.format(ip=pjlink.name, data=TEST_SALT)),
                       call('({ip}) Calling function for PJLINK'.format(ip=pjlink.name)),
                       call('({ip}) Processing PJLINK command'.format(ip=pjlink.name))]
    pjlink.pin = TEST_PIN

    # WHEN: process_pjlink called with invalid authentication scheme
    chk = process_command(projector=pjlink, cmd='PJLINK', data='0 {data}'.format(data=TEST_SALT))

    # THEN: Proper calls should be made
    mock_log.error.assert_has_calls(log_error_calls)
    mock_log.warning.assert_has_calls(log_warning_calls)
    mock_log.debug.assert_has_calls(log_debug_calls)
    assert chk == E_NO_AUTHENTICATION, \
        'Should have returned {data}'.format(data=STATUS_CODE[E_NO_AUTHENTICATION])
