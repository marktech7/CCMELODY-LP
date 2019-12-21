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
The :mod:`powerpraiseimport` module provides the functionality for importing
Powerpraise song files into the current database.
"""
from lxml import objectify

from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport


class PowerPraiseImport(SongImport):
    """
    The :class:`PowerpraiseImport` class provides OpenLP with the
    ability to import Powerpraise song files.
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=file_path.name))
            with file_path.open('rb') as xml_file:
                root = objectify.parse(xml_file).getroot()
                self.process_song(root)

    def process_song(self, root):
        self.set_defaults()
        self.title = str(root.general.title)
        verse_order_list = []
        verse_count = {}
        for item in root.order.item:
            verse_order_list.append(str(item))
        for part in root.songtext.part:
            original_verse_def = part.get('caption')
            # There are some predefined verse defitions in PowerPraise, try to parse these
            if original_verse_def.startswith("Strophe") or original_verse_def.startswith("Teil"):
                verse_def = 'v'
            elif original_verse_def.startswith("Refrain"):
                verse_def = 'c'
            elif original_verse_def.startswith("Bridge"):
                verse_def = 'b'
            elif original_verse_def.startswith("Schluss"):
                verse_def = 'e'
            else:
                verse_def = 'o'
            verse_count[verse_def] = verse_count.get(verse_def, 0) + 1
            verse_def = '{verse}{count:d}'.format(verse=verse_def, count=verse_count[verse_def])
            verse_text = []
            for slide in part.slide:
                if not hasattr(slide, 'line'):
                    continue  # No content
                for line in slide.line:
                    verse_text.append(str(line))
            self.add_verse('\n'.join(verse_text), verse_def)
            # Update verse name in verse order list
            for i in range(len(verse_order_list)):
                if verse_order_list[i].lower() == original_verse_def.lower():
                    verse_order_list[i] = verse_def

        self.verse_order_list = verse_order_list
        if not self.finish():
            self.log_error(self.import_source)
