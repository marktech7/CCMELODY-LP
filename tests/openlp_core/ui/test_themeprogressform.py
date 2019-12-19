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
Package to test the openlp.core.ui.themeform package.
"""
# from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.ui.themeprogressform import ThemeProgressForm
from tests.helpers.testmixin import TestMixin


class TestThemeProgressForm(TestCase, TestMixin):
    """
    Test the functions in the ThemeProgressForm class
    """
    def setUp(self):
        self.setup_application()

    def tearDown(self):
        del self.app

    def _get_theme_progress_form(self):
        """Common code used to create the ThemeProgressForm object"""
        with patch('openlp.core.ui.themeprogressdialog.ThemePreviewRenderer'), \
                patch('openlp.core.ui.themeprogressdialog.UiThemeProgressDialog.setup_ui'):
            form = ThemeProgressForm()
        return form

    def test_init(self):
        """Test that the ThemeProgressForm is created without problems"""
        # GIVEN: ThemeProgressForm class
        # WHEN: An object is instatiated
        # THEN: There is no problem
        self._get_theme_progress_form()

    @patch('openlp.core.ui.themeprogressform.ScreenList')
    @patch('openlp.core.ui.themeprogressform.QtWidgets.QDialog.show')
    def test_show(self, mocked_show, MockScreenList):
        """Test that the ThemeProgressForm is created without problems"""
        # GIVEN: ThemeProgressForm object
        form = self._get_theme_progress_form()
        mocked_screen_list = MagicMock()
        mocked_screen_list.current.display_geometry.width.return_value = 1920
        mocked_screen_list.current.display_geometry.height.return_value = 1080
        MockScreenList.return_value = mocked_screen_list
        form.progress_bar = MagicMock()
        form.theme_preview_layout = MagicMock()

        # WHEN: The show() method is called
        form.show()

        # THEN: The correct display ratio is calculated and the form is shown
        expected_ratio = 16 / 9
        form.progress_bar.setValue.assert_called_once_with(0)
        assert form.ratio == expected_ratio
        assert form.theme_preview_layout.aspect_ratio == expected_ratio
        mocked_show.assert_called_once()

    @patch('openlp.core.ui.themeprogressform.ScreenList')
    @patch('openlp.core.ui.themeprogressform.QtWidgets.QDialog.show')
    def test_show_divide_by_zero(self, mocked_show, MockScreenList):
        """Test that the ThemeProgressForm is created without problems even if there's a divide by zero exception"""
        # GIVEN: ThemeProgressForm object
        form = self._get_theme_progress_form()
        mocked_screen_list = MagicMock()
        mocked_screen_list.current.display_geometry.width.return_value = 1920
        mocked_screen_list.current.display_geometry.height.return_value = 0
        MockScreenList.return_value = mocked_screen_list
        form.progress_bar = MagicMock()
        form.theme_preview_layout = MagicMock()

        # WHEN: The show() method is called
        form.show()

        # THEN: The correct display ratio is calculated and the form is shown
        expected_ratio = 16 / 9
        form.progress_bar.setValue.assert_called_once_with(0)
        assert form.ratio == expected_ratio
        assert form.theme_preview_layout.aspect_ratio == expected_ratio
        mocked_show.assert_called_once()

    def test_get_preview(self):
        """Test that the get_preview() method returns a preview image"""
        # GIVEN: ThemeProgressForm object
        test_theme_name = 'Test Theme'
        test_theme_data = {'name': test_theme_name}
        form = self._get_theme_progress_form()
        form.progress_bar = MagicMock(**{'value.return_value': 0})
        form.label = MagicMock()
        form.theme_display = MagicMock(**{'width.return_value': 192, 'generate_preview.return_value': 'preview'})
        form.renderer.width = MagicMock(return_value=1920)

        # WHEN: get_preview() is called
        preview = form.get_preview(test_theme_name, test_theme_data)

        # THEN: All the correct methods should be called and the correct results should be returned
        form.label.setText.assert_called_once_with(test_theme_name)
        form.progress_bar.value.assert_called_once()
        form.progress_bar.setValue.assert_called_once_with(1)
        form.theme_display.width.assert_called_once()
        form.renderer.width.assert_called_once()
        form.theme_display.set_scale.assert_called_once_with(0.1)
        form.theme_display.generate_preview.assert_called_once_with(test_theme_data, generate_screenshot=True)
        assert preview == 'preview'

    def test_theme_list(self):
        # GIVEN: ThemeProgressForm object and theme list
        test_theme_list = ['Theme 1', 'Theme 2']
        form = self._get_theme_progress_form()
        form.progress_bar = MagicMock()

        # WHEN: theme_list is set and get'ed
        form.theme_list = test_theme_list
        theme_list = form.theme_list

        # THEN: The theme list should be correct
        form.progress_bar.setMaximum.assert_called_once_with(2)
        assert theme_list == test_theme_list
