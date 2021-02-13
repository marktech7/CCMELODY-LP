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
Package to test the screens tab functionality (primarily ScreenSelectionWidget and ScreenButton classes)
within openlp/core/widgets/widgets.py
"""

import pytest

from unittest.mock import MagicMock, patch

from PyQt5 import QtWidgets, QtCore, QtTest

from openlp.core.widgets.widgets import ScreenSelectionWidget


@pytest.fixture()
def form(settings):
    test_form = ScreenSelectionWidget()
    return test_form


def mocked_screens(customGeometry):
    screen0 = MagicMock()
    screen0.number = 0
    screen0.is_display = True
    screen0.is_primary = False
    screen0.geometry = QtCore.QRect(-271, -1080, 1920, 1080)
    screen0.custom_geometry = customGeometry
    screen0.__str__.return_value = "Screen 1"
    screen1 = MagicMock()
    screen1.number = 1
    screen1.is_display = False
    screen1.is_primary = True
    screen1.geometry = QtCore.QRect(0, 0, 1366, 768)
    screen1.custom_geometry = customGeometry
    screen1.__str__.return_value = "Screen 2"
    return [screen0, screen1]


@patch('openlp.core.display.screens.ScreenList')
def test_screen_buttons_show_pixels(mocked_screenList, form):
    '''
    Test that the screen buttons show the screen sizes in pixels
    '''
    # GIVEN: A mocked extended desktop configuration

    mocked_screenList.return_value = mocked_screens(None)
    form.screens = mocked_screenList()

    # WHEN: When I go into screen settings for the display screen
    ScreenSelectionWidget.load(form)

    # THEN: The screen buttons should show the correct size of that screen
    screen_0_button = form.findChild(QtWidgets.QPushButton, 'screen_0_button')
    screen_1_button = form.findChild(QtWidgets.QPushButton, 'screen_1_button')
    assert '1920' in str(screen_0_button.text())
    assert '1080' in str(screen_0_button.text())
    assert '1366' in str(screen_1_button.text())
    assert '768' in str(screen_1_button.text())


@patch('openlp.core.display.screens.ScreenList')
def test_spinboxes_no_previous_custom_geometry(mocked_screenList, form):
    """
    Test screen custom geometry can be changed from None
    """
    # GIVEN: A mocked extended desktop configuration

    mocked_screenList.return_value = mocked_screens(None)
    form.screens = mocked_screenList()

    # WHEN: When I go into screen settings for the display screen and set the custom geometry
    ScreenSelectionWidget.load(form)
    QtTest.QTest.mouseClick(form.custom_geometry_button, QtCore.Qt.LeftButton)
    QtTest.QTest.keyClick(form.left_spin_box, QtCore.Qt.Key_Up)
    QtTest.QTest.keyClick(form.top_spin_box, QtCore.Qt.Key_Up)
    QtTest.QTest.keyClick(form.width_spin_box, QtCore.Qt.Key_Down)
    QtTest.QTest.keyClick(form.height_spin_box, QtCore.Qt.Key_Down)

    # THEN: The spin boxes should show the correct values
    assert form.left_spin_box.value() == 1
    assert form.top_spin_box.value() == 1
    assert form.width_spin_box.value() == 1919
    assert form.height_spin_box.value() == 1079


@patch('openlp.core.display.screens.ScreenList')
def test_spinboxes_with_previous_custom_geometry(mocked_screenList, form):
    """
    Test screen existing custom geometry can be changed
    """
    # GIVEN: A mocked extended desktop configuration

    testGeometry = QtCore.QRect(1, 1, 1919, 1079)
    mocked_screenList.return_value = mocked_screens(testGeometry)
    form.screens = mocked_screenList()

    # WHEN: When I go into screen settings for the display screen and update the custom geometry
    ScreenSelectionWidget.load(form)
    QtTest.QTest.mouseClick(form.custom_geometry_button, QtCore.Qt.LeftButton)
    QtTest.QTest.keyClick(form.left_spin_box, QtCore.Qt.Key_Up)
    QtTest.QTest.keyClick(form.top_spin_box, QtCore.Qt.Key_Up)
    QtTest.QTest.keyClick(form.width_spin_box, QtCore.Qt.Key_Down)
    QtTest.QTest.keyClick(form.height_spin_box, QtCore.Qt.Key_Down)

    # THEN: The spin boxes should show the updated values
    assert form.left_spin_box.value() == 2
    assert form.top_spin_box.value() == 2
    assert form.width_spin_box.value() == 1918
    assert form.height_spin_box.value() == 1078


@patch('openlp.core.display.screens.ScreenList')
def test_spinboxes_going_outside_screen_geometry(mocked_screenList, form):
    """
    Test screen existing custom geometry can be increased beyond the bounds of the screen
    """
    # GIVEN: A mocked extended desktop configuration

    testGeometry = QtCore.QRect(1, 1, 1919, 1079)
    mocked_screenList.return_value = mocked_screens(testGeometry)
    form.screens = mocked_screenList()

    # WHEN: When I go into screen settings for the display screen and
    #       update the custom geometry to be outside the screen coordinates
    ScreenSelectionWidget.load(form)
    QtTest.QTest.mouseClick(form.custom_geometry_button, QtCore.Qt.LeftButton)
    for _ in range(2):
        QtTest.QTest.keyClick(form.left_spin_box, QtCore.Qt.Key_Down)
        QtTest.QTest.keyClick(form.top_spin_box, QtCore.Qt.Key_Down)
        QtTest.QTest.keyClick(form.width_spin_box, QtCore.Qt.Key_Up)
        QtTest.QTest.keyClick(form.height_spin_box, QtCore.Qt.Key_Up)

    # THEN: The spin boxes should show the updated values
    assert form.left_spin_box.value() == -1
    assert form.top_spin_box.value() == -1
    assert form.width_spin_box.value() == 1921
    assert form.height_spin_box.value() == 1081
