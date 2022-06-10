# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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
The :mod:`~openlp.core.pages.background` module contains the background page used in the theme wizard
"""
from openlp.core.pages import GridLayoutPage
from openlp.core.themes.editor_widgets import WidgetProxy
from openlp.core.themes.editor_widgets.background import BackgroundWidget


class BackgroundPage(GridLayoutPage, WidgetProxy):
    """
    A background selection widget
    """
    def __init__(self, parent=None):
        GridLayoutPage.__init__(self, parent)

    def create_widgets(self):
        return BackgroundWidget(self, self._layout)
