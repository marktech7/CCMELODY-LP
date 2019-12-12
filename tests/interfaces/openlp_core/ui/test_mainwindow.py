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
Package to test the openlp.core.ui.mainwindow package.
"""
from unittest import TestCase, skipIf
from unittest.mock import MagicMock, patch

from PyQt5 import QtGui

from openlp.core.state import State
from openlp.core.common import is_macosx
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus
from openlp.core.ui.mainwindow import MainWindow
from tests.helpers.testmixin import TestMixin


@skipIf(is_macosx(), 'Skip on macOS until we can figure out what the problem is or the tests are refactored')
class TestMainWindow(TestCase, TestMixin):

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.registry = Registry()
        self.setup_application()
        # Mock cursor busy/normal methods.
        self.app.set_busy_cursor = MagicMock()
        self.app.set_normal_cursor = MagicMock()
        self.app.args = []
        Registry().register('application', self.app)
        Registry().set_flag('no_web_server', True)
        mocked_plugin = MagicMock()
        mocked_plugin.status = PluginStatus.Active
        mocked_plugin.icon = QtGui.QIcon()
        Registry().register('mock_plugin', mocked_plugin)
        State().add_service("mock", 1, is_plugin=True, status=PluginStatus.Active)
        # Mock classes and methods used by mainwindow.
        with patch('openlp.core.ui.mainwindow.SettingsForm'), \
                patch('openlp.core.ui.mainwindow.OpenLPDockWidget'), \
                patch('openlp.core.ui.mainwindow.QtWidgets.QToolBox'), \
                patch('openlp.core.ui.mainwindow.QtWidgets.QMainWindow.addDockWidget'), \
                patch('openlp.core.ui.mainwindow.ServiceManager'), \
                patch('openlp.core.ui.mainwindow.ThemeManager'), \
                patch('openlp.core.ui.mainwindow.ProjectorManager'), \
                patch('openlp.core.ui.mainwindow.HttpServer'), \
                patch('openlp.core.ui.mainwindow.WebSocketServer'), \
                patch('openlp.core.ui.mainwindow.start_zeroconf'), \
                patch('openlp.core.ui.mainwindow.PluginForm'):
            self.main_window = MainWindow()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.main_window

    def test_restore_current_media_manager_item(self):
        """
        Regression test for bug #1152509.
        """
        # GIVEN: Mocked Settings().value method.
        with patch('openlp.core.ui.mainwindow.Settings.value') as mocked_value:
            # save current plugin: True; current media plugin: 2
            mocked_value.side_effect = [True, 2]

            # WHEN: Call the restore method.
            self.main_window.restore_current_media_manager_item()

            # THEN: The current widget should have been set.
            self.main_window.media_tool_box.setCurrentIndex.assert_called_with(2)

    def test_projector_manager_dock_locked(self):
        """
        Projector Manager enable UI options -  bug #1390702
        """
        # GIVEN: A mocked projector manager dock item:
        projector_dock = self.main_window.projector_manager_dock

        # WHEN: main_window.lock_panel action is triggered
        self.main_window.lock_panel.triggered.emit(True)

        # THEN: Projector manager dock should have been called with disable UI features
        projector_dock.setFeatures.assert_called_with(0)

    def test_projector_manager_dock_unlocked(self):
        """
        Projector Manager disable UI options -  bug #1390702
        """
        # GIVEN: A mocked projector manager dock item:
        projector_dock = self.main_window.projector_manager_dock

        # WHEN: main_window.lock_panel action is triggered
        self.main_window.lock_panel.triggered.emit(False)

        # THEN: Projector manager dock should have been called with enable UI features
        projector_dock.setFeatures.assert_called_with(7)
