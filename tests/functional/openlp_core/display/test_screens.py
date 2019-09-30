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
Package to test the openlp.core.lib.screenlist package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.display.screens import Screen, ScreenList


SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}


class TestScreenList(TestCase):

    def setUp(self):
        """
        Set up the components need for all tests.
        """
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']

        self.application = QtWidgets.QApplication.instance()
        Registry.create()
        self.application.setOrganizationName('OpenLP-tests')
        self.application.setOrganizationDomain('openlp.org')
        self.screens = ScreenList.create(self.desktop)

    def tearDown(self):
        """
        Delete QApplication.
        """
        del self.screens
        del self.application

    def test_current_display_screen(self):
        """
        Test that the "current" property returns the first display screen
        """
        # GIVEN: A new ScreenList object with some screens
        screen_list = ScreenList()
        screen_list.screens = [
            Screen(number=0, geometry=QtCore.QRect(0, 0, 1024, 768), is_primary=True),
            Screen(number=1, geometry=QtCore.QRect(1024, 0, 1024, 768), is_primary=False, is_display=True)
        ]

        # WHEN: The current property is accessed
        screen = screen_list.current

        # THEN: It should be the display screen
        assert screen.number == 1
        assert screen.geometry == QtCore.QRect(1024, 0, 1024, 768)
        assert screen.is_primary is False
        assert screen.is_display is True

    def test_current_primary_screen(self):
        """
        Test that the "current" property returns the first primary screen
        """
        # GIVEN: A new ScreenList object with some screens
        screen_list = ScreenList()
        screen_list.screens = [
            Screen(number=0, geometry=QtCore.QRect(0, 0, 1024, 768), is_primary=True)
        ]

        # WHEN: The current property is accessed
        screen = screen_list.current

        # THEN: It should be the display screen
        assert screen.number == 0
        assert screen.geometry == QtCore.QRect(0, 0, 1024, 768)
        assert screen.is_primary is True
        assert screen.is_display is False

    @patch('openlp.core.display.screens.QtWidgets.QApplication.screens')
    def test_create_screen_list(self, mocked_screens):
        """
        Create the screen list
        """
        # GIVEN: Mocked desktop
        mocked_desktop = MagicMock()
        mocked_desktop.screenCount.return_value = 2
        mocked_desktop.primaryScreen.return_value = 0
        mocked_screens.return_value = [
            MagicMock(**{'geometry.return_value': QtCore.QRect(0, 0, 1024, 768)}),
            MagicMock(**{'geometry.return_value': QtCore.QRect(1024, 0, 1024, 768)})
        ]

        # WHEN: create() is called
        screen_list = ScreenList.create(mocked_desktop)

        # THEN: The correct screens have been set up
        assert screen_list.screens[0].number == 0
        assert screen_list.screens[0].geometry == QtCore.QRect(0, 0, 1024, 768)
        assert screen_list.screens[0].is_primary is True
        assert screen_list.screens[1].number == 1
        assert screen_list.screens[1].geometry == QtCore.QRect(1024, 0, 1024, 768)
        assert screen_list.screens[1].is_primary is False
