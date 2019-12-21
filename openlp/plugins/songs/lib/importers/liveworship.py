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
The :mod:`liveworship` module provides the functionality for importing
a LiveWorship database into the OpenLP database.
"""
import os
import logging
import ctypes

from lxml import etree
from pathlib import Path
from tempfile import gettempdir

from openlp.core.common import is_win, is_linux, is_macosx, is_64bit_instance, delete_file
from openlp.core.common.i18n import translate
from openlp.core.lib.ui import critical_error_message_box
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
    LiveWorship Valentina Database.

    The approach is to use the Valentina DB ADK for C via ctypes to dump the database content to a XML
    file that is then analysed for data extraction. It would also be possible to skip the XML and
    extract the data directly from the database using ctypes, but that approach requires a lot of ctypes
    interaction and type conversion that is rather fragile across platforms and versions, so the XML approach
    is used for now.
    It was implemented using Valentina DB ADK for C version 9.6.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the LiveWorship importer.
        """
        self.root = None
        super(LiveWorshipImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a path to a LiveWorship (valentina) DB.
        """
        self.dump_file = Path(gettempdir()) / 'openlp-liveworship-dump.xml'
        if not self.dump_valentina_to_xml():
            return
        self.load_xml_dump()
        if self.root is None:
            return
        self.extract_songs()
        delete_file(self.dump_file)

    def dump_valentina_to_xml(self):
        """
        Load the LiveWorship database using the Valentina DB ADK for C and dump the DB content to a XML file.
        """
        self.import_wizard.increment_progress_bar(translate('SongsPlugin.LiveWorshipImport',
                                                            'Extracting data from database'), 0)
        # Based on OS and bitness, try to load the dll
        libVCSDK = None
        if is_win():
            # The DLL path must be set depending on the bitness of the OpenLP/Python instance
            if is_64bit_instance():
                vcdk_install_folder = 'VCDK_x64_{adkver}'
                dll_name = '/vcsdk_release_x64.dll'
            else:
                vcdk_install_folder = 'VCDK_{adkver}'
                dll_name = '/vcsdk_release_x86.dll'
            dll_path = '{pf}\\Paradigma Software\\{vcdk}'.format(pf=os.getenv('PROGRAMFILES'), vcdk=vcdk_install_folder)
            dll_path2 = '{pf}\\Paradigma Software\\vcomponents_win_vc'.format(pf=os.getenv('PROGRAMFILES'))
            os.environ['PATH'] = ';'.join([os.environ['PATH'], dll_path, dll_path2])
            libVCSDK_path = dll_path + dll_name
        elif is_linux():
            libVCSDK_path = '/opt/VCSDK/libVCSDK.so'
        elif is_macosx():
            # The DLL path must be set depending on the bitness of the OpenLP/Python instance
            if is_64bit_instance():
                vcdk_install_folder = 'VCDK_x64_{adkver}'
                dll_name = '/vcsdk_x64.dylib'
            else:
                vcdk_install_folder = 'VCDK_{adkver}'
                dll_name = '/vcsdk_x86.dylib'
            libVCSDK_path = '/Users/Shared/Paradigma Software/{folder}/{dll}'.format(folder=vcdk_install_folder,
                                                                                     dll=dll_name)
        # Try to make this somewhat future proof by trying versions 9 to 15
        found_dll = False
        if '{adkver}' in libVCSDK_path:
            for i in range(9, 16):
                if os.path.exists(libVCSDK_path.format(adkver=i)):
                    found_dll = True
                    libVCSDK_path = libVCSDK_path.format(adkver=i)
                    break
            if not found_dll:
                libVCSDK_path = libVCSDK_path.format(adkver=9)
        elif os.path.exists(libVCSDK_path):
            found_dll = True
        if not found_dll:
            adk_name = "Valentina DB ADK for C, {bitness} bit"
            if is_64bit_instance():
                adk_name = adk_name.format(bitness=64)
            else:
                adk_name = adk_name.format(bitness=32)
            critical_error_message_box(translate('SongsPlugin.LiveWorshipImport',
                                                 'Could not find Valentina DB ADK libraries '),
                                       translate('SongsPlugin.LiveWorshipImport',
                                                 'Could not find "{dllpath}", please install "{adk}"'
                                                 .format(dllpath=libVCSDK_path, adk=adk_name)))
            return False
        libVCSDK = ctypes.CDLL(libVCSDK_path)
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
        # Dump the database to XML
        libVCSDK.Database_Dump(database_ptr, ctypes.c_char_p(str(self.dump_file).encode()), EVDumpType_kXML,
                               EVDataKind_kStructureAndRecords, pretty_print, ctypes.c_char_p(b'utf-8'))
        # Close the DB
        libVCSDK.Database_Close(database_ptr)
        # Shutdown Valentina
        libVCSDK.Valentina_Shutdown()
        return True

    def load_xml_dump(self):
        self.import_wizard.increment_progress_bar(translate('SongsPlugin.LiveWorshipImport',
                                                            'Loading the extracting data'), 0)
        # The file can contain the EOT control character and certain invalid tags with missing attributewhich
        # will make lxml fail, so it must be removed.
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
        xpath = "//BaseObjectData[@Name='SlideCol']/Record/f[@n='Type' and normalize-space(text())='song']/.."
        song_records = self.root.xpath(xpath)
        # Song count for progress bar
        song_count = len(song_records)
        # set progress bar to songcount
        self.import_wizard.progress_bar.setMaximum(song_count)
        for record in song_records:
            if self.stop_import_flag:
                break
            # reset to default values
            self.set_defaults()
            # Get song metadata
            title = record.xpath("f[@n='Title']/text()")
            song_rowid = record.xpath("f[@n='_rowid']/text()")
            if title and song_rowid:
                self.title = self.clean_string(title[0])
                song_rowid = self.clean_string(song_rowid[0])
            else:
                # if no title or no rowid we skip the song
                continue
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

    def extract_tags(self, song_id):
        """
        Extract the tags for a particular song
        """
        xpath = "//BaseObjectData[@Name='TagGroup']/Record/f[@n='SlideCol_rowid' "\
                "and normalize-space(text())='{rowid}']/.."
        tag_group_records = self.root.xpath(xpath.format(rowid=song_id))
        for record in tag_group_records:
            tag_rowid = record.xpath("f[@n='Tag_rowid']/text()")
            if tag_rowid:
                tag_rowid = self.clean_string(tag_rowid[0])
                xpath = "//BaseObjectData[@Name='Tag']/Record/f[@n='_rowid' and normalize-space(text())='{rowid}']/"\
                        "../f[@n='Description']/text()"
                tag = self.root.xpath(xpath.format(rowid=tag_rowid))
                if tag:
                    tag = self.clean_string(tag[0])
                    self.topics.append(tag)

    def extract_verses(self, song_id):
        """
        Extract the verses for a particular song
        """
        xpath = "//BaseObjectData[@Name='SlideColSlides']/Record/f[@n='SlideCol_rowid' and "\
                "normalize-space(text())='{rowid}']/.."
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
