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
Functional tests to test the Bible Manager class and related methods.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.enum import LanguageSelection
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.bibles.lib.manager import BibleManager
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestBibleManager(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the environment for testing bible queries with 1 Timothy 3
        """
        self.setup_application()
        self.build_settings()
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('application', MagicMock())
        with patch('openlp.core.common.applocation.AppLocation.get_section_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.AppLocation.get_files') as mocked_get_files:
            # GIVEN: A mocked out Settings class and a mocked out AppLocation.get_files()
            mocked_class = MagicMock()
            Registry().register('settings', Settings())
            mocked_settings = mocked_class.return_value
            mocked_settings.contains.return_value = False
            mocked_get_files.return_value = ["tests.sqlite"]
            mocked_get_data_path.return_value = TEST_RESOURCES_PATH + "/bibles"
            self.manager = BibleManager(MagicMock())

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.manager
        self.destroy_settings()

    def test_get_books(self):
        """
        Test the get_books method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the books of the bible
        books = self.manager.get_books('tests')
        # THEN a list of books should be returned
        assert 66 == len(books), 'There should be 66 books in the bible'

    def test_get_book_by_id(self):
        """
        Test the get_book_by_id method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the book of the bible
        book = self.manager.get_book_by_id('tests', 54)
        # THEN a book should be returned
        assert '1 Timothy' == book.name, '1 Timothy should have been returned from the bible'

    def test_get_chapter_count(self):
        """
        Test the get_chapter_count method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the chapters in a book of the bible
        book = self.manager.get_book_by_id('tests', 54)
        chapter = self.manager.get_chapter_count('tests', book)
        # THEN the chapter count should be returned
        assert 6 == chapter, '1 Timothy should have 6 chapters returned from the bible'

    def test_get_verse_count_by_book_ref_id(self):
        """
        Test the get_verse_count_by_book_ref_id method
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking for the number of verses in a book of the bible
        verses = self.manager.get_verse_count_by_book_ref_id('tests', 54, 3)
        # THEN the chapter count should be returned
        assert 16 == verses, '1 Timothy v3 should have 16 verses returned from the bible'
