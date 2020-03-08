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
Package to test the openlp.core.ui.mainwindow package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PyQt5 import QtGui

from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus
from openlp.core.ui.mainwindow import MainWindow


@pytest.fixture()
def main_window(settings, state):
    """
    Create the UI
    """
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
        return MainWindow()


def test_restore_current_media_manager_item(main_window):
    """
    Regression test for bug #1152509.
    """
    # save current plugin: True; current media plugin: 2
    main_window.settings.setValue('advanced/save current plugin', True)
    main_window.settings.setValue('advanced/current media plugin', 2)

    # WHEN: Call the restore method.
    main_window.restore_current_media_manager_item()

    # THEN: The current widget should have been set.
    main_window.media_tool_box.setCurrentIndex.assert_called_with(2)


def test_projector_manager_dock_locked(main_window):
    """
    Projector Manager enable UI options -  bug #1390702
    """
    # GIVEN: A mocked projector manager dock item:
    projector_dock = main_window.projector_manager_dock

    # WHEN: main_window.lock_panel action is triggered
    main_window.lock_panel.triggered.emit(True)

    # THEN: Projector manager dock should have been called with disable UI features
    projector_dock.setFeatures.assert_called_with(0)


def test_projector_manager_dock_unlocked(main_window):
    """
    Projector Manager disable UI options -  bug #1390702
    """
    # GIVEN: A mocked projector manager dock item:
    projector_dock = main_window.projector_manager_dock

    # WHEN: main_window.lock_panel action is triggered
    main_window.lock_panel.triggered.emit(False)

    # THEN: Projector manager dock should have been called with enable UI features
    projector_dock.setFeatures.assert_called_with(7)
