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

import logging

import ctypes
from lxml import objectify
from lxml.etree import Error, LxmlError
from tempfile import gettempdir

from openlp.core.common import is_win, is_linux, is_osx
from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport

# Copied from  VCSDK_Enums.h
EVStorageType_kDisk = 1
EVDumpType_kSQL = 1
EVDumpType_kXML = 2
EVDataKind_kStructureAndRecords = 2
EVDataKind_kRecordsOnly = 3

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
        super(LiveWorshipImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a path to a LiveWorship (valentina) DB.
        """
        self.dump_file = Path(gettempdir()) / 'openlp' / 'liveworship-dump.xml'

        self.dump_valentina_to_xml()

        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        try:
            tree = etree.parse(str(self.dump_file), parser)
        except etree.XMLSyntaxError:
            self.log_error(file_path, SongStrings.XMLSyntaxError)
            log.exception('XML syntax error in file {path}'.format(path=file_path))

        root = tree.getroot()

        # TODO: convert this from json parsing to XML parsing
        songs = extract_songs(json_data)
        for song in songs:
            if song['Type'] != 'song':
                continue
            verses = extract_verses(json_data, song['_rowid'])

        self.import_wizard.progress_bar.setMaximum(len(self.import_source))

    def dump_valentina_to_xml(self):
        libVCSDK = None
        if is_win():
            dll_path = 'c:\\Program Files\\Paradigma Software\\VCDK_x64_9'
            dll_path2 = 'c:\\Program Files\\Paradigma Software\\vcomponents_win_vc'
            os.environ['PATH'] = ';'.join([os.environ['PATH'], dll_path, dll_path2])
            libVCSDK = ctypes.CDLL(dll_path + '/vcsdk_release_x64.dll')
        elif is_linux():
            libVCSDK = ctypes.CDLL('/opt/VCSDK/libVCSDK.so')
        elif is_osx():
            # TODO: find path on macOS
            libVCSDK = ctypes.CDLL('/opt/VCSDK/libVCSDK.so')

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
        is_open = libVCSDK.Database_IsOpen(database_ptr)
        print('is open: %d' % is_open)
        
        # For some reason python/valentina crashes if the code below is executed
        #encoding = libVCSDK.Database_GetStorageEncoding(database_ptr);
        #print('encoding: %s' % ctypes.c_char_p(encoding).value)
        #table_count = libVCSDK.Database_GetTableCount(database_ptr)
        #print('table count: %d' % table_count)
        #name = libVCSDK.Database_GetName(database_ptr)
        #print('name: %s' % ctypes.c_char_p(name).value)
        
        # Dump the database to XML
        libVCSDK.Database_Dump(database_ptr, ctypes.c_char_p(str(self.dump_file).encode()), EVDumpType_kXML,
                               EVDataKind_kStructureAndRecords, pretty_print, ctypes.c_char_p(b'utf-8'))
        # Close the DB
        libVCSDK.Database_Close(database_ptr)
        # Shutdown Valentina
        libVCSDK.Valentina_Shutdown()

    def extract_songs(json_data):
        """
        Extract all the songs from the JSON object
        """
        songs = []
        for table in json_data:
            if table['name'] != 'SlideCol':
                continue
            songs.extend(table['records'])
        return songs

    def extract_verses(json_data, song_id):
        """
        Extract the verses for a particular song
        """
        verses = []
        for table in json_data:
            if table['name'] != 'SlideColSlides':
                continue
            for verse in table['records']:
                if verse['SlideCol_rowid'] == song_id:
                    verses.append(verse)
        return verses

    def extract_authors(authors_line):
        """
        Extract the authors as a list of str from the authors record
        """
        if not authors_line:
            return ['Author Unknown']
        authors = []
        for author_name in authors_line.split('/'):
            name_parts = [part.strip() for part in author_name.split(',')][::-1]
            authors.append(' '.join(name_parts))
        return authors

    def clean_string(string):
        """
        Clean up the strings
        """
        return string.replace('^`^', '\'').replace('/', '-')

    def extract_verse(verse_line):
        """
        Extract the verse lines from the verse record
        """
        return verse_line.replace('\r', '\n').replace('^`^', '\'')

    def convert_verse_name(verse_name):
        """
        Convert the Verse # to v#
        """
        name_parts = verse_name.lower().split()
        if len(name_parts) > 1:
            return name_parts[0][0] + name_parts[1]
        else:
            return name_parts[0][0]
