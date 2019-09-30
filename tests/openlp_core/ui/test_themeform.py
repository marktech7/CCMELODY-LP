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
Interface tests to test the ThemeWizard class and related methods.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from openlp.core.common.registry import Registry
from openlp.core.ui.themeform import ThemeForm
from tests.helpers.testmixin import TestMixin


class TestThemeManager(TestCase, TestMixin):
    """
    Test the functions in the ThemeManager module
    """
    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        mocked_renderer = MagicMock()
        Registry().register('renderer', mocked_renderer)

    @patch('openlp.core.display.window.QtWidgets.QVBoxLayout')
    def test_create_theme_wizard(self, mocked_qvboxlayout):
        """
        Test creating a ThemeForm instance
        """
        # GIVEN: A ThemeForm class
        # WHEN: An object is created
        # THEN: There should be no problems
        ThemeForm(None)
