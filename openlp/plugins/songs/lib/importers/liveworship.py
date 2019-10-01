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
The :mod:`liveworship` module provides the functionality for importing
a LiveWorship database into the OpenLP database.
"""
import os
import logging
import ctypes

from lxml import etree
from pathlib import Path
from tempfile import gettempdir

from openlp.core.common import is_win, is_linux, is_macosx
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings

# Copied from  VCSDK_Enums.h
EVStorageType_kDisk = 1
EVDumpType_kSQL = 1
EVDumpType_kXML = 2
EVDataKind_kStructureAndRecords = 2
EVDataKind_kRecordsOnly = 3

pretty_print = 1

log = logging.getLogger(__name__)


class LiveWorshipImport(SongImport):
    """
    The :class:`LiveWorshipImport` class provides the ability to import the
    LiveWorship Valentina Database
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the MediaShout importer.
        """
        self.root = None
        super(LiveWorshipImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a path to a LiveWorship (valentina) DB.
        """
        self.dump_file = Path(gettempdir()) / 'openlp-liveworship-dump.xml'
        self.dump_valentina_to_xml()
        if not self.root:
            return
        self.load_xml_dump()
        self.extract_songs()

    def dump_valentina_to_xml(self):
        """
        Load the LiveWorship database using the Valentina DB ADK for C and dump the DB content to a XML file.
        """
        libVCSDK = None
        if is_win():
            dll_path = 'c:\\Program Files\\Paradigma Software\\VCDK_x64_9'
            dll_path2 = 'c:\\Program Files\\Paradigma Software\\vcomponents_win_vc'
            os.environ['PATH'] = ';'.join([os.environ['PATH'], dll_path, dll_path2])
            libVCSDK = ctypes.CDLL(dll_path + '/vcsdk_release_x64.dll')
        elif is_linux():
            libVCSDK = ctypes.CDLL('/opt/VCSDK/libVCSDK.so')
        elif is_macosx():
            libVCSDK = ctypes.CDLL('/Users/Shared/Paradigma Software/VCSDK_x64_9/vcsdk_x64.dylib')
        # cache size set to 1024, got no idea what this means...
        # serial numbers set to None - only 10 minutes access, should be enough :)
        libVCSDK.Valentina_Init(1024, None, None, None)
        # Create a DB instance
        Database_New = libVCSDK.Database_New
        Database_New.argtypes = [ctypes.c_int]
        Database_New.restype = ctypes.c_void_p
        database = Database_New(EVStorageType_kDisk)
        database_ptr = ctypes.c_void_p(database)
        # Load the file into our instance
        libVCSDK.Database_Open(database_ptr, ctypes.c_char_p(str(self.import_source).encode()))
        # Some debug printing
        # is_open = libVCSDK.Database_IsOpen(database_ptr)
        # print('is open: %d' % is_open)
        # For some reason python/valentina crashes if the code below is executed
        # encoding = libVCSDK.Database_GetStorageEncoding(database_ptr);
        # print('encoding: %s' % ctypes.c_char_p(encoding).value)
        # table_count = libVCSDK.Database_GetTableCount(database_ptr)
        # print('table count: %d' % table_count)
        # name = libVCSDK.Database_GetName(database_ptr)
        # print('name: %s' % ctypes.c_char_p(name).value)

        # Dump the database to XML
        libVCSDK.Database_Dump(database_ptr, ctypes.c_char_p(str(self.dump_file).encode()), EVDumpType_kXML,
                               EVDataKind_kStructureAndRecords, pretty_print, ctypes.c_char_p(b'utf-8'))
        # Close the DB
        libVCSDK.Database_Close(database_ptr)
        # Shutdown Valentina
        libVCSDK.Valentina_Shutdown()

    def load_xml_dump(self):
        # The file can contain the EOT control character which will make lxml fail, so it must be removed.
        xml_file = open(self.dump_file, 'rt')
        xml_content = xml_file.read()
        xml_file.close()
        xml_content = xml_content.replace('\4', '**EOT**').replace('CustomProperty =""', 'CustomProperty a=""', 1)
        # Now load the XML
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        try:
            self.root = etree.fromstring(xml_content, parser)
        except etree.XMLSyntaxError:
            self.log_error(self.dump_file, SongStrings.XMLSyntaxError)
            log.exception('XML syntax error in file {path}'.format(path=str(self.dump_file)))

    def extract_songs(self):
        """
        Extract all the songs from the XML object
        """
        # Find song records
        song_records = self.root.xpath("//BaseObjectData[@Name='SlideCol']/Record/f[@n='Type' and text()='song']/..")
        # Song count for progress bar
        song_count = len(song_records)
        # set progress bar to songcount
        self.import_wizard.progress_bar.setMaximum(song_count)
        for record in song_records:
            # reset to default values
            self.set_defaults()
            # Get song metadata
            title = record.xpath("f[@n='Title']/text()")
            song_rowid = record.xpath("f[@n='_rowid']/text()")
            if title and song_rowid:
                self.title = self.clean_string(title[0])
                song_rowid = song_rowid[0]
            else:
                # if no title or no rowid we skip the song
                continue
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=self.title))
            authors_line = record.xpath("f[@n='Author']/text()")
            if authors_line:
                self.extract_authors(authors_line[0])
            cpr = record.xpath("f[@n='Copyright']/text()")
            if cpr:
                self.add_copyright(self.clean_string(cpr[0]))
            ccli = record.xpath("f[@n='CCLI']/text()")
            if ccli:
                self.ccli = self.clean_string(ccli[0])
            # Get song tags
            self.extract_tags(song_rowid)
            # Get song verses
            self.extract_verses(song_rowid)
            if not self.finish():
                self.log_error(self.title)

    def extract_tags(self, row_id):
        """
        Extract the tags for a particular song
        """
        xpath = "//BaseObjectData[@Name='TagGroup']/Record/f[@n='SlideCol_rowid' and text()='{rowid}']/.."
        tag_group_records = self.root.xpath(xpath.format(rowid=row_id))
        for record in tag_group_records:
            tag_rowid = record.xpath("f[@n='Tag_rowid']/text()")
            if tag_rowid:
                tag_rowid = self.clean_string(tag_rowid[0])
                xpath = "//BaseObjectData[@Name='Tag']/Record/f[@n='SlideCol_rowid' and text()='{rowid}']/../"\
                        "f[@n='Description']/text()"
                tag = self.root.xpath(xpath.format(rowid=tag_rowid))
                if tag:
                    tag = self.clean_string(tag[0])
                    # TODO: find a way to import tags

    def extract_verses(self, song_id):
        """
        Extract the verses for a particular song
        """
        xpath = "//BaseObjectData[@Name='SlideColSlides']/Record/f[@n='SlideCol_rowid' and text()='{rowid}']/.."
        slides_records = self.root.xpath(xpath.format(rowid=song_id))
        for record in slides_records:
            verse_text = record.xpath("f[@n='kText']/text()")
            if verse_text:
                verse_text = self.clean_verse(verse_text[0])
                verse_tag = record.xpath("f[@n='Description']/text()")
                if verse_tag:
                    verse_tag = self.convert_verse_name(verse_tag[0])
                else:
                    verse_tag = 'v'
                self.add_verse(verse_text, verse_tag)

    def extract_authors(self, authors_line):
        """
        Extract the authors as a list of str from the authors record
        """
        if not authors_line:
            return
        for author_name in authors_line.split('/'):
            name_parts = [self.clean_string(part) for part in author_name.split(',')][::-1]
            self.parse_author(' '.join(name_parts))

    def clean_string(self, string):
        """
        Clean up the strings
        """
        # &#x09; is tab
        return string.replace('^`^', '\'').replace('/', '-').replace('&#x09;', ' ').strip()

    def clean_verse(self, verse_line):
        """
        Extract the verse lines from the verse record
        """
        # &#x0D; is carriage return
        return self.clean_string(verse_line.replace('&#x0D;', '\n'))

    def convert_verse_name(self, verse_name):
        """
        Convert the Verse # to v#
        """
        name_parts = verse_name.lower().split()
        if len(name_parts) > 1:
            return name_parts[0][0] + name_parts[1]
        else:
            return name_parts[0][0]
