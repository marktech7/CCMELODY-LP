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
This module contains tests for the EasySlides song importer.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'easyslides'


class TestEasySlidesFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'EasySlidesImport'
        self.importer_module_name = 'easyslides'
        super(TestEasySlidesFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an EasySlides file works correctly on various files
        """
        self.file_import(TEST_PATH / 'amazing-grace.xml',
                         self.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
        self.file_import(TEST_PATH / 'Export_2017-01-12_BB.xml',
                         self.load_external_result_data(TEST_PATH / 'Export_2017-01-12_BB.json'))
