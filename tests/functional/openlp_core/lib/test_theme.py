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
Package to test the openlp.core.lib.theme package.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.lib.theme import BackgroundType, Theme


class TestBackgroundType(TestCase):
    """
    Test the BackgroundType enum methods.
    """
    def test_solid_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Solid

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'solid'

    def test_gradient_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Gradient

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'gradient'

    def test_image_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Image

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'image'

    def test_transparent_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Transparent

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'transparent'

    def test_video_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Video

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'video'

    def test_stream_to_string(self):
        """
        Test the to_string method of :class:`BackgroundType`
        """
        # GIVEN: A BackgroundType member
        background_type = BackgroundType.Stream

        # WHEN: Calling BackgroundType.to_string
        # THEN: The string equivalent should have been returned
        assert BackgroundType.to_string(background_type) == 'stream'


class TestTheme(TestCase):
    """
    Test the Theme class
    """
    def test_new_theme(self):
        """
        Test the Theme constructor
        """
        # GIVEN: The Theme class
        # WHEN: A theme object is created
        default_theme = Theme()

        # THEN: The default values should be correct
        self.check_theme(default_theme)

    def test_expand_json(self):
        """
        Test the expand_json method
        """
        # GIVEN: A Theme object and some JSON to "expand"
        theme = Theme()
        theme_json = {
            'background': {
                'border_color': '#000000',
                'type': 'solid'
            },
            'display': {
                'vertical_align': 0
            },
            'font': {
                'footer': {
                    'bold': False
                },
                'main': {
                    'name': 'Arial'
                }
            }
        }

        # WHEN: Theme.expand_json() is run
        theme.expand_json(theme_json)

        # THEN: The attributes should be set on the object
        self.check_theme(theme)

    def test_extend_image_filename(self):
        """
        Test the extend_image_filename method
        """
        # GIVEN: A theme object
        theme = Theme()
        theme.theme_name = 'MyBeautifulTheme'
        theme.background_filename = Path('video.mp4')
        theme.background_type = 'video'
        path = Path.home()

        # WHEN: Theme.extend_image_filename is run
        theme.extend_image_filename(path)

        # THEN: The filename of the background should be correct
        expected_filename = path / 'MyBeautifulTheme' / 'video.mp4'
        assert expected_filename == theme.background_filename
        assert 'MyBeautifulTheme' == theme.theme_name

    def test_save_retrieve(self):
        """
        Load a dummy theme, save it and reload it
        """
        # GIVEN: The default Theme class
        # WHEN: A theme object is created
        default_theme = Theme()
        # THEN: The default values should be correct
        save_theme_json = default_theme.export_theme()
        lt = Theme()
        lt.load_theme(save_theme_json)
        self.check_theme(lt)

    @patch('openlp.core.display.screens.ScreenList.current')
    def test_set_default_footer(self, mock_geometry):
        """
        Test the set_default_footer function sets the footer back to default
        (reletive to the screen)
        """
        # GIVEN: A screen geometry object and a Theme footer with a strange area
        mock_geometry.display_geometry = MagicMock()
        mock_geometry.display_geometry.height.return_value = 600
        mock_geometry.display_geometry.width.return_value = 400
        theme = Theme()
        theme.font_main_x = 20
        theme.font_footer_x = 207
        theme.font_footer_y = 25
        theme.font_footer_width = 4253
        theme.font_footer_height = 5423

        # WHEN: set_default_footer is called
        theme.set_default_footer()

        # THEN: footer should be set, header should not have changed
        assert theme.font_main_x == 20, 'header should not have been changed'
        assert theme.font_footer_x == 10, 'x pos should be reset to default of 10'
        assert theme.font_footer_y == 540, 'y pos should be reset to (screen_size_height * 9 / 10)'
        assert theme.font_footer_width == 380, 'width should have been reset to (screen_size_width - 20)'
        assert theme.font_footer_height == 60, 'height should have been reset to (screen_size_height / 10)'

    @patch('openlp.core.display.screens.ScreenList.current')
    def test_set_default_header(self, mock_geometry):
        """
        Test the set_default_header function sets the header back to default
        (reletive to the screen)
        """
        # GIVEN: A screen geometry object and a Theme header with a strange area
        mock_geometry.display_geometry = MagicMock()
        mock_geometry.display_geometry.height.return_value = 600
        mock_geometry.display_geometry.width.return_value = 400
        theme = Theme()
        theme.font_footer_x = 200
        theme.font_main_x = 687
        theme.font_main_y = 546
        theme.font_main_width = 345
        theme.font_main_height = 653

        # WHEN: set_default_header is called
        theme.set_default_header()

        # THEN: footer should be set, header should not have changed
        assert theme.font_footer_x == 200, 'footer should not have been changed'
        assert theme.font_main_x == 10, 'x pos should be reset to default of 10'
        assert theme.font_main_y == 0, 'y pos should be reset to 0'
        assert theme.font_main_width == 380, 'width should have been reset to (screen_size_width - 20)'
        assert theme.font_main_height == 540, 'height should have been reset to (screen_size_height * 9 / 10)'

    @patch('openlp.core.display.screens.ScreenList.current')
    def test_set_default_header_footer(self, mock_geometry):
        """
        Test the set_default_header_footer function sets the header and footer back to default
        (reletive to the screen)
        """
        # GIVEN: A screen geometry object and a Theme header with a strange area
        mock_geometry.display_geometry = MagicMock()
        theme = Theme()
        theme.font_footer_x = 200
        theme.font_main_x = 687

        # WHEN: set_default_header is called
        theme.set_default_header_footer()

        # THEN: footer should be set, header should not have changed
        assert theme.font_footer_x == 10, 'footer x pos should be reset to default of 10'
        assert theme.font_main_x == 10, 'header x pos should be reset to default of 10'

    def check_theme(self, theme):
        assert '#000000' == theme.background_border_color, 'background_border_color should be "#000000"'
        assert 'solid' == theme.background_type, 'background_type should be "solid"'
        assert 0 == theme.display_vertical_align, 'display_vertical_align should be 0'
        assert theme.font_footer_bold is False, 'font_footer_bold should be False'
        assert 'Arial' == theme.font_main_name, 'font_main_name should be "Arial"'
        assert 48 == len(theme.__dict__), 'The theme should have 48 attributes'
