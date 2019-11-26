# -*- coding: utf-8 -*-

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
Package to test the openlp.core.ui package.
"""
from unittest import TestCase, skip
from unittest.mock import patch

from PyQt5 import QtCore

from openlp.core.ui.media import parse_optical_path
from openlp.core.ui.media import format_milliseconds
from tests.helpers.testmixin import TestMixin


class TestMedia(TestCase, TestMixin):

    @skip
    def test_get_media_players_no_config(self):
        """
        Test that when there's no config, get_media_players() returns an empty list of players (not a string)
        """
        def value_results(key):
            if key == 'media/players':
                return ''
            else:
                return False

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = 'vlc'

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            assert [] == used_players, 'Used players should be an empty list'
            assert '' == overridden_player, 'Overridden player should be an empty string'

    @skip
    def test_get_media_players_no_players(self):
        """
        Test that when there's no players but overridden player is set, get_media_players() returns 'auto'
        """
        def value_results(key):
            if key == 'media/override player':
                return QtCore.Qt.Checked
            else:
                return ''

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players, overridden_player = 'vlc'

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            assert [] == used_players, 'Used players should be an empty list'
            assert 'auto' == overridden_player, 'Overridden player should be "auto"'

    @skip
    def test_get_media_players_with_valid_list(self):
        """
        Test that when get_media_players() is called the string list is interpreted correctly
        """
        def value_results(key):
            if key == 'media/players':
                return '[vlc]'
            else:
                return False

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players = 'vlc'

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            assert ['vlc', 'webkit', 'system'] == used_players, 'Used players should be correct'

    @skip
    def test_get_media_players_with_overridden_player(self):
        """
        Test that when get_media_players() is called the overridden player is correctly set
        """
        def value_results(key):
            if key == 'media/players':
                return '[vlc]'
            else:
                return QtCore.Qt.Checked

        # GIVEN: A mocked out Settings() object
        with patch('openlp.core.ui.media.Settings.value') as mocked_value:
            mocked_value.side_effect = value_results

            # WHEN: get_media_players() is called
            used_players = 'vlc'

            # THEN: the used_players should be an empty list, and the overridden player should be an empty string
            assert ['vlc'] == used_players, 'Used players should be correct'

    def test_parse_optical_path_linux(self):
        """
        Test that test_parse_optical_path() parses a optical path with linux device path correctly
        """

        # GIVEN: An optical formatted path
        org_title_track = 1
        org_audio_track = 2
        org_subtitle_track = -1
        org_start = 1234
        org_end = 4321
        org_name = 'test name'
        org_device_path = '/dev/dvd'
        path = 'optical:%d:%d:%d:%d:%d:%s:%s' % (org_title_track, org_audio_track, org_subtitle_track,
                                                 org_start, org_end, org_name, org_device_path)

        # WHEN: parsing the path
        (device_path, title_track, audio_track, subtitle_track, start, end, name) = parse_optical_path(path)

        # THEN: The return values should match the original values
        assert org_title_track == int(title_track), 'Returned title_track should match the original'
        assert org_audio_track == audio_track, 'Returned audio_track should match the original'
        assert org_subtitle_track == int(subtitle_track), 'Returned subtitle_track should match the original'
        assert org_start == start, 'Returned start should match the original'
        assert org_end == end, 'Returned end should match the original'
        assert org_name == name, 'Returned end should match the original'
        assert org_device_path == device_path, 'Returned device_path should match the original'

    def test_parse_optical_path_win(self):
        """
        Test that test_parse_optical_path() parses a optical path with windows device path correctly
        """

        # GIVEN: An optical formatted path
        org_title_track = 1
        org_audio_track = 2
        org_subtitle_track = -1
        org_start = 1234
        org_end = 4321
        org_name = 'test name'
        org_device_path = 'D:'
        path = 'optical:%d:%d:%d:%d:%d:%s:%s' % (org_title_track, org_audio_track, org_subtitle_track,
                                                 org_start, org_end, org_name, org_device_path)

        # WHEN: parsing the path
        (device_path, title_track, audio_track, subtitle_track, start, end, name) = parse_optical_path(path)

        # THEN: The return values should match the original values
        assert org_title_track == int(title_track), 'Returned title_track should match the original'
        assert org_audio_track == audio_track, 'Returned audio_track should match the original'
        assert org_subtitle_track == int(subtitle_track), 'Returned subtitle_track should match the original'
        assert org_start == start, 'Returned start should match the original'
        assert org_end == end, 'Returned end should match the original'
        assert org_name == name, 'Returned end should match the original'
        assert org_device_path == device_path, 'Returned device_path should match the original'

    def test_format_milliseconds(self):
        """
        Test that format_milliseconds(...) makes an expected human readable time string
        """

        # GIVEN: 200 million milliseconds (Revelation 9:16)
        num_soldiers_on_horses_as_milliseconds = 200 * 1000 * 1000

        # WHEN: converting milliseconds to human readable string
        num_soldiers_on_horses_as_formatted_time_string = format_milliseconds(num_soldiers_on_horses_as_milliseconds)

        # THEN: The formatted time string should be 55 hours, 33 minutes, 20 seconds, and 000 milliseconds
        assert num_soldiers_on_horses_as_formatted_time_string == "55:33:20,000"
