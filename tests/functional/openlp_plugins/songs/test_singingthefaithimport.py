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
This module contains tests for the SingingTheFaith song importer.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'singingthefaith'


class TestSingingTheFaithFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'SingingTheFaithImport'
        self.importer_module_name = 'singingthefaith'
        super(TestSingingTheFaithFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading a Singing The Faith file works correctly on various files
        """
        # Note that the previous tests without hints no longer apply as there is always a
        # hints file, which contains the hints for the real Singing The Faith Songs.
        # Unhinted songs here must be numbered above any real Singing The Faith Song
        # Single verse
        self.file_import([TEST_PATH / 'H901.txt'],
                         self.load_external_result_data(TEST_PATH / 'STF901.json'))
        # Whole song
        self.file_import([TEST_PATH / 'H902.txt'],
                         self.load_external_result_data(TEST_PATH / 'STF902.json'))

        # Tests with hints - note that the hints directory has a hints.tag which specifies
        # SongbookNumberInTitle: True
        # The default is false, so the unhinted tests will not have the title, but the hinted
        # song tests will need it

        # Single verse
        self.file_import([TEST_PATH / 'hints' / 'H1.txt'],
                         self.load_external_result_data(TEST_PATH / 'hints' / 'STF001.json'))
        # Whole song
        self.file_import([TEST_PATH / 'hints' / 'H2.txt'],
                         self.load_external_result_data(TEST_PATH / 'hints' / 'STF002.json'))
