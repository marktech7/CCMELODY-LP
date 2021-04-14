# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
Test the media plugin
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.plugins.media.lib.mediaitem import MediaMediaItem


@pytest.fixture
def media_item(settings):
    """Local test setup"""
    mocked_main_window = MagicMock()
    Registry().register('service_list', MagicMock())
    Registry().register('main_window', mocked_main_window)
    Registry().register('live_controller', MagicMock())
    mocked_plugin = MagicMock()
    with patch('openlp.plugins.media.lib.mediaitem.MediaManagerItem._setup'), \
            patch('openlp.plugins.media.lib.mediaitem.MediaMediaItem.setup_item'):
        m_item = MediaMediaItem(None, mocked_plugin)
    return m_item


def test_search_found(media_item):
    """
    Media Remote Search Successful find
    """
    # GIVEN: The Mediaitem set up a list of media
    media_item.settings.setValue('media/media files', [Path('test.mp3'), Path('test.mp4')])
    # WHEN: Retrieving the test file
    result = media_item.search('test.mp4', False)
    # THEN: a file should be found
    assert result == [['test.mp4', 'test.mp4']], 'The result file contain the file name'


def test_search_found_mixed(media_item):
    """
    Media Remote Search Successful find with Paths and Strings
    """
    # GIVEN: The Mediaitem set up a list of media
    media_item.settings.setValue('media/media files', [Path('test.mp3'), 'test.mp4'])
    # WHEN: Retrieving the test file
    result = media_item.search('test.mp4', False)
    # THEN: a file should be found
    assert result == [['test.mp4', 'test.mp4']], 'The result file contain the file name'


def test_search_not_found(media_item):
    """
    Media Remote Search not find
    """
    # GIVEN: The Mediaitem set up a list of media
    media_item.settings.setValue('media/media files', [Path('test.mp3'), Path('test.mp4')])
    # WHEN: Retrieving the test file
    result = media_item.search('test.mpx', False)
    # THEN: a file should be found
    assert result == [], 'The result file should be empty'
