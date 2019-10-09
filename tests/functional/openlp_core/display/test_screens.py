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


def test_screen_from_dict():
    """Test that all the correct attributes are set when creating a screen from a dictionary"""
    # GIVEN: A dictionary of values
    screen_dict = {
        'number': 1,
        'geometry': {'x': 0, 'y': 0, 'width': 1920, 'height': 1080},
        'custom_geometry': {'x': 10, 'y': 10, 'width': 1900, 'height': 1060},
        'is_primary': True,
        'is_display': False
    }

    # WHEN: A screen object is created from a dictionary
    screen = Screen.from_dict(screen_dict)

    # THEN: A screen object with the correct attributes is created
    assert screen.number == 1
    assert screen.is_primary is True
    assert screen.is_display is False
    assert screen.geometry == QtCore.QRect(0, 0, 1920, 1080)
    assert screen.custom_geometry == QtCore.QRect(10, 10, 1900, 1060)


def test_screen_to_dict():
    """Test that the correct dictionary is generated"""
    # GIVEN: A screen object
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), QtCore.QRect(10, 10, 1900, 1060), True, False)

    # WHEN: A dictionary is generated
    screen_dict = screen.to_dict()

    # THEN: The dictionary should be correct
    expected_screen = {
        'number': 1,
        'geometry': {'x': 0, 'y': 0, 'width': 1920, 'height': 1080},
        'custom_geometry': {'x': 10, 'y': 10, 'width': 1900, 'height': 1060},
        'is_primary': True,
        'is_display': False
    }
    assert screen_dict == expected_screen


def test_screen_update():
    """Test that updating a screen object from a dictionary results in the correct attributes"""
    # GIVEN: A screen object and a dictionary with updated values
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), is_primary=True, is_display=False)
    updated_screen = {
        'geometry': {'x': 0, 'y': 0, 'width': 3840, 'height': 2160},
        'custom_geometry': {'x': 10, 'y': 10, 'width': 1900, 'height': 1060},
        'is_primary': False,
        'is_display': True
    }

    # WHEN: screen.update() is called
    screen.update(updated_screen)

    # Then the screen attributes should be correct
    assert screen.is_primary is False
    assert screen.is_display is True
    assert screen.geometry == QtCore.QRect(0, 0, 3840, 2160)
    assert screen.custom_geometry == QtCore.QRect(10, 10, 1900, 1060)


def test_screen_update_bad_geometry():
    """Test that updating a screen object from a dictionary results in the correct attributes"""
    # GIVEN: A screen object and a dictionary with updated values
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), is_primary=True, is_display=False)
    updated_screen = {
        'geometry': {'x': 0, 'y': 0, 'x2': 3840, 'y2': 2160},
        'custom_geometry': {'x': 10, 'y': 10, 'width': 1900, 'height': 1060},
        'is_primary': False,
        'is_display': True
    }

    # WHEN: screen.update() is called
    screen.update(updated_screen)

    # Then the screen attributes should be correct
    assert screen.is_primary is False
    assert screen.is_display is True
    assert screen.geometry == QtCore.QRect(0, 0, 1920, 1080)
    assert screen.custom_geometry == QtCore.QRect(10, 10, 1900, 1060)


def test_screen_to_str():
    """Test that the correct string is generated"""
    # GIVEN: A screen object
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), QtCore.QRect(10, 10, 1900, 1060), True, False)

    # WHEN: A string is generated
    screen_str = str(screen)

    # THEN: The string should be correct (screens are 0-based)
    assert screen_str == 'Screen 2 (primary)'


def test_screen_display_geometry():
    """Test that the display_geometry property returns the geometry when no custom geometry exists"""
    # GIVEN: A screen object
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), is_primary=True, is_display=False)

    # WHEN: The display_geometry property is accessed
    display_geometry = screen.display_geometry

    # THEN: The display geometry is correct
    assert display_geometry == QtCore.QRect(0, 0, 1920, 1080)


def test_screen_display_geometry_custom():
    """Test that the display_geometry property returns the custom geometry when it exists"""
    # GIVEN: A screen object
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), QtCore.QRect(10, 10, 1900, 1060), True, False)

    # WHEN: The display_geometry property is accessed
    display_geometry = screen.display_geometry

    # THEN: The display geometry is correct
    assert display_geometry == QtCore.QRect(10, 10, 1900, 1060)


def test_screen_repr():
    """Test that the correct screen representation is generated"""
    # GIVEN: A screen object
    screen = Screen(1, QtCore.QRect(0, 0, 1920, 1080), QtCore.QRect(10, 10, 1900, 1060), True, False)

    # WHEN: A string is generated
    screen_str = screen.__repr__()

    # THEN: The string should be correct (screens are 0-based)
    assert screen_str == '<Screen 2 (primary)>'
