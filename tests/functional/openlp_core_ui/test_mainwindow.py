# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2017 OpenLP Developers                                   #
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
Package to test openlp.core.ui.mainwindow package.
"""
import os

from unittest import TestCase

from openlp.core.ui.mainwindow import MainWindow
from openlp.core.lib.ui import UiStrings
from openlp.core.common.registry import Registry

from tests.functional import MagicMock, patch
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestMainWindow(TestCase, TestMixin):

    def setUp(self):
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        # Mock cursor busy/normal methods.
        self.app.set_busy_cursor = MagicMock()
        self.app.set_normal_cursor = MagicMock()
        self.app.args = []
        Registry().register('application', self.app)
        # Mock classes and methods used by mainwindow.
        with patch('openlp.core.ui.mainwindow.SettingsForm') as mocked_settings_form, \
                patch('openlp.core.ui.mainwindow.ImageManager') as mocked_image_manager, \
                patch('openlp.core.ui.mainwindow.LiveController') as mocked_live_controller, \
                patch('openlp.core.ui.mainwindow.PreviewController') as mocked_preview_controller, \
                patch('openlp.core.ui.mainwindow.OpenLPDockWidget') as mocked_dock_widget, \
                patch('openlp.core.ui.mainwindow.QtWidgets.QToolBox') as mocked_q_tool_box_class, \
                patch('openlp.core.ui.mainwindow.QtWidgets.QMainWindow.addDockWidget') as mocked_add_dock_method, \
                patch('openlp.core.ui.mainwindow.ThemeManager') as mocked_theme_manager, \
                patch('openlp.core.ui.mainwindow.Renderer') as mocked_renderer:
            self.mocked_settings_form = mocked_settings_form
            self.mocked_image_manager = mocked_image_manager
            self.mocked_live_controller = mocked_live_controller
            self.mocked_preview_controller = mocked_preview_controller
            self.mocked_dock_widget = mocked_dock_widget
            self.mocked_q_tool_box_class = mocked_q_tool_box_class
            self.mocked_add_dock_method = mocked_add_dock_method
            self.mocked_theme_manager = mocked_theme_manager
            self.mocked_renderer = mocked_renderer
            self.main_window = MainWindow()

    def tearDown(self):
        del self.main_window

    def cmd_line_file_test(self):
        """
        Test that passing a service file from the command line loads the service.
        """
        # GIVEN a service as an argument to openlp
        service = os.path.join(TEST_RESOURCES_PATH, 'service', 'test.osz')
        self.main_window.arguments = [service]
        with patch('openlp.core.ui.servicemanager.ServiceManager.load_file') as mocked_load_path:

            # WHEN the argument is processed
            self.main_window.open_cmd_line_files(service)

            # THEN the service from the arguments is loaded
            mocked_load_path.assert_called_with(service), 'load_path should have been called with the service\'s path'

    def cmd_line_arg_test(self):
        """
        Test that passing a non service file does nothing.
        """
        # GIVEN a non service file as an argument to openlp
        service = os.path.join('openlp.py')
        self.main_window.arguments = [service]
        with patch('openlp.core.ui.servicemanager.ServiceManager.load_file') as mocked_load_path:

            # WHEN the argument is processed
            self.main_window.open_cmd_line_files("")

            # THEN the file should not be opened
            assert not mocked_load_path.called, 'load_path should not have been called'

    def main_window_title_test(self):
        """
        Test that running a new instance of OpenLP set the window title correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN no changes are made to the service

        # THEN the main window's title shoud be the same as the OLPV2x string in the UiStrings class
        self.assertEqual(self.main_window.windowTitle(), UiStrings().OLPV2x,
                         'The main window\'s title should be the same as the OLPV2x string in UiStrings class')

    def set_service_modifed_test(self):
        """
        Test that when setting the service's title the main window's title is set correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN set_service_modified is called with with the modified flag set true and a file name
        self.main_window.set_service_modified(True, 'test.osz')

        # THEN the main window's title should be set to the
        self.assertEqual(self.main_window.windowTitle(), '%s - %s*' % (UiStrings().OLPV2x, 'test.osz'),
                         'The main window\'s title should be set to "<the contents of UiStrings().OLPV2x> - test.osz*"')

    def set_service_unmodified_test(self):
        """
        Test that when setting the service's title the main window's title is set correctly
        """
        # GIVEN a newly opened OpenLP instance

        # WHEN set_service_modified is called with with the modified flag set False and a file name
        self.main_window.set_service_modified(False, 'test.osz')

        # THEN the main window's title should be set to the
        self.assertEqual(self.main_window.windowTitle(), '%s - %s' % (UiStrings().OLPV2x, 'test.osz'),
                         'The main window\'s title should be set to "<the contents of UiStrings().OLPV2x> - test.osz"')

    def mainwindow_configuration_test(self):
        """
        Check that the Main Window initialises the Registry Correctly
        """
        # GIVEN: A built main window

        # WHEN: you check the started functions

        # THEN: the following registry functions should have been registered
        self.assertEqual(len(self.registry.service_list), 6, 'The registry should have 6 services.')
        self.assertEqual(len(self.registry.functions_list), 16, 'The registry should have 16 functions')
        self.assertTrue('application' in self.registry.service_list, 'The application should have been registered.')
        self.assertTrue('main_window' in self.registry.service_list, 'The main_window should have been registered.')
        self.assertTrue('media_controller' in self.registry.service_list, 'The media_controller should have been '
                                                                          'registered.')
        self.assertTrue('plugin_manager' in self.registry.service_list,
                        'The plugin_manager should have been registered.')

    def test_projector_dock_hidden_by_default(self):
        """
        Test that the projector dock is hidden by default
        """
        # GIVEN: A main window
        # WHEN: OpenLP starts
        # THEN: The projector dock is hidden
        self.main_window.projector_manager_dock.setVisible.assert_called_once_with(False)

    def on_search_shortcut_triggered_shows_media_manager_test(self):
        """
        Test that the media manager is made visible when the search shortcut is triggered
        """
        # GIVEN: A build main window set up for testing
        with patch.object(self.main_window, 'media_manager_dock') as mocked_media_manager_dock, \
                patch.object(self.main_window, 'media_tool_box') as mocked_media_tool_box:
            mocked_media_manager_dock.isVisible.return_value = False
            mocked_media_tool_box.currentWidget.return_value = None

            # WHEN: The search shortcut is triggered
            self.main_window.on_search_shortcut_triggered()

            # THEN: The media manager dock is made visible
            mocked_media_manager_dock.setVisible.assert_called_with(True)

    def on_search_shortcut_triggered_focuses_widget_test(self):
        """
        Test that the focus is set on the widget when the search shortcut is triggered
        """
        # GIVEN: A build main window set up for testing
        with patch.object(self.main_window, 'media_manager_dock') as mocked_media_manager_dock, \
                patch.object(self.main_window, 'media_tool_box') as mocked_media_tool_box:
            mocked_media_manager_dock.isVisible.return_value = True
            mocked_widget = MagicMock()
            mocked_media_tool_box.currentWidget.return_value = mocked_widget

            # WHEN: The search shortcut is triggered
            self.main_window.on_search_shortcut_triggered()

            # THEN: The media manager dock is made visible
            self.assertEqual(0, mocked_media_manager_dock.setVisible.call_count)
            mocked_widget.on_focus.assert_called_with()
