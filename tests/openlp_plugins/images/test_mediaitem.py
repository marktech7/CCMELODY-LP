# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2023 OpenLP Developers                              #
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
This module contains tests for the lib submodule of the Images plugin.
"""
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.common.enum import ImageThemeMode
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.plugins.images.lib.mediaitem import ImageMediaItem


@pytest.fixture
def media_item(mock_settings):
    """Local test setup"""
    mocked_main_window = MagicMock()
    Registry().register('service_list', MagicMock())
    Registry().register('main_window', mocked_main_window)
    Registry().register('live_controller', MagicMock())
    mocked_plugin = MagicMock()
    with patch('openlp.plugins.images.lib.mediaitem.FolderLibraryItem._setup'), \
            patch('openlp.plugins.images.lib.mediaitem.ImageMediaItem.setup_item'):
        m_item = ImageMediaItem(None, mocked_plugin)
        m_item.settings_section = 'images'
        m_item.list_view = MagicMock()
    return m_item


def test_on_reset_click(media_item):
    """
    Test that on_reset_click() actually resets the background
    """
    # GIVEN: A mocked version of reset_action
    media_item.reset_action = MagicMock()
    media_item.reset_action_context = MagicMock()

    # WHEN: on_reset_click is called
    media_item.on_reset_click()

    # THEN: the reset_action should be set invisible, and the image should be reset
    media_item.reset_action.setVisible.assert_called_with(False)
    media_item.reset_action_context.setVisible.assert_called_with(False)
    media_item.live_controller.reload_theme.assert_called_with()


def test_on_display_changed(media_item):
    """
    Test that on_display_changed() hides the reset background button
    """
    # GIVEN: A mocked version of reset_action
    media_item.reset_action = MagicMock()
    media_item.reset_action_context = MagicMock()

    # WHEN: on_display_changed is called
    media_item.on_display_changed()

    # THEN: the reset_action should be set invisible
    media_item.reset_action.setVisible.assert_called_with(False)
    media_item.reset_action_context.setVisible.assert_called_with(False)


def test_generate_slide_data_default_theme(media_item):
    """
    Test that the generated service item provides the corect theme
    """
    # GIVEN: A mocked service item and settings
    mocked_service_item = MagicMock()
    media_item.list_view = MagicMock()
    Registry().get('settings').value.side_effect = [ImageThemeMode.Black]

    # WHEN: generate_slide_data is called
    media_item.generate_slide_data(mocked_service_item)

    # THEN: The service item should force the theme, and use the default theme
    mocked_service_item.add_capability.assert_any_call(ItemCapabilities.ProvidesOwnTheme)
    assert mocked_service_item.theme == -1


def test_generate_slide_data_custom_theme(media_item):
    """
    Test that the generated service item provides the corect theme
    """
    # GIVEN: A mocked service item and settings
    mocked_service_item = MagicMock()
    media_item.list_view = MagicMock()
    Registry().get('settings').value.side_effect = [ImageThemeMode.CustomTheme, 'theme_name']

    # WHEN: generate_slide_data is called
    media_item.generate_slide_data(mocked_service_item)

    # THEN: The service item should force the theme, and use the theme in the settings
    mocked_service_item.add_capability.assert_any_call(ItemCapabilities.ProvidesOwnTheme)
    assert mocked_service_item.theme == 'theme_name'


@patch('openlp.plugins.images.lib.mediaitem.check_item_selected')
@patch('openlp.plugins.images.lib.mediaitem.isinstance')
@patch('openlp.plugins.images.lib.mediaitem.Path.exists')
def test_on_replace_click(mocked_exists, mocked_isinstance, mocked_check_item_selected, media_item):
    """
    Test that on_replace_click() actually sets the background
    """
    # GIVEN: A mocked version of reset_action, and a (faked) existing selected image file
    media_item.reset_action = MagicMock()
    media_item.reset_action_context = MagicMock()
    media_item.list_view = MagicMock()
    mocked_check_item_selected.return_value = True
    mocked_isinstance.return_value = True
    mocked_exists.return_value = True

    # WHEN: on_replace_click is called
    media_item.on_replace_click()

    # THEN: the reset_action should be set visible, and the image should be set
    media_item.reset_action.setVisible.assert_called_with(True)
    media_item.reset_action_context.setVisible.assert_called_with(True)
    media_item.live_controller.set_background_image.assert_called_with(ANY)


def test_generate_thumbnail_path_hash(media_item):
    """
    Test that the thumbnail path is correctly generated with the file hash
    """
    # GIVEN: A media item and an Image object
    mocked_image = MagicMock(file_path=Path('myimage.jpg'), file_hash='c3986a0bd8e1ec9da406df142950c67e7d435410')
    media_item.service_path = Path('.')

    # WHEN: generate_thumbnail_path() is called
    result = media_item.generate_thumbnail_path(mocked_image)

    # THEN: The path should be correct
    assert result == Path('.') / 'c3986a0bd8e1ec9da406df142950c67e7d435410.jpg'


def test_generate_thumbnail_path_filename(media_item):
    """
    Test that the thumbnail path is correctly generated with the file name
    """
    # GIVEN: A media item and an Image object
    mocked_image = MagicMock(file_path=Path('myimage.jpg'), file_hash=None)
    media_item.service_path = Path('.')

    # WHEN: generate_thumbnail_path() is called
    result = media_item.generate_thumbnail_path(mocked_image)

    # THEN: The path should be correct
    assert result == Path('.') / 'myimage.jpg'
