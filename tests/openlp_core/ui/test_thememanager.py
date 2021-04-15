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
Package to test the openlp.core.ui.thememanager package.
"""
import os
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import ANY, Mock, MagicMock, patch, call, sentinel

from PyQt5 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.ui.thememanager import ThemeManager
from tests.utils.constants import RESOURCE_PATH


@patch('openlp.core.ui.thememanager.zipfile.ZipFile.__init__')
@patch('openlp.core.ui.thememanager.zipfile.ZipFile.write')
def test_export_theme(mocked_zipfile_write, mocked_zipfile_init, registry):
    """
    Test exporting a theme .
    """
    # GIVEN: A new ThemeManager instance.
    theme_manager = ThemeManager()
    theme_manager.theme_path = RESOURCE_PATH / 'themes'
    mocked_zipfile_init.return_value = None

    # WHEN: The theme is exported
    theme_manager._export_theme(Path('some', 'path', 'Default.otz'), 'Default')

    # THEN: The zipfile should be created at the given path
    mocked_zipfile_init.assert_called_with(Path('some', 'path', 'Default.otz'), 'w')
    mocked_zipfile_write.assert_called_with(RESOURCE_PATH / 'themes' / 'Default' / 'Default.xml',
                                            Path('Default', 'Default.xml'))


def test_initial_theme_manager(registry):
    """
    Test the instantiation of theme manager.
    """
    # GIVEN: A new service manager instance.
    ThemeManager(None)

    # WHEN: the default theme manager is built.
    # THEN: The the controller should be registered in the registry.
    assert Registry().get('theme_manager') is not None, 'The base theme manager should be registered'


@patch('openlp.core.ui.thememanager.Theme')
def test_get_global_theme(mocked_theme, registry):
    """
    Test the global theme method returns the theme data for the global theme
    """
    # GIVEN: A service manager instance and the global theme
    theme_manager = ThemeManager(None)
    theme_manager.global_theme = 'global theme name'
    theme_manager._theme_list = {'global theme name': sentinel.global_theme}

    # WHEN: Calling get_global_theme
    result = theme_manager.get_global_theme()

    # THEN: Returned global theme
    assert result == sentinel.global_theme


@patch('openlp.core.ui.thememanager.Theme')
def test_get_theme_data(mocked_theme, registry):
    """
    Test that the get theme data method returns the requested theme data
    """
    # GIVEN: A service manager instance and themes
    theme_manager = ThemeManager(None)
    theme_manager._theme_list = {'theme1': sentinel.theme1, 'theme2': sentinel.theme2}

    # WHEN: Get theme data is called with 'theme2'
    result = theme_manager.get_theme_data('theme2')

    # THEN: Should return theme2's data
    assert result == sentinel.theme2


@patch('openlp.core.ui.thememanager.Theme')
def test_get_theme_data_missing(mocked_theme, registry):
    """
    Test that the get theme data method returns the default theme when theme name not found
    """
    # GIVEN: A service manager instance and themes
    theme_manager = ThemeManager(None)
    theme_manager._theme_list = {'theme1': sentinel.theme1, 'theme2': sentinel.theme2}
    mocked_theme.return_value = sentinel.default_theme

    # WHEN: Get theme data is called with None
    result = theme_manager.get_theme_data(None)

    # THEN: Should return default theme's data
    assert result == sentinel.default_theme


@patch('openlp.core.ui.thememanager.shutil')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_same_image(mocked_create_paths, mocked_shutil, registry):
    """
    Test that we don't try to overwrite a theme background image with itself
    """
    # GIVEN: A new theme manager instance, with mocked builtins.open, copyfile,
    #        theme, create_paths, thememanager-attributes and background
    #       .filename path is the same as the source path.
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = None
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.extract_formatted_xml = MagicMock()
    mocked_theme.extract_formatted_xml.return_value = 'fake_theme_xml'.encode()
    file_path_1 = RESOURCE_PATH / 'church.jpg'
    mocked_theme.background_filename = file_path_1
    mocked_theme.background_source = file_path_1

    # WHEN: Calling save_theme with both background paths to the same image
    theme_manager.save_theme(mocked_theme)

    # THEN: The mocked_copyfile should not have been called
    assert mocked_shutil.copyfile.called is False, 'copyfile should not be called'


@patch('openlp.core.ui.thememanager.shutil')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_diff_images(mocked_create_paths, mocked_shutil, registry):
    """
    Test that we do overwrite a theme background image when a new is submitted
    """
    # GIVEN: A new theme manager instance, with mocked builtins.open, copyfile,
    #        theme, create_paths, thememanager-attributes and background
    #       .filename path is the same as the source path.
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = None
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.background_filename = RESOURCE_PATH / 'church.jpg'
    mocked_theme.background_source = RESOURCE_PATH / 'church2.jpg'

    # WHEN: Calling save_theme with both background paths to different images
    theme_manager.save_theme(mocked_theme)

    # THEN: The mocked_copyfile should have been called
    assert mocked_shutil.copyfile.called is True, 'copyfile should be called'


@patch('openlp.core.ui.thememanager.shutil')
@patch('openlp.core.ui.thememanager.delete_file')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_delete_old_image(mocked_create_paths, mocked_delete_file, mocked_shutil, registry):
    """
    Test that we do delete a old theme background image when a new is submitted
    """
    # GIVEN: A new theme manager instance, with mocked builtins.open,
    #        theme, create_paths, thememanager-attributes and background
    #       .filename path is the same as the source path.
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = RESOURCE_PATH / 'old_church.png'
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.background_filename = RESOURCE_PATH / 'church.jpg'
    mocked_theme.background_source = RESOURCE_PATH / 'church2.jpg'

    # WHEN: Calling save_theme with both background paths to different images
    theme_manager.save_theme(mocked_theme)

    # THEN: The mocked_delete_file should have been called to delete the old cached background
    assert mocked_delete_file.called is True, 'delete_file should be called'


@patch.object(ThemeManager, 'log_exception')
@patch('openlp.core.ui.thememanager.delete_file')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_missing_original(mocked_paths, mocked_delete, mocked_log_exception, registry):
    """
    Test that we revert to the old theme background image if the source is missing
    when changing the theme. (User doesn't change background but the original is
    missing)
    """
    # GIVEN: A new theme manager instance, with invalid files. Setup as if the user
    # has left the background the same, or reselected the same path.
    # Not using resource dir because I could potentially copy a file
    folder_path = Path(mkdtemp())
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = folder_path / 'old.png'
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.background_filename = folder_path / 'old.png'
    mocked_theme.background_source = folder_path / 'non_existent_original.png'

    # WHEN: Calling save_theme with a invalid background_filename
    # Although all filenames are considered invalid in this test,
    # it is important it reverts to the old background path as this in reality is always
    # valid unless someone has messed with the cache.
    theme_manager.save_theme(mocked_theme)

    # THEN: The old background should not have bee deleted
    #       AND the filename should have been replaced with the old cached background
    #       AND there is no exception
    assert mocked_delete.called is False, 'delete_file should not be called'
    assert mocked_theme.background_filename == theme_manager.old_background_image_path, \
        'Background path should be reverted'
    assert mocked_log_exception.called is False, \
        'Should not have been an exception as the file wasn\'t changed'


@patch.object(ThemeManager, 'log_warning')
@patch('openlp.core.ui.thememanager.delete_file')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_missing_new(mocked_paths, mocked_delete, mocked_log_warning, registry):
    """
    Test that we log a warning if the new background is missing
    """
    # GIVEN: A new theme manager instance, with invalid files. Setup as if the user
    # has changed the background to a invalid path.
    # Not using resource dir because I could potentially copy a file
    folder_path = Path(mkdtemp())
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = folder_path / 'old.png'
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.background_filename = folder_path / 'new_cached.png'
    mocked_theme.background_source = folder_path / 'new_original.png'

    # WHEN: Calling save_theme with a invalid background_filename
    theme_manager.save_theme(mocked_theme)

    # THEN: A warning should have happened due to attempting to copy a missing file
    mocked_log_warning.assert_called_once_with('Background does not exist, retaining cached background')


@patch('openlp.core.ui.thememanager.shutil')
@patch('openlp.core.ui.thememanager.delete_file')
@patch('openlp.core.ui.thememanager.create_paths')
def test_save_theme_background_override(mocked_paths, mocked_delete, mocked_shutil, registry):
    """
    Test that we log a warning if the new background is missing
    """
    # GIVEN: A new theme manager instance, with invalid files. Setup as if the user
    # has changed the background to a invalid path.
    # Not using resource dir because I could potentially copy a file
    folder_path = Path(mkdtemp())
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = folder_path / 'old.png'
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = MagicMock()
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'themename'
    mocked_theme.background_filename = folder_path / 'new_cached.png'
    # mocked_theme.background_source.exists() will return True
    mocked_theme.background_source = MagicMock()
    # override_background.exists() will return True
    override_background = MagicMock()

    # WHEN: Calling save_theme with a background override
    theme_manager.save_theme(mocked_theme, background_override=override_background)

    # THEN: The override_background should have been copied rather than the background_source
    mocked_shutil.copyfile.assert_called_once_with(override_background, mocked_theme.background_filename)


def test_save_theme_special_char_name(registry, temp_folder):
    """
    Test that we can save themes with special characters in the name
    """
    # GIVEN: A new theme manager instance, with mocked theme and thememanager-attributes.
    theme_manager = ThemeManager(None)
    theme_manager.old_background_image_path = None
    theme_manager.update_preview_images = MagicMock()
    theme_manager.theme_path = Path(temp_folder)
    mocked_theme = MagicMock()
    mocked_theme.theme_name = 'theme 愛 name'
    mocked_theme.export_theme.return_value = "{}"

    # WHEN: Calling save_theme with a theme with a name with special characters in it
    theme_manager.save_theme(mocked_theme)

    # THEN: It should have been created
    assert os.path.exists(os.path.join(temp_folder, 'theme 愛 name', 'theme 愛 name.json')) is True, \
        'Theme with special characters should have been created!'


@patch('openlp.core.ui.thememanager.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.Yes)
@patch('openlp.core.ui.thememanager.translate')
def test_over_write_message_box_yes(mocked_translate, mocked_qmessagebox_question, registry):
    """
    Test that theme_manager.over_write_message_box returns True when the user clicks yes.
    """
    # GIVEN: A patched QMessageBox.question and an instance of ThemeManager
    mocked_translate.side_effect = lambda context, text: text
    theme_manager = ThemeManager(None)

    # WHEN: Calling over_write_message_box with 'Theme Name'
    result = theme_manager.over_write_message_box('Theme Name')

    # THEN: over_write_message_box should return True and the message box should contain the theme name
    assert result is True
    mocked_qmessagebox_question.assert_called_once_with(
        theme_manager, 'Theme Already Exists', 'Theme Theme Name already exists. Do you want to replace it?',
        defaultButton=ANY)


@patch('openlp.core.ui.thememanager.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.No)
@patch('openlp.core.ui.thememanager.translate')
def test_over_write_message_box_no(mocked_translate, mocked_qmessagebox_question, registry):
    """
    Test that theme_manager.over_write_message_box returns False when the user clicks no.
    """
    # GIVEN: A patched QMessageBox.question and an instance of ThemeManager
    mocked_translate.side_effect = lambda context, text: text
    theme_manager = ThemeManager(None)

    # WHEN: Calling over_write_message_box with 'Theme Name'
    result = theme_manager.over_write_message_box('Theme Name')

    # THEN: over_write_message_box should return False and the message box should contain the theme name
    assert result is False
    mocked_qmessagebox_question.assert_called_once_with(
        theme_manager, 'Theme Already Exists', 'Theme Theme Name already exists. Do you want to replace it?',
        defaultButton=ANY)


@patch('openlp.core.lib.theme.Theme.set_default_header_footer')
def test_unzip_theme(mocked_theme_set_defaults, registry):
    """
    Test that unzipping of themes works
    """
    # GIVEN: A theme file, a output folder and some mocked out internal functions
    with patch('openlp.core.ui.thememanager.critical_error_message_box') \
            as mocked_critical_error_message_box:
        theme_manager = ThemeManager(None)
        theme_manager.update_preview_images = MagicMock()
        theme_manager.theme_path = Path(mkdtemp())
        theme_file_path = RESOURCE_PATH / 'themes' / 'Moss_on_tree.otz'

        # WHEN: We try to unzip it
        theme_manager.unzip_theme(theme_file_path)

        # THEN: Files should be unpacked AND xml file should be upgraded to json
        assert (theme_manager.theme_path / 'Moss on tree' / 'Moss on tree.xml').exists() is False
        assert (theme_manager.theme_path / 'Moss on tree' / 'Moss on tree.json').exists() is True
        assert mocked_critical_error_message_box.call_count == 0, 'No errors should have happened'
        shutil.rmtree(theme_manager.theme_path)


def test_unzip_theme_invalid_version(registry):
    """
    Test that themes with invalid (< 2.0) or with no version attributes are rejected
    """
    # GIVEN: An instance of ThemeManager whilst mocking a theme that returns a theme with no version attribute
    with patch('openlp.core.ui.thememanager.zipfile.ZipFile') as mocked_zip_file,\
            patch('openlp.core.ui.thememanager.ElementTree.getroot') as mocked_getroot,\
            patch('openlp.core.ui.thememanager.XML'),\
            patch('openlp.core.ui.thememanager.critical_error_message_box') as mocked_critical_error_message_box:

        mocked_zip_file.return_value = MagicMock(**{'namelist.return_value': [os.path.join('theme', 'theme.xml')]})
        mocked_getroot.return_value = MagicMock(**{'get.return_value': None})
        theme_manager = ThemeManager(None)
        theme_manager.theme_path = Path('folder')

        # WHEN: unzip_theme is called
        theme_manager.unzip_theme(Path('theme.file'))

        # THEN: The critical_error_message_box should have been called
        assert mocked_critical_error_message_box.call_count == 1, 'Should have been called once'


def test_update_preview_images(registry):
    """
    Test that the update_preview_images() method works correctly
    """
    # GIVEN: A ThemeManager
    def get_theme_data(value):
        return '{}_theme_data'.format(value)
    theme_manager = ThemeManager(None)
    theme_manager.save_preview = MagicMock()
    theme_manager._get_theme_data = Mock(side_effect=get_theme_data)
    theme_manager.progress_form = MagicMock(**{'get_preview.return_value': 'preview'})
    theme_manager.load_themes = MagicMock()
    theme_list = {'Default': get_theme_data('Default'), 'Test': get_theme_data('Test')}

    # WHEN: ThemeManager.update_preview_images() is called
    theme_manager.update_preview_images(theme_list)

    # THEN: Things should work right
    assert theme_manager.progress_form.theme_list == theme_list
    theme_manager.progress_form.show.assert_called_once_with()
    assert theme_manager.progress_form.get_preview.call_args_list == [call('Default', get_theme_data('Default')),
                                                                      call('Test', get_theme_data('Test'))]
    assert theme_manager.save_preview.call_args_list == [call('Default', 'preview'), call('Test', 'preview')]
    theme_manager.progress_form.close.assert_called_once_with()
    theme_manager.load_themes.assert_called_once_with()
