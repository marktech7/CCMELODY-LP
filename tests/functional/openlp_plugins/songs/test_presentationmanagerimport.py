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
This module contains tests for the PresentationManager song importer.
"""
from unittest import skipIf

from openlp.core.common import is_macosx
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'presentationmanager'


def test_presenter_manager(mock_settings):

    class TestPresentationManagerFileImport(SongImportTestHelper):

        def __init__(self, *args, **kwargs):
            self.importer_class_name = 'PresentationManagerImport'
            self.importer_module_name = 'presentationmanager'
            super(TestPresentationManagerFileImport, self).__init__(*args, **kwargs)

        @skipIf(is_macosx(), 'This test fails for an undetermined reason on macOS')
        def test_song_import(self):
            """
            Test that loading a PresentationManager file works correctly
            """
            self.file_import([TEST_PATH / 'Great Is Thy Faithfulness.sng'],
                             self.load_external_result_data(TEST_PATH / 'Great Is Thy Faithfulness.json'))
            self.file_import([TEST_PATH / 'Amazing Grace.sng'],
                             self.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))

    test_file_import = TestPresentationManagerFileImport()
    test_file_import.setUp()
    test_file_import.test_song_import()
    test_file_import.tearDown()
