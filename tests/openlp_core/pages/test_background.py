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
Package to test the openlp.core.pages.background package.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

import pytest

from openlp.core.lib.theme import BackgroundType, BackgroundGradientType
from openlp.core.pages.background import BackgroundPage
from tests.helpers.testmixin import TestMixin


class TestBackgroundPage(TestCase, TestMixin):

    def setUp(self):
        """Test setup"""
        self.setup_application()
        self.build_settings()

    def tearDown(self):
        """Tear down tests"""
        del self.app

    def test_init_(self):
        """
        Test the initialisation of BackgroundPage
        """
        # GIVEN: The BackgroundPage class
        # WHEN: Initialising BackgroundPage
        # THEN: We should have an instance of the widget with no errors
        BackgroundPage()

    def test_on_background_type_index_changed(self):
        """
        Test the _on_background_type_index_changed() slot
        """
        # GIVEN: And instance of BackgroundPage and some mock widgets
        page = BackgroundPage()
        page.color_widgets = [MagicMock()]
        page.gradient_widgets = [MagicMock()]

        # WHEN: _on_background_type_index_changed
        page._on_background_type_index_changed(1)

        # THEN: The correct widgets should be visible
        page.color_widgets[0].hide.assert_called_once()
        page.gradient_widgets[0].hide.assert_called_once()
        page.gradient_widgets[0].show.assert_called_once()

    def test_get_background_type(self):
        """
        Test the background_type getter
        """
        # GIVEN: A BackgroundPage instance with the combobox set to index 1
        page = BackgroundPage()
        page.background_combo_box.setCurrentIndex(1)

        # WHEN: The property is accessed
        result = page.background_type

        # THEN: The result should be correct
        assert result == 'gradient'

    def test_set_background_type_int(self):
        """
        Test the background_type setter with an int
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.background_type = BackgroundType.Image

        # THEN: The combobox should be correct
        assert page.background_combo_box.currentIndex() == 2

    def test_set_background_type_str(self):
        """
        Test the background_type setter with a str
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.background_type = BackgroundType.to_string(BackgroundType.Gradient)

        # THEN: The combobox should be correct
        assert page.background_combo_box.currentIndex() == 1

    def test_set_background_type_exception(self):
        """
        Test the background_type setter with something other than a str or int
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        # THEN: An exception is raised
        with pytest.raises(TypeError, match='background_type must either be a string or an int'):
            page.background_type = []

    def test_get_color(self):
        """
        Test the color getter
        """
        # GIVEN: A BackgroundPage instance with the color button set to #f0f
        page = BackgroundPage()
        page.color_button.color = '#f0f'

        # WHEN: The property is accessed
        result = page.color

        # THEN: The result should be correct
        assert result == '#f0f'

    def test_set_color(self):
        """
        Test the color setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.color = '#0f0'

        # THEN: The result should be correct
        assert page.color_button.color == '#0f0'

    def test_get_gradient_type(self):
        """
        Test the gradient_type getter
        """
        # GIVEN: A BackgroundPage instance with the combobox set to index 1
        page = BackgroundPage()
        page.gradient_combo_box.setCurrentIndex(1)

        # WHEN: The property is accessed
        result = page.gradient_type

        # THEN: The result should be correct
        assert result == 'vertical'

    def test_set_gradient_type_int(self):
        """
        Test the gradient_type setter with an int
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.gradient_type = BackgroundGradientType.Horizontal

        # THEN: The combobox should be correct
        assert page.gradient_combo_box.currentIndex() == 0

    def test_set_gradient_type_str(self):
        """
        Test the gradient_type setter with a str
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.gradient_type = BackgroundGradientType.to_string(BackgroundGradientType.Circular)

        # THEN: The combobox should be correct
        assert page.gradient_combo_box.currentIndex() == 2

    def test_set_gradient_type_exception(self):
        """
        Test the gradient_type setter with something other than a str or int
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        # THEN: An exception is raised
        with pytest.raises(TypeError, match='gradient_type must either be a string or an int'):
            page.gradient_type = []

    def test_get_gradient_start(self):
        """
        Test the gradient_start getter
        """
        # GIVEN: A BackgroundPage instance with the gradient_start button set to #f0f
        page = BackgroundPage()
        page.gradient_start_button.color = '#f0f'

        # WHEN: The property is accessed
        result = page.gradient_start

        # THEN: The result should be correct
        assert result == '#f0f'

    def test_set_gradient_start(self):
        """
        Test the gradient_start setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.gradient_start = '#0f0'

        # THEN: The result should be correct
        assert page.gradient_start_button.color == '#0f0'

    def test_get_gradient_end(self):
        """
        Test the gradient_end getter
        """
        # GIVEN: A BackgroundPage instance with the gradient_end button set to #f0f
        page = BackgroundPage()
        page.gradient_end_button.color = '#f0f'

        # WHEN: The property is accessed
        result = page.gradient_end

        # THEN: The result should be correct
        assert result == '#f0f'

    def test_set_gradient_end(self):
        """
        Test the gradient_end setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.gradient_end = '#0f0'

        # THEN: The result should be correct
        assert page.gradient_end_button.color == '#0f0'

    def test_get_image_color(self):
        """
        Test the image_color getter
        """
        # GIVEN: A BackgroundPage instance with the image_color button set to #f0f
        page = BackgroundPage()
        page.image_color_button.color = '#f0f'

        # WHEN: The property is accessed
        result = page.image_color

        # THEN: The result should be correct
        assert result == '#f0f'

    def test_set_image_color(self):
        """
        Test the image_color setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.image_color = '#0f0'

        # THEN: The result should be correct
        assert page.image_color_button.color == '#0f0'

    def test_get_image_path(self):
        """
        Test the image_path getter
        """
        # GIVEN: A BackgroundPage instance with the image_path edit set to a path
        page = BackgroundPage()
        page.image_path_edit.path = Path('.')

        # WHEN: The property is accessed
        result = page.image_path

        # THEN: The result should be correct
        assert result == Path('.')

    def test_set_image_path(self):
        """
        Test the image_path setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.image_path = Path('openlp')

        # THEN: The result should be correct
        assert page.image_path_edit.path == Path('openlp')

    def test_get_video_color(self):
        """
        Test the video_color getter
        """
        # GIVEN: A BackgroundPage instance with the video_color button set to #f0f
        page = BackgroundPage()
        page.video_color_button.color = '#f0f'

        # WHEN: The property is accessed
        result = page.video_color

        # THEN: The result should be correct
        assert result == '#f0f'

    def test_set_video_color(self):
        """
        Test the video_color setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.video_color = '#0f0'

        # THEN: The result should be correct
        assert page.video_color_button.color == '#0f0'

    def test_get_video_path(self):
        """
        Test the video_path getter
        """
        # GIVEN: A BackgroundPage instance with the video_path edit set to a path
        page = BackgroundPage()
        page.video_path_edit.path = Path('.')

        # WHEN: The property is accessed
        result = page.video_path

        # THEN: The result should be correct
        assert result == Path('.')

    def test_set_video_path(self):
        """
        Test the video_path setter
        """
        # GIVEN: A BackgroundPage instance
        page = BackgroundPage()

        # WHEN: The property is set
        page.video_path = Path('openlp')

        # THEN: The result should be correct
        assert page.video_path_edit.path == Path('openlp')
