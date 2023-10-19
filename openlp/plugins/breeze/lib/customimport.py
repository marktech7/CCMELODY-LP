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
The :mod:`~openlp.plugins.breeze.lib.customimport` module provides
a function that imports a single custom slide into the database and returns
the database ID of the slide.  This mimics the implementation for SongPlugin
that was used to import songs from Planning Center.
"""

from openlp.core.common.registry import Registry
from openlp.plugins.custom.lib.customxmlhandler import CustomXML
from openlp.plugins.custom.lib.db import CustomSlide


class BreezeCustomImport(object):
    """
    Creates a custom slide and returns the database ID of that slide

    :param item_title: The text to put on the slide.
    :param html_details: The "details" element from PCO, with html formatting
    :param theme_name:  The theme_name to use for the slide.
    """
    def add_slide(self, segment, theme_name):
        sxml = CustomXML()
        sxml.add_verse_to_lyrics('custom', str(1), segment["content"])
        custom_slide = CustomSlide(title="General", text=str(sxml.extract_xml(), 'utf-8'), credits='pco',
                                   theme_name=theme_name)
        custom = Registry().get('custom')
        custom_db_manager = custom.plugin.db_manager
        custom_db_manager.save_object(custom_slide)
        return custom_slide.id
