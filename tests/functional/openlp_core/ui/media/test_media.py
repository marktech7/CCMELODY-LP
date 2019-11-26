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
from openlp.core.ui.media import parse_optical_path


def test_parse_optical_path_linux():
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


def test_parse_optical_path_win():
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
