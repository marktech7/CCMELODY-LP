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
Package to test the openlp.core.ui.media package.
"""
import pytest

from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.ui import DisplayControllerType
from openlp.core.ui.media.mediacontroller import MediaController
from openlp.core.ui.media import ItemMediaInfo

from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'media'
TEST_MEDIA = [['avi_file.avi', 61495], ['mp3_file.mp3', 134426], ['mpg_file.mpg', 9404], ['mp4_file.mp4', 188336]]


@pytest.yield_fixture
def media_env(registry):
    """Local test setup"""
    Registry().register('service_manager', MagicMock())
    media_controller = MediaController()
    yield media_controller


def test_resize(media_env):
    """
    Test that the resize method is called correctly
    """
    # GIVEN: A media controller, a player and a display
    mocked_player = MagicMock()
    mocked_display = MagicMock()

    # WHEN: resize() is called
    media_env.media_controller.resize(mocked_display, mocked_player)

    # THEN: The player's resize method should be called correctly
    mocked_player.resize.assert_called_with(mocked_display)


def test_check_file_type_null(media_env):
    """
    Test that we don't try to play media when no players available
    """
    # GIVEN: A mocked UiStrings, get_used_players, controller, display and service_item
    mocked_controller = MagicMock()
    mocked_display = MagicMock()
    media_env.media_controller.media_players = MagicMock()

    # WHEN: calling _check_file_type when no players exists
    ret = media_env.media_controller._check_file_type(mocked_controller, mocked_display)

    # THEN: it should return False
    assert ret is False, '_check_file_type should return False when no media file matches.'


def test_check_file_video(media_env):
    """
    Test that we process a file that is valid
    """
    # GIVEN: A mocked UiStrings, get_used_players, controller, display and service_item
    mocked_controller = MagicMock()
    mocked_display = MagicMock()
    media_env.media_controller.media_players = MagicMock()
    mocked_controller.media_info = ItemMediaInfo()
    mocked_controller.media_info.file_info = [TEST_PATH / 'mp3_file.mp3']
    media_env.media_controller.current_media_players = {}
    media_env.media_controller.vlc_player = MagicMock()

    # WHEN: calling _check_file_type when no players exists
    ret = media_env.media_controller._check_file_type(mocked_controller, mocked_display)

    # THEN: it should return False
    assert ret is True, '_check_file_type should return True when audio file is present and matches.'


def test_check_file_audio(media_env):
    """
    Test that we process a file that is valid
    """
    # GIVEN: A mocked UiStrings, get_used_players, controller, display and service_item
    mocked_controller = MagicMock()
    mocked_display = MagicMock()
    media_env.media_controller.media_players = MagicMock()
    mocked_controller.media_info = ItemMediaInfo()
    mocked_controller.media_info.file_info = [TEST_PATH / 'mp4_file.mp4']
    media_env.media_controller.current_media_players = {}
    media_env.media_controller.vlc_player = MagicMock()

    # WHEN: calling _check_file_type when no players exists
    ret = media_env.media_controller._check_file_type(mocked_controller, mocked_display)

    # THEN: it should return False
    assert ret is True, '_check_file_type should return True when media file is present and matches.'


def test_media_play_msg(media_env):
    """
    Test that the media controller responds to the request to play a loaded video
    """
    # GIVEN: A media controller and a message with two elements
    message = (1, 2)

    # WHEN: media_play_msg() is called
    with patch.object(media_env.media_controller, u'media_play') as mocked_media_play:
        media_env.media_controller.media_play_msg(message, False)

    # THEN: The underlying method is called
    mocked_media_play.assert_called_with(1, False)


def test_media_pause_msg(media_env):
    """
    Test that the media controller responds to the request to pause a loaded video
    """
    # GIVEN: A media controller and a message with two elements
    message = (1, 2)

    # WHEN: media_play_msg() is called
    with patch.object(media_env.media_controller, u'media_pause') as mocked_media_pause:
        media_env.media_controller.media_pause_msg(message)

    # THEN: The underlying method is called
    mocked_media_pause.assert_called_with(1)


def test_media_stop_msg(media_env):
    """
    Test that the media controller responds to the request to stop a loaded video
    """
    # GIVEN: A media controller and a message with two elements
    message = (1, 2)

    # WHEN: media_play_msg() is called
    with patch.object(media_env.media_controller, u'media_stop') as mocked_media_stop:
        media_env.media_controller.media_stop_msg(message)

    # THEN: The underlying method is called
    mocked_media_stop.assert_called_with(1)


def test_media_volume_msg(media_env):
    """
    Test that the media controller responds to the request to change the volume
    """
    # GIVEN: A media controller and a message with two elements
    message = (1, [50])

    # WHEN: media_play_msg() is called
    with patch.object(media_env.media_controller, u'media_volume') as mocked_media_volume:
        media_env.media_controller.media_volume_msg(message)

    # THEN: The underlying method is called
    mocked_media_volume.assert_called_with(1, 50)


def test_media_seek_msg(media_env):
    """
    Test that the media controller responds to the request to seek to a particular position
    """
    # GIVEN: A media controller and a message with two elements
    message = (1, [800])

    # WHEN: media_play_msg() is called
    with patch.object(media_env.media_controller, u'media_seek') as mocked_media_seek:
        media_env.media_controller.media_seek_msg(message)

    # THEN: The underlying method is called
    mocked_media_seek.assert_called_with(1, 800)


def test_media_length(media_env):
    """
    Test the Media Info basic functionality
    """
    for test_data in TEST_MEDIA:
        # GIVEN: a media file
        full_path = str(TEST_PATH / test_data[0])

        # WHEN the media data is retrieved
        results = media_env.media_controller.media_length(full_path)

        # THEN you can determine the run time
        assert results == test_data[1], 'The correct duration is returned for ' + test_data[0]


def test_on_media_play(media_env):
    """
    Test the on_media_play method
    """
    # GIVEN: A mocked live controller and a mocked media_play() method
    mocked_live_controller = MagicMock()
    Registry().register('live_controller', mocked_live_controller)
    media_env.media_controller.media_play = MagicMock()

    # WHEN: the on_media_play() method is called
    media_env.media_controller.on_media_play()

    # The mocked live controller should be called
    media_env.media_controller.media_play.assert_called_once_with(mocked_live_controller, False)


def test_on_media_pause(media_env):
    """
    Test the on_media_pause method
    """
    # GIVEN: A mocked live controller and a mocked media_pause() method
    mocked_live_controller = MagicMock()
    Registry().register('live_controller', mocked_live_controller)
    media_env.media_controller.media_pause = MagicMock()

    # WHEN: the on_media_pause() method is called
    media_env.media_controller.on_media_pause()

    # The mocked live controller should be called
    media_env.media_controller.media_pause.assert_called_once_with(mocked_live_controller)


def test_on_media_stop(media_env):
    """
    Test the on_media_stop method
    """
    # GIVEN: A mocked live controller and a mocked media_stop() method
    mocked_live_controller = MagicMock()
    Registry().register('live_controller', mocked_live_controller)
    media_env.media_controller.media_stop = MagicMock()

    # WHEN: the on_media_stop() method is called
    media_env.media_controller.on_media_stop()

    # The mocked live controller should be called
    media_env.media_controller.media_stop.assert_called_once_with(mocked_live_controller)


def test_display_controllers_live(media_env):
    """
    Test that the display_controllers() method returns the live controller when requested
    """
    # GIVEN: A mocked live controller
    mocked_live_controller = MagicMock()
    mocked_preview_controller = MagicMock()
    Registry().register('live_controller', mocked_live_controller)
    Registry().register('preview_controller', mocked_preview_controller)

    # WHEN: display_controllers() is called with DisplayControllerType.Live
    controller = media_env.media_controller.display_controllers(DisplayControllerType.Live)

    # THEN: the controller should be the live controller
    assert controller is mocked_live_controller


def test_display_controllers_preview(media_env):
    """
    Test that the display_controllers() method returns the preview controller when requested
    """
    # GIVEN: A mocked live controller
    mocked_live_controller = MagicMock()
    mocked_preview_controller = MagicMock()
    Registry().register('live_controller', mocked_live_controller)
    Registry().register('preview_controller', mocked_preview_controller)

    # WHEN: display_controllers() is called with DisplayControllerType.Preview
    controller = media_env.media_controller.display_controllers(DisplayControllerType.Preview)

    # THEN: the controller should be the live controller
    assert controller is mocked_preview_controller


def test_set_controls_visible(media_env):
    """
    Test that "set_controls_visible" sets the media controls on the controller to be visible or not
    """
    # GIVEN: A mocked controller
    mocked_controller = MagicMock()

    # WHEN: Set to visible
    MediaController.set_controls_visible(mocked_controller, True)

    # THEN: The media controls should have been set to visible
    mocked_controller.mediabar.setVisible.assert_called_once_with(True)


@patch('openlp.core.ui.media.mediacontroller.ItemMediaInfo')
def test_setup_display(MockItemMediaInfo, media_env):
    """
    Test that the display/controllers are set up correctly
    """
    # GIVEN: A media controller object and some mocks
    mocked_media_info = MagicMock()
    MockItemMediaInfo.return_value = mocked_media_info
    media_env.media_controller.vlc_player = MagicMock()
    mocked_display = MagicMock()
    media_env.media_controller._define_display = MagicMock(return_value=mocked_display)
    media_env.media_controller.vlc_player = MagicMock()
    controller = MagicMock()

    # WHEN: setup_display() is called
    media_env.media_controller.setup_display(controller, True)

    # THEN: The right calls should have been made
    assert controller.media_info == mocked_media_info
    assert controller.has_audio is False
    media_env.media_controller._define_display.assert_called_once_with(controller)
    media_env.media_controller.vlc_player.setup(controller, mocked_display, False)
