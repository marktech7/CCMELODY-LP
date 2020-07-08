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
Package to test openlp.core.ui.mainwindow package.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import UiStrings
from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.core.ui.mainwindow import MainWindow
from tests.utils.constants import TEST_RESOURCES_PATH, RESOURCE_PATH


def _create_mock_action(parent, name, **kwargs):
    """
    Create a fake action with some "real" attributes
    """
    action = QtWidgets.QAction(parent)
    action.setObjectName(name)
    if kwargs.get('triggers'):
        action.triggered.connect(kwargs.pop('triggers'))
    return action


@pytest.yield_fixture()
def main_window(state, settings):
    app = Registry().get('application')
    app.set_busy_cursor = MagicMock()
    app.set_normal_cursor = MagicMock()
    app.process_events = MagicMock()
    app.args = []
    Registry().set_flag('no_web_server', True)
    add_toolbar_action_patcher = patch('openlp.core.ui.mainwindow.create_action')
    mocked_add_toolbar_action = add_toolbar_action_patcher.start()
    mocked_add_toolbar_action.side_effect = _create_mock_action
    renderer_patcher = patch('openlp.core.display.render.Renderer')
    renderer_patcher.start()
    mocked_desktop = MagicMock()
    mocked_desktop.screenCount.return_value = 1
    mocked_desktop.screenGeometry.return_value = QtCore.QRect(0, 0, 1024, 768)
    mocked_desktop.primaryScreen.return_value = 1
    ScreenList.create(mocked_desktop)
    mainwindow = MainWindow()
    yield mainwindow
    del mainwindow
    renderer_patcher.stop()
    add_toolbar_action_patcher.stop()


def test_cmd_line_file(main_window):
    """
    Test that passing a service file from the command line loads the service.
    """
    # GIVEN a service as an argument to openlp
    service = os.path.join(TEST_RESOURCES_PATH, 'service', 'test.osz')

    # WHEN the argument is processed
    with patch.object(main_window.service_manager, 'load_file') as mocked_load_file:
        main_window.open_cmd_line_files([service])

    # THEN the service from the arguments is loaded
    mocked_load_file.assert_called_with(Path(service))


@patch('openlp.core.ui.servicemanager.ServiceManager.load_file')
def test_cmd_line_arg(mocked_load_file, main_window):
    """
    Test that passing a non service file does nothing.
    """
    # GIVEN a non service file as an argument to openlp
    service = 'run_openlp.py'

    # WHEN the argument is processed
    main_window.open_cmd_line_files(service)

    # THEN the file should not be opened
    assert mocked_load_file.called is False, 'load_file should not have been called'


def test_main_window_title(main_window):
    """
    Test that running a new instance of OpenLP set the window title correctly
    """
    # GIVEN a newly opened OpenLP instance

    # WHEN no changes are made to the service

    # THEN the main window's title shoud be the same as the OpenLP string in the UiStrings class
    assert main_window.windowTitle() == UiStrings().OpenLP, \
        'The main window\'s title should be the same as the OpenLP string in UiStrings class'


def test_set_service_modifed(main_window):
    """
    Test that when setting the service's title the main window's title is set correctly
    """
    # GIVEN a newly opened OpenLP instance

    # WHEN set_service_modified is called with with the modified flag set true and a file name
    main_window.set_service_modified(True, 'test.osz')

    # THEN the main window's title should be set to the
    assert main_window.windowTitle(), '%s - %s*' % (UiStrings().OpenLP, 'test.osz') == \
        'The main window\'s title should be set to "<the contents of UiStrings().OpenLP> - test.osz*"'


def test_set_service_unmodified(main_window):
    """
    Test that when setting the service's title the main window's title is set correctly
    """
    # GIVEN a newly opened OpenLP instance

    # WHEN set_service_modified is called with with the modified flag set False and a file name
    main_window.set_service_modified(False, 'test.osz')

    # THEN the main window's title should be set to the
    assert main_window.windowTitle(), '%s - %s' % (UiStrings().OpenLP, 'test.osz') == \
        'The main window\'s title should be set to "<the contents of UiStrings().OpenLP> - test.osz"'


def test_mainwindow_configuration(main_window):
    """
    Check that the Main Window initialises the Registry Correctly
    """
    # GIVEN: A built main window

    # WHEN: you check the started functions

    # THEN: the following registry functions should have been registered
    expected_service_list = ['settings', 'settings_thread', 'application', 'main_window', 'http_server',
                             'authentication_token', 'settings_form', 'service_manager', 'theme_manager',
                             'projector_manager']
    expected_functions_list = ['bootstrap_initialise', 'bootstrap_post_set_up', 'bootstrap_completion',
                               'config_screen_changed', 'theme_update_global']
    assert list(Registry().service_list.keys()) == expected_service_list, \
        'The service list should have been {}'.format(Registry().service_list.keys())
    assert list(Registry().functions_list.keys()) == expected_functions_list, \
        'The function list should have been {}'.format(Registry().functions_list.keys())
    assert 'application' in Registry().service_list, 'The application should have been registered.'
    assert 'main_window' in Registry().service_list, 'The main_window should have been registered.'
    assert 'settings' in Registry().service_list, 'The settings should have been registered.'


def test_projector_manager_hidden_on_startup(main_window):
    """
    Test that the projector manager is hidden on startup
    """
    # GIVEN: A built main window
    # WHEN: OpenLP is started
    # THEN: The projector manager should be hidden
    assert main_window.projector_manager_dock.isVisible() is False


