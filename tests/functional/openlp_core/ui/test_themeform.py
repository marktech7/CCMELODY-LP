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
Package to test the openlp.core.ui.themeform package.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.ui.themeform import ThemeForm


class TestThemeManager(TestCase):
    """
    Test the functions in the ThemeManager Class
    """
    def setUp(self):
        with patch('openlp.core.ui.themeform.ThemeForm._setup'):
            self.instance = ThemeForm(None)

    def test_on_image_path_edit_path_changed(self):
        """
        Test the `image_path_edit.pathChanged` handler
        """
        # GIVEN: An instance of Theme Form
        with patch.object(self.instance, 'set_background_page_values') as mocked_set_background_page_values:
            self.instance.theme = MagicMock()

            # WHEN: `on_image_path_edit_path_changed` is clicked
            self.instance.on_image_path_edit_path_changed(Path('/', 'new', 'pat.h'))

            # THEN: The theme background file should be set and `set_background_page_values` should have been called
            assert self.instance.theme.background_filename == Path('/', 'new', 'pat.h')
            mocked_set_background_page_values.assert_called_once_with()
