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
import sys

from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

# Mock QtWebEngineWidgets
sys.modules['PyQt5.QtWebEngineWidgets'] = MagicMock()

from openlp.core.app import parse_options
from openlp.core.common import is_win
from openlp.core.common.settings import Settings


def test_parse_options_basic():
    """
    Test the parse options process works
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = []

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_debug():
    """
    Test the parse options process works for debug only
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_debug_and_portable():
    """
    Test the parse options process works for debug and portable
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['--portable']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is True, 'The portable flag should be set to true'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_portable_and_portable_path():
    """
    Test the parse options process works portable and portable-path
    """
    # GIVEN: a a set of system arguments.
    if is_win():
        data_path = 'c:\\temp\\openlp-data'
    else:
        data_path = '/tmp/openlp-data'
    sys.argv[1:] = ['--portable', '--portable-path', '{datapath}'.format(datapath=data_path)]

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is True, 'The portable flag should be set to true'
    assert args.portablepath == data_path, 'The portable path should be set as expected'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_all_no_file():
    """
    Test the parse options process works with two options
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug', '-p']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is True, 'The portable flag should be set to false'
    assert args.rargs == [], 'The service file should be blank'


def test_parse_options_file():
    """
    Test the parse options process works with a file
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['dummy_temp']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == 'warning', 'The log level should be set to warning'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == ['dummy_temp'], 'The service file should not be blank'


def test_parse_options_file_and_debug():
    """
    Test the parse options process works with a file and the debug log level
    """
    # GIVEN: a a set of system arguments.
    sys.argv[1:] = ['-l debug', 'dummy_temp']

    # WHEN: We we parse them to expand to options
    args = parse_options()

    # THEN: the following fields will have been extracted.
    assert args.loglevel == ' debug', 'The log level should be set to debug'
    assert args.no_error_form is False, 'The no_error_form should be set to False'
    assert args.portable is False, 'The portable flag should be set to false'
    assert args.rargs == ['dummy_temp'], 'The service file should not be blank'


@patch('openlp.core.app.QtWidgets.QMessageBox.critical')
@patch('openlp.core.app.QtWidgets.QMessageBox.StandardButtons')
def test_is_already_running_is_running_continue(MockedStandardButtons, mocked_critical, qapp):
    """
    Test the is_already_running() method when OpenLP IS running and the user chooses to continue
    """
    # GIVEN: An OpenLP app and some mocks
    MockedStandardButtons.return_value = 0
    mocked_critical.return_value = QtWidgets.QMessageBox.Yes

    # WHEN: is_already_running() is called
    qapp.is_already_running()

    # THEN: The result should be false
    MockedStandardButtons.assert_called_once_with(QtWidgets.QMessageBox.Ok)
    mocked_critical.assert_called_once_with(None, 'Error',
                                            'OpenLP is already running on this machine. \nClosing this instance', 0)


@patch('openlp.core.app.QtWidgets.QApplication.processEvents')
def test_process_events(mocked_processEvents, qapp):
    """
    Test that the app.process_events() method simply calls the Qt method
    """
    # GIVEN: An app
    # WHEN: process_events() is called
    qapp.process_events()

    # THEN: processEvents was called
    mocked_processEvents.assert_called_once_with()


@patch('openlp.core.app.QtWidgets.QApplication.setOverrideCursor')
@patch('openlp.core.app.QtWidgets.QApplication.processEvents')
def test_set_busy_cursor(mocked_processEvents, mocked_setOverrideCursor, qapp):
    """
    Test that the set_busy_cursor() method sets the cursor
    """
    # GIVEN: An app
    # WHEN: set_busy_cursor() is called
    qapp.set_busy_cursor()

    # THEN: The cursor should have been set
    mocked_setOverrideCursor.assert_called_once_with(QtCore.Qt.BusyCursor)
    mocked_processEvents.assert_called_once_with()


@patch('openlp.core.app.QtWidgets.QApplication.restoreOverrideCursor')
@patch('openlp.core.app.QtWidgets.QApplication.processEvents')
def test_set_normal_cursor(mocked_restoreOverrideCursor, mocked_processEvents, qapp):
    """
    Test that the set_normal_cursor() method resets the cursor
    """
    # GIVEN: An app
    # WHEN: set_normal_cursor() is called
    qapp.set_normal_cursor()

    # THEN: The cursor should have been set
    mocked_restoreOverrideCursor.assert_called_once_with()
    mocked_processEvents.assert_called_once_with()


@patch('openlp.core.app.get_version')
@patch('openlp.core.app.QtWidgets.QMessageBox.question')
def test_backup_on_upgrade_first_install(mocked_question, mocked_get_version, qapp, settings):
    """
    Test that we don't try to backup on a new install
    """
    # GIVEN: Mocked data version and OpenLP version which are the same
    old_install = False
    MOCKED_VERSION = {
        'full': '2.4.0',
        'version': '2.4.0',
        'build': None
    }
    settings.setValue('core/application version', '2.4.0')
    mocked_get_version.return_value = MOCKED_VERSION
    mocked_question.return_value = QtWidgets.QMessageBox.No

    # WHEN: We check if a backup should be created
    qapp.backup_on_upgrade(old_install, False)

    # THEN: It should not ask if we want to create a backup
    assert Settings().value('core/application version') == '2.4.0', 'Version should be the same!'
    assert mocked_question.call_count == 0, 'No question should have been asked!'


@patch('openlp.core.app.get_version')
@patch('openlp.core.app.QtWidgets.QMessageBox.question')
def test_backup_on_upgrade(mocked_question, mocked_get_version, qapp, settings):
    """
    Test that we try to backup on a new install
    """
    # GIVEN: Mocked data version and OpenLP version which are different
    old_install = True
    MOCKED_VERSION = {
        'full': '2.9.0.dev2963+97ba02d1f',
        'version': '2.9.0',
        'build': '97ba02d1f'
    }
    settings.setValue('core/application version', '2.4.6')
    qapp.splash = MagicMock()
    qapp.splash.isVisible.return_value = True
    mocked_get_version.return_value = MOCKED_VERSION
    mocked_question.return_value = QtWidgets.QMessageBox.No

    # WHEN: We check if a backup should be created
    qapp.backup_on_upgrade(old_install, True)

    # THEN: It should ask if we want to create a backup
    assert Settings().value('core/application version') == '2.9.0', 'Version should be upgraded!'
    assert mocked_question.call_count == 1, 'A question should have been asked!'
    qapp.splash.hide.assert_called_once_with()
    qapp.splash.show.assert_called_once_with()
