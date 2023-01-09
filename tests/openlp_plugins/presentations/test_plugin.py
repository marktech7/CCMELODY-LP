# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2023 OpenLP Developers                              #
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
This module contains tests for the plugin class Presentation plugin.
"""
from openlp.plugins.presentations.presentationplugin import PresentationPlugin


def test_plugin_about():
    result = PresentationPlugin.about()

    assert result == (
        '<strong>Presentation '
        'Plugin</strong><br />The presentation plugin provides the '
        'ability to show presentations using a number of different '
        'programs. The choice of available presentation programs is '
        'available to the user in a drop down box.'
    )
