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
Package to test the openlp.core.display.window package.
"""
import sys

from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore

# Mock QtWebEngineWidgets
sys.modules['PyQt5.QtWebEngineWidgets'] = MagicMock()

from openlp.core.display.window import DisplayWindow
from tests.helpers.testmixin import TestMixin


@patch('PyQt5.QtWidgets.QVBoxLayout')
@patch('openlp.core.display.webengine.WebEngineView')
@patch('openlp.core.display.window.Settings')
class TestDisplayWindow(TestCase, TestMixin):
    """
    A test suite to test the functions in DisplayWindow
    """

    def test_x11_override_on(self, MockSettings, mocked_webengine, mocked_addWidget):
        """
        Test that the x11 override option bit is set
        """
        # GIVEN: x11 bypass is on
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = True
        MockSettings.return_value = mocked_settings

        # WHEN: A DisplayWindow is generated
        display_window = DisplayWindow()

        # THEN: The x11 override flag should be set
        x11_bit = display_window.windowFlags() & QtCore.Qt.X11BypassWindowManagerHint
        assert x11_bit == QtCore.Qt.X11BypassWindowManagerHint

    def test_x11_override_off(self, MockSettings, mocked_webengine, mocked_addWidget):
        """
        Test that the x11 override option bit is not set when setting if off
        """
        # GIVEN: x11 bypass is off
        mocked_settings = MagicMock()
        mocked_settings.value.return_value = False
        MockSettings.return_value = mocked_settings

        # WHEN: A DisplayWindow is generated
        display_window = DisplayWindow()

        # THEN: The x11 override flag should not be set
        x11_bit = display_window.windowFlags() & QtCore.Qt.X11BypassWindowManagerHint
        assert x11_bit != QtCore.Qt.X11BypassWindowManagerHint
