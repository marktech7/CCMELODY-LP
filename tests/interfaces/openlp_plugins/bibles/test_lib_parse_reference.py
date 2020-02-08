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
This module contains tests for the lib submodule of the Bibles plugin.
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.bibles.lib import parse_reference
from openlp.plugins.bibles.lib.manager import BibleManager
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


class TestBibleManager(TestCase, TestMixin):

    def setUp(self):
        """
        Set up the environment for testing bible parse reference
        """
        self.setup_application()
        self.build_settings()
        Registry.create()
        Registry().register('service_list', MagicMock())
        Registry().register('application', MagicMock())
        with patch('openlp.core.common.applocation.AppLocation.get_section_data_path') as mocked_get_data_path, \
                patch('openlp.core.common.applocation.AppLocation.get_files') as mocked_get_files:
            Registry().register('settings', Settings())
            mocked_get_files.return_value = ["tests.sqlite"]
            mocked_get_data_path.return_value = TEST_RESOURCES_PATH + "/bibles"
            self.manager = BibleManager(MagicMock())

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.manager
        self.destroy_settings()

    def test_parse_reference_numbered_book_single_chapter_no_verse_reference(self):
        """
        Test the parse_reference method with 1 Timothy 1
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a one tuple verse array should be returned
        assert [(54, 1, 1, -1)] == results, "The bible verses should match the expected results"

    def test_parse_reference_numbered_book_single_range_single_chapter_multiple_verses(self):
        """
        Test the parse_reference method with 1 Timothy 1:1-2
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:1-2', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a one tuple verse array should be returned
        assert [(54, 1, 1, 2)] == results, "The bible verses should match the expected results"

    def test_parse_reference_numbered_book_single_range_multiple_chapters_specific_verses(self):
        """
        Test the parse_reference method with 1 Timothy 1:1-2
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:1-2:1', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a two tuple verse array should be returned
        assert [(54, 1, 1, -1), (54, 2, 1, 1)] == results, \
            "The bible verses should match the expected results"

    def test_parse_reference_invalid_book(self):
        """
        Test the parse_reference method with non existent book
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('Raoul 1', self.manager.db_cache['tests'], MagicMock())
        # THEN an empty verse array should be returned
        assert [] == results, "The bible search should return an empty list"

    def test_parse_reference_numbered_book_single_range_single_chapter_with_end_reference(self):
        """
        Test the parse_reference method with 1 Timothy 1:3-end
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference
        results = parse_reference('1 Timothy 1:3-end', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a one tuple verse array should be returned
        assert [(54, 1, 3, -1)] == results, "The bible verses should match the expected results"

    def test_parse_reference_numbered_book_single_range_single_chapter_with_end_reference_no_bible_ref_id(self):
        """
        Test the parse_reference method with 1 Timothy 1:3-end without a bible ref id to match
        how the GUI does the search.  This is logged in issue #282
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference in Language 0 (english)
        results = parse_reference('1 Timothy 1:3-end', self.manager.db_cache['tests'], 0)
        # THEN a one tuple verse array should be returned
        assert [(54, 1, 3, -1)] == results, "The bible verses should match the expected results"

    def test_parse_reference_book_ref_id_invalid(self):
        """
        Test the parse_reference method with 1 Timothy 1:1 with an invalid bible ref id
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference with an invalid bible reference id
        results = parse_reference('1 Timothy 1:1', self.manager.db_cache['tests'], MagicMock(), -666)
        # THEN an empty verse array should be returned
        assert [] == results, "The bible verse list should be empty"

    def test_parse_reference_no_from_chapter_in_second_range(self):
        """
        Test the parse_reference method with 1 Timothy 1:1,3
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference that has no from_chapter in the second range
        results = parse_reference('1 Timothy 1:1,3', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a two tuple verse array should be returned
        assert [(54, 1, 1, 1), (54, 1, 3, 3)] == results, "The bible verses should match the expected results"

    def test_parse_reference_to_chapter_less_than_from_chapter(self):
        """
        Test the parse_reference method with 1 Timothy 2:1-1:1
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference with a to_chapter less than the from_chapter
        results = parse_reference('1 Timothy 2:1-1:1', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN an empty verse array should be returned
        assert [] == results, "The bible verse list should be empty"

    def test_parse_reference_no_from_chapter_specified(self):
        """
        Test the parse_reference method with 1 Timothy :1-2
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference with no from_chapter specified
        results = parse_reference('1 Timothy :1-2', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a two tuple verse array should be returned with the bible verse references treated as chapter references
        assert [(54, 1, 1, -1), (54, 2, 1, -1)] == results, "The bible verses should match the expected results"

    def test_parse_reference_three_chapters(self):
        """
        Test the parse_reference method with 1 Timothy 1-3
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference with three chapters
        results = parse_reference('1 Timothy 1-3', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN a three tuple verse array should be returned
        assert [(54, 1, 1, -1), (54, 2, 1, -1), (54, 3, 1, -1)] == results, \
            "The bible verses should match the expected results"

    def test_parse_reference_non_regexp_matching_reference(self):
        """
        Test the parse_reference method with 1 Timothy
        """
        # GIVEN given a bible in the bible manager
        # WHEN asking to parse the bible reference that fails the regexp matching
        results = parse_reference('1 Timothy', self.manager.db_cache['tests'], MagicMock(), 54)
        # THEN an empty verse array should be returned
        assert [] == results, "The bible verse list should be empty"
