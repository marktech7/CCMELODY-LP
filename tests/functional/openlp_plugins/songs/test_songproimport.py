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
The :mod:`songproimport` module provides the functionality for importing
SongPro song files into the current installation database.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'songpro'


def test_song_pro(mock_settings):

    class TestSongProFileImport(SongImportTestHelper):

        def __init__(self, *args, **kwargs):
            self.importer_class_name = 'SongProImport'
            self.importer_module_name = 'songpro'
            super(TestSongProFileImport, self).__init__(*args, **kwargs)

        def test_song_import(self):
            """
            Test that loading an SongPro file works correctly
            """
            self.file_import(TEST_PATH / 'amazing-grace.txt',
                             self.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))

    test_file_import = TestSongProFileImport()
    test_file_import.setUp()
    test_file_import.test_song_import()
    test_file_import.tearDown()
