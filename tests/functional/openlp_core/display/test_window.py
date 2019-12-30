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
Package to test the openlp.core.display.window package.
"""
import sys
import time

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

    def test_set_scale_not_initialised(self, MockSettings, mocked_webengine, mocked_addWidget):
        """
        Test that the scale js is not run if the page is not initialised
        """
        # GIVEN: A display window not yet initialised
        display_window = DisplayWindow()
        display_window._is_initialised = False
        display_window.run_javascript = MagicMock()

        # WHEN: set scale is run
        display_window.set_scale(0.5)

        # THEN: javascript should not be run
        display_window.run_javascript.assert_not_called()

    def test_set_scale_initialised(self, MockSettings, mocked_webengine, mocked_addWidget):
        """
        Test that the scale js is not run if the page is not initialised
        """
        # GIVEN: A display window not yet initialised
        display_window = DisplayWindow()
        display_window._is_initialised = True
        display_window.run_javascript = MagicMock()

        # WHEN: set scale is run
        display_window.set_scale(0.5)

        # THEN: javascript should not be run
        display_window.run_javascript.assert_called_once_with('Display.setScale(50.0);')

    @patch.object(time, 'time')
    def test_run_javascript_no_sync_no_wait(self, MockSettings, mocked_webengine, mocked_addWidget, mock_time):
        """
        test a script is run on the webview
        """
        # GIVEN: A (fake) webengine page
        display_window = DisplayWindow()
        webengine_page = MagicMock()
        display_window.webview.page = MagicMock(return_value=webengine_page)

        # WHEN: javascript is requested to run
        display_window.run_javascript('javascript to execute')

        # THEN: javascript should be run with no delay
        webengine_page.runJavaScript.assert_called_once_with('javascript to execute')
        mock_time.sleep.assert_not_called()

    @patch.object(time, 'time')
    def test_run_javascript_sync_no_wait(self, MockSettings, mocked_webengine, mocked_addWidget, mock_time):
        """
        test a synced script is run on the webview and immediately returns a result
        """
        # GIVEN: A (fake) webengine page with a js callback fn
        def save_callback(script, callback):
            callback(1234)
        display_window = DisplayWindow()
        display_window.webview = MagicMock()
        webengine_page = MagicMock()
        webengine_page.runJavaScript.side_effect = save_callback
        display_window.webview.page.return_value = webengine_page

        # WHEN: javascript is requested to run
        result = display_window.run_javascript('javascript to execute', True)

        # THEN: javascript should be run with no delay and return with the correct result
        assert result == 1234
        webengine_page.runJavaScript.assert_called_once()
        mock_time.sleep.assert_not_called()
