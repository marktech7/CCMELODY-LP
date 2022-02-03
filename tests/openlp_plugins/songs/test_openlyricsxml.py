# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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
This module contains tests for the OpenLyrics song importer.
"""
import json
from unittest.mock import MagicMock, patch

from lxml import etree, objectify

from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics, SongXML
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'openlyrics'
START_TAGS = [{"protected": False, "desc": "z", "start tag": "{z}", "end html": "</strong>", "temporary": False,
               "end tag": "{/z}", "start html": "strong>"}]
RESULT_TAGS = [{"temporary": False, "protected": False, "desc": "z", "start tag": "{z}", "start html": "strong>",
                "end html": "</strong>", "end tag": "{/z}"},
               {"temporary": False, "end tag": "{/c}", "desc": "c", "start tag": "{c}",
                "start html": "<span class=\"chord\" style=\"display:none\"><strong>", "end html": "</strong></span>",
                "protected": False}]
AUTHOR_XML = '<properties>\
                  <authors>\
                      <author type="words">Test Author1</author>\
                      <author type="music">Test Author1</author>\
                      <author type="words">Test Author2</author>\
                  </authors>\
            </properties>'
SONGBOOK_XML = '<properties>\
                    <songbooks>\
                        <songbook name="Collection 1" entry="48"/>\
                        <songbook name="Collection 2" entry="445 A"/>\
                    </songbooks>\
                </properties>'


def test_songxml_get_verses_invalid_xml():
    """Test that invalid XML for a song is ignored"""
    # GIVEN: Invalid XML and a SongXML object
    invalid_xml = 'this is not xml'
    song_xml = SongXML()

    # WHEN: get_verses is called with invalid XML
    result = song_xml.get_verses(invalid_xml)

    # THEN: An empty list is returned
    assert result == []


def test_process_formatting_tags(settings):
    """
    Test that _process_formatting_tags works
    """
    # GIVEN: A OpenLyric XML with formatting tags and a mocked out manager
    mocked_manager = MagicMock()
    settings.setValue('formattingTags/html_tags', json.dumps(START_TAGS))
    ol = OpenLyrics(mocked_manager)
    parser = etree.XMLParser(remove_blank_text=True)
    parsed_file = etree.parse((TEST_PATH / 'duchu-tags.xml').open('rb'), parser)
    xml = etree.tostring(parsed_file).decode()
    song_xml = objectify.fromstring(xml)

    # WHEN: processing the formatting tags
    ol._process_formatting_tags(song_xml, False)

    # THEN: New tags should have been saved
    assert json.loads(json.dumps(RESULT_TAGS)) == json.loads(str(settings.value('formattingTags/html_tags'))), \
        'The formatting tags should contain both the old and the new'


def test_process_author(registry, settings):
    """
    Test that _process_authors works
    """
    # GIVEN: A OpenLyric XML with authors and a mocked out manager
    with patch('openlp.plugins.songs.lib.openlyricsxml.Author'):
        mocked_manager = MagicMock()
        mocked_manager.get_object_filtered.return_value = None
        ol = OpenLyrics(mocked_manager)
        properties_xml = objectify.fromstring(AUTHOR_XML)
        mocked_song = MagicMock()

        # WHEN: processing the author xml
        ol._process_authors(properties_xml, mocked_song)

        # THEN: add_author should have been called twice
        assert mocked_song.method_calls[0][1][1] == 'words+music'
        assert mocked_song.method_calls[1][1][1] == 'words'


def test_process_songbooks(registry, settings):
    """
    Test that _process_songbooks works
    """
    # GIVEN: A OpenLyric XML with songbooks and a mocked out manager
    with patch('openlp.plugins.songs.lib.openlyricsxml.Book'):
        mocked_manager = MagicMock()
        mocked_manager.get_object_filtered.return_value = None
        ol = OpenLyrics(mocked_manager)
        properties_xml = objectify.fromstring(SONGBOOK_XML)
        mocked_song = MagicMock()

        # WHEN: processing the songbook xml
        ol._process_songbooks(properties_xml, mocked_song)

        # THEN: add_songbook_entry should have been called twice
        assert mocked_song.method_calls[0][1][1] == '48'
        assert mocked_song.method_calls[1][1][1] == '445 A'
