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
Package to test the openlp.core.widgets.widgets package.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.display.screens import Screen
from openlp.core.widgets.widgets import ScreenButton, ScreenSelectionWidget


class TestSceenButton(TestCase):
    def test_screen_button_initialisation(self):
        """
        Test the initialisation of the ScreenButton object
        """
        # GIVEN: A mocked screen object
        screen_mock = MagicMock(spec=Screen)
        screen_mock.number = 0
        screen_mock.__str__.return_value = 'Mocked Screen Object'

        # WHEN: initialising the ScreenButton object
        instance = ScreenButton(None, screen_mock)

        # THEN: The ScreenButton should have been initalised correctly with the data from the mocked screen object
        assert isinstance(instance, QtWidgets.QPushButton)
        assert instance.objectName() == 'screen_0_button'
        assert instance.isCheckable() is True
        assert instance.text() == 'Mocked Screen Object'


class TestScreenSelectionWidget(TestCase):
    def setUp(self):
        patched_qtimer = patch('openlp.core.widgets.widgets.QtCore.QTimer')
        self.addCleanup(patched_qtimer.stop)
        self.timer_mock = MagicMock(spec=QtCore.QTimer)
        qtimer_mock = patched_qtimer.start()
        qtimer_mock.return_value = self.timer_mock

        patched_screen_selection_widget_setup_ui = patch.object(ScreenSelectionWidget, 'setup_ui')
        self.addCleanup(patched_screen_selection_widget_setup_ui.stop)
        patched_screen_selection_widget_setup_ui.start()

    def test_init_default_args(self):
        """
        Test the initialisation of ScreenSelectionWidget, when initialised with default arguments
        """
        # GIVEN: The ScreenSelectionWidget class
        # WHEN: Initialising ScreenSelectionWidget with default arguments
        instance = ScreenSelectionWidget()

        # THEN: ScreenSelectionWidget should be an instance of QWidget and the screens attribute should be an empty list
        assert isinstance(instance, QtWidgets.QWidget)
        assert instance.screens == []
        self.timer_mock.setSingleShot.assert_called_once_with(True)
        self.timer_mock.setInterval.assert_called_once_with(3000)

    def test_init_with_args(self):
        """
        Test the initialisation of ScreenSelectionWidget, when initialised with the screens keyword arg set
        """
        # GIVEN: The ScreenSelectionWidget class
        screens_object_mock = MagicMock()

        # WHEN: Initialising ScreenSelectionWidget with the screens keyword arg set
        instance = ScreenSelectionWidget(screens=screens_object_mock)

        # THEN: ScreenSelectionWidget should be an instance of QWidget and the screens attribute should the mock used
        assert isinstance(instance, QtWidgets.QWidget)
        assert instance.screens is screens_object_mock
        self.timer_mock.setSingleShot.assert_called_once_with(True)
        self.timer_mock.setInterval.assert_called_once_with(3000)

    def test_save_screen_none(self):
        """
        Test ScreenSelectionWidget._save_screen when called with the screen arg set as None
        """
        # GIVEN: An instance of the ScreenSelectionWidget
        instance = ScreenSelectionWidget()
        instance.display_group_box = MagicMock(spec=QtWidgets.QGroupBox)

        # WHEN: Calling _save_screen and no screen is selected
        instance._save_screen(None)

        # THEN: _save_screen should return without attempting to write to the screen object
        instance.display_group_box.isChecked.assert_not_called()

    def test_save_screen_not_display(self):
        """
        Test ScreenSelectionWidget._save_screen when the display_group_box is not checked.
        """
        # GIVEN: An instance of the ScreenSelectionWidget, and a mocked group_box
        instance = ScreenSelectionWidget()
        instance.display_group_box = MagicMock(spec=QtWidgets.QGroupBox)
        instance.custom_geometry_button = MagicMock(spec=QtWidgets.QRadioButton, **{'isChecked.return_value': False})
        mocked_screen_object = MagicMock(spec=Screen)
        mocked_screen_object.is_dislpay = True

        # WHEN: display_group_box isn't checked and _save_screen is called with a mocked Screen object.
        instance.display_group_box.isChecked.return_value = False
        instance._save_screen(mocked_screen_object)

        # THEN: _save_screen should should be set to False
        assert mocked_screen_object.is_display is False

    def test_save_screen_display(self):
        """
        Test ScreenSelectionWidget._save_screen when the display_group_box is checked.
        """
        # GIVEN: An instance of the ScreenSelectionWidget, and a mocked group_box
        instance = ScreenSelectionWidget()
        instance.display_group_box = MagicMock(spec=QtWidgets.QGroupBox)
        instance.custom_geometry_button = MagicMock(spec=QtWidgets.QRadioButton, **{'isChecked.return_value': False})
        mocked_screen_object = MagicMock(spec=Screen)

        # WHEN: display_group_box is checked and _save_screen is called with a mocked Screen object.
        instance.display_group_box.isChecked.return_value = True
        instance._save_screen(mocked_screen_object)

        # THEN: _save_screen should should be set to True
        assert mocked_screen_object.is_display is True

    @patch('openlp.core.widgets.widgets.QtCore.QRect')
    def test_save_screen_full_screen(self, mocked_q_rect):
        """
        Test ScreenSelectionWidget._save_screen when the display is set to full screen
        """
        # GIVEN: An instance of the ScreenSelectionWidget, and a mocked custom_geometry_button
        instance = ScreenSelectionWidget()
        instance.display_group_box = MagicMock(spec=QtWidgets.QGroupBox)
        instance.custom_geometry_button = MagicMock(spec=QtWidgets.QRadioButton)
        mocked_screen_object = MagicMock(spec=Screen)

        # WHEN: custom_geometry_button isn't checked and _save_screen is called with a mocked Screen object.
        instance.custom_geometry_button.isChecked.return_value = False
        instance._save_screen(mocked_screen_object)

        # THEN: _save_screen should not attempt to save a custom geometry
        mocked_q_rect.assert_not_called()

    @patch('openlp.core.widgets.widgets.QtCore.QRect')
    def test_save_screen_custom_geometry(self, mocked_q_rect):
        """
        Test ScreenSelectionWidget._save_screen when a custom geometry is set
        """
        # GIVEN: An instance of the ScreenSelectionWidget, and a mocked custom_geometry_button
        instance = ScreenSelectionWidget()
        instance.display_group_box = MagicMock(spec=QtWidgets.QGroupBox)
        instance.custom_geometry_button = MagicMock(spec=QtWidgets.QRadioButton)
        instance.left_spin_box = MagicMock(spec=QtWidgets.QSpinBox, **{'value.return_value': 100})
        instance.top_spin_box = MagicMock(spec=QtWidgets.QSpinBox, **{'value.return_value': 200})
        instance.width_spin_box = MagicMock(spec=QtWidgets.QSpinBox, **{'value.return_value': 300})
        instance.height_spin_box = MagicMock(spec=QtWidgets.QSpinBox, **{'value.return_value': 400})
        mocked_screen_object = MagicMock(spec=Screen)

        # WHEN: custom_geometry_button is checked and _save_screen is called with a mocked Screen object.
        instance.custom_geometry_button.isChecked.return_value = True
        instance._save_screen(mocked_screen_object)

        # THEN: _save_screen should save the custom geometry
        mocked_q_rect.assert_called_once_with(100, 200, 300, 400)

    def test_setup_spin_box(self):
        """
        Test that ScreenSelectionWidget._setup_spin_box sets up the given spinbox correctly
        """
        # GIVEN: An instance of the ScreenSelectionWidget class and a mocked spin box object
        instance = ScreenSelectionWidget()
        spin_box_mock = MagicMock(spec=QtWidgets.QSpinBox)

        # WHEN: Calling _setup_spin_box with the mocked spin box object and some sample values
        instance._setup_spin_box(spin_box_mock, 0, 100, 50)

        # THEN: The mocked spin box object should have been set up with the specified values
        spin_box_mock.setMinimum.assert_called_once_with(0)
        spin_box_mock.setMaximum.assert_called_once_with(100)
        spin_box_mock.setValue.assert_called_once_with(50)
