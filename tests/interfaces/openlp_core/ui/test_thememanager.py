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
Interface tests to test the themeManager class and related methods.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlp.core.common.settings import Settings
from openlp.core.ui.thememanager import ThemeManager


@pytest.fixture()
def theme_manager(settings):
    thm = ThemeManager()
    return thm


def test_theme_manager_initialise(theme_manager):
    """
    Test the thememanager initialise - basic test
    """
    # GIVEN: A new a call to initialise
    theme_manager.setup_ui = MagicMock()
    theme_manager.build_theme_path = MagicMock()
    Settings().setValue('themes/global theme', 'my_theme')

    # WHEN: the initialisation is run
    theme_manager.bootstrap_initialise()

    # THEN:
    theme_manager.setup_ui.assert_called_once_with(theme_manager)
    assert theme_manager.global_theme == 'my_theme'
    theme_manager.build_theme_path.assert_called_once_with()


@patch('openlp.core.ui.thememanager.create_paths')
@patch('openlp.core.ui.thememanager.AppLocation.get_section_data_path')
def test_build_theme_path(mocked_get_section_data_path, mocked_create_paths, theme_manager):
    """
    Test the thememanager build_theme_path
    """
    # GIVEN: A mocked out AppLocation.get_directory() and mocked create_paths
    mocked_get_section_data_path.return_value = Path('tests/my_theme')

    # WHEN: the build_theme_path is run
    theme_manager.build_theme_path()

    #  THEN: The theme path and the thumb path should be correct
    assert theme_manager.theme_path == Path('tests/my_theme')
    assert theme_manager.thumb_path == Path('tests/my_theme/thumbnails')
    mocked_create_paths.assert_called_once_with(Path('tests/my_theme'), Path('tests/my_theme/thumbnails'))


def test_click_on_new_theme(theme_manager):
    """
    Test the on_add_theme event handler is called by the UI
    """
    # GIVEN: An initial form
    Settings().setValue('themes/global theme', 'my_theme')
    mocked_event = MagicMock()
    theme_manager.on_add_theme = mocked_event
    theme_manager.setup_ui(theme_manager)

    # WHEN displaying the UI and pressing cancel
    new_theme = theme_manager.toolbar.actions['newTheme']
    new_theme.trigger()

    assert mocked_event.call_count == 1, 'The on_add_theme method should have been called once'


@patch('openlp.core.ui.themeform.ThemeForm._setup')
@patch('openlp.core.ui.filerenameform.FileRenameForm._setup')
def test_bootstrap_post(mocked_rename_form, mocked_theme_form, theme_manager):
    """
    Test the functions of bootstrap_post_setup are called.
    """
    # GIVEN:
    theme_manager.theme_path = MagicMock()

    # WHEN:
    with patch('openlp.core.ui.thememanager.ThemeProgressForm'):
        theme_manager.bootstrap_post_set_up()

    # THEN:
    assert theme_manager.progress_form is not None
    assert theme_manager.theme_form is not None
    assert theme_manager.file_rename_form is not None


def test_bootstrap_completion(theme_manager):
    """
    Test the functions of bootstrap_post_setup are called.
    """
    # GIVEN:
    theme_manager.load_themes = MagicMock()
    theme_manager.upgrade_themes = MagicMock()

    # WHEN:
    theme_manager.bootstrap_completion()

    # THEN:
    theme_manager.upgrade_themes.assert_called_once()
    theme_manager.load_themes.assert_called_once()