def test_on_search_shortcut_triggered_shows_media_manager(main_window):
    """
    Test that the media manager is made visible when the search shortcut is triggered
    """
    # GIVEN: A build main window set up for testing
    with patch.object(main_window, 'media_manager_dock') as mocked_media_manager_dock, \
            patch.object(main_window, 'media_tool_box') as mocked_media_tool_box:
        mocked_media_manager_dock.isVisible.return_value = False
        mocked_media_tool_box.currentWidget.return_value = None

        # WHEN: The search shortcut is triggered
        main_window.on_search_shortcut_triggered()

        # THEN: The media manager dock is made visible
        mocked_media_manager_dock.setVisible.assert_called_with(True)


def test_on_search_shortcut_triggered_focuses_widget(main_window):
    """
    Test that the focus is set on the widget when the search shortcut is triggered
    """
    # GIVEN: A build main window set up for testing
    with patch.object(main_window, 'media_manager_dock') as mocked_media_manager_dock, \
            patch.object(main_window, 'media_tool_box') as mocked_media_tool_box:
        mocked_media_manager_dock.isVisible.return_value = True
        mocked_widget = MagicMock()
        mocked_media_tool_box.currentWidget.return_value = mocked_widget

        # WHEN: The search shortcut is triggered
        main_window.on_search_shortcut_triggered()

        # THEN: The media manager dock is made visible
        assert 0 == mocked_media_manager_dock.setVisible.call_count
        mocked_widget.on_focus.assert_called_with()


@patch('openlp.core.ui.mainwindow.FirstTimeForm')
@patch('openlp.core.ui.mainwindow.QtWidgets.QMessageBox.warning')
def test_on_first_time_wizard_clicked_show_projectors_after(mocked_warning, MockWizard, main_window):
    """Test that the projector manager is shown after the FTW is run"""
    # GIVEN: Main_window, patched things, patched "Yes" as confirmation to re-run wizard, settings to True.
    mocked_warning.return_value = QtWidgets.QMessageBox.Yes
    MockWizard.return_value.was_cancelled = False
    main_window.settings.setValue('projector/show after wizard', True)

    with patch.object(main_window, 'projector_manager_dock') as mocked_dock, \
            patch.object(Registry(), 'execute'), patch.object(main_window, 'theme_manager_contents'):
        # WHEN: on_first_time_wizard_clicked is called
        main_window.on_first_time_wizard_clicked()

    # THEN: projector_manager_dock.setVisible should had been called once
    mocked_dock.setVisible.assert_called_once_with(True)


@patch('openlp.core.ui.mainwindow.FirstTimeForm')
@patch('openlp.core.ui.mainwindow.QtWidgets.QMessageBox.warning')
def test_on_first_time_wizard_clicked_hide_projectors_after(mocked_warning, MockWizard, main_window):
    """Test that the projector manager is hidden after the FTW is run"""
    # GIVEN: Main_window, patched things, patched "Yes" as confirmation to re-run wizard, settings to False.
    mocked_warning.return_value = QtWidgets.QMessageBox.Yes
    MockWizard.return_value.was_cancelled = False
    main_window.settings.setValue('projector/show after wizard', False)

    # WHEN: on_first_time_wizard_clicked is called
    with patch.object(main_window, 'projector_manager_dock') as mocked_dock, \
            patch.object(Registry(), 'execute'), patch.object(main_window, 'theme_manager_contents'):
        main_window.on_first_time_wizard_clicked()

    # THEN: projector_manager_dock.setVisible should had been called once
    mocked_dock.setVisible.assert_called_once_with(False)


def test_increment_progress_bar_default_increment(main_window):
    """
    Test that increment_progress_bar increments the progress bar by 1 when called without the `increment` arg.
    """
    # GIVEN: A mocked progress bar
    with patch.object(main_window, 'load_progress_bar', **{'value.return_value': 0}) as mocked_progress_bar:

        # WHEN: Calling increment_progress_bar without the `increment` arg
        main_window.increment_progress_bar()

    # THEN: The progress bar value should have been incremented by 1
    mocked_progress_bar.setValue.assert_called_once_with(1)


def test_increment_progress_bar_custom_increment(main_window):
    """
    Test that increment_progress_bar increments the progress bar by the `increment` arg when called with the
    `increment` arg with a set value.
    """
    # GIVEN: A mocked progress bar
    with patch.object(main_window, 'load_progress_bar', **{'value.return_value': 0}) as mocked_progress_bar:

        # WHEN: Calling increment_progress_bar with `increment` set to 10
        main_window.increment_progress_bar(increment=10)

    # THEN: The progress bar value should have been incremented by 10
    mocked_progress_bar.setValue.assert_called_once_with(10)


def test_eventFilter(main_window):
    """
    Test the reimplemented event method
    """
    # GIVEN: A file path and a QEvent.
    file_path = str(RESOURCE_PATH / 'church.jpg')
    mocked_file_method = MagicMock(return_value=file_path)
    event = QtCore.QEvent(QtCore.QEvent.FileOpen)
    event.file = mocked_file_method

    # WHEN: Call the vent method.
    result = main_window.eventFilter(MagicMock(), event)

    # THEN: The path should be inserted.
    assert result is True, "The method should have returned True."
    mocked_file_method.assert_called_once_with()
    assert Registry().get('application').args[0] == file_path, "The path should be in args."


@patch('openlp.core.ui.mainwindow.is_macosx')
def test_application_activate_event(mocked_is_macosx, main_window):
    """
    Test that clicking on the dock icon on Mac OS X restores the main window if it is minimized
    """
    # GIVEN: Mac OS X and an ApplicationActivate event
    mocked_is_macosx.return_value = True
    event = QtCore.QEvent(QtCore.QEvent.ApplicationActivate)
    main_window.showMinimized()

    # WHEN: The icon in the dock is clicked
    result = main_window.eventFilter(MagicMock(), event)

    # THEN:
    assert result is True, "The method should have returned True."
    assert main_window.isMinimized() is False
