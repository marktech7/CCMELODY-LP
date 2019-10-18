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
The theme regeneration progress dialog
"""
from PyQt5 import QtWidgets

from openlp.core.display.screens import ScreenList
from openlp.core.ui.themeprogressdialog import UiThemeProgressDialog
from openlp.core.common.mixins import RegistryProperties


class ThemeProgressForm(QtWidgets.QDialog, UiThemeProgressDialog, RegistryProperties):
    """
    The theme regeneration progress dialog
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui(self)
        self._theme_list = []
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        try:
            screens = ScreenList()
            self.ratio = screens.current.display_geometry.width() / screens.current.display_geometry.height()
        except ZeroDivisionError:
            self.ratio = 16 / 9
        self.theme_preview_layout.aspect_ratio = self.ratio

    def get_preview(self, theme_name, theme_data):
        self.label.setText(theme_name)
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.theme_display.set_scale(float(self.theme_display.width()) / self.renderer.width())
        return self.theme_display.generate_preview(theme_data, generate_screenshot=True)

    def _get_theme_list(self):
        """Property getter"""
        return self._theme_list

    def _set_theme_list(self, value):
        """Property setter"""
        self._theme_list = value
        self.progress_bar.setMaximum(len(self._theme_list))

    theme_list = property(_get_theme_list, _set_theme_list)
