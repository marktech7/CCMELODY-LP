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
Test the ThemeForm class and related methods.
"""
from pathlib import Path
from unittest.mock import patch, MagicMock

from openlp.core.common.registry import Registry
from openlp.core.lib.theme import BackgroundType
from openlp.core.ui.themeform import ThemeForm
from openlp.core.ui.themelayoutform import ThemeLayoutForm


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_create_theme_wizard(mocked_setup, settings):
    """
    Test creating a ThemeForm instance
    """
    # GIVEN: A ThemeForm class
    # WHEN: An object is created
    # THEN: There should be no problems
    ThemeForm(None)


def test_setup(settings):
    """
    Test the _setup method
    """
    # GIVEN: A ThemeForm instance
    with patch('openlp.core.ui.themeform.ThemeForm._setup'):
        theme_form = ThemeForm(None)
    theme_form.setup_ui = MagicMock()
    theme_form.main_area_page = MagicMock()
    theme_form.footer_area_page = MagicMock()

    # WHEN: _setup() is called
    theme_form._setup()

    # THEN: The right calls should have been made
    theme_form.setup_ui.assert_called_once_with(theme_form)
    assert theme_form.can_update_theme is True
    assert theme_form.temp_background_filename is None
    assert isinstance(theme_form.theme_layout_form, ThemeLayoutForm)
    theme_form.main_area_page.font_name_changed.connect.assert_called_once_with(theme_form.calculate_lines)
    theme_form.main_area_page.font_size_changed.connect.assert_called_once_with(theme_form.calculate_lines)
    theme_form.main_area_page.line_spacing_changed.connect.assert_called_once_with(theme_form.calculate_lines)
    theme_form.main_area_page.is_outline_enabled_changed.connect.assert_called_once_with(
        theme_form.on_outline_toggled)
    theme_form.main_area_page.outline_size_changed.connect.assert_called_once_with(theme_form.calculate_lines)
    theme_form.main_area_page.is_shadow_enabled_changed.connect.assert_called_once_with(
        theme_form.on_shadow_toggled)
    theme_form.main_area_page.shadow_size_changed.connect.assert_called_once_with(theme_form.calculate_lines)
    theme_form.footer_area_page.font_name_changed.connect.assert_called_once_with(theme_form.update_theme)
    theme_form.footer_area_page.font_size_changed.connect.assert_called_once_with(theme_form.update_theme)


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_set_defaults(mocked_setup, settings):
    """
    Test that the right methods are called by the set_defaults() method
    """
    # GIVEN: A ThemeForm instance with mocked methods
    theme_form = ThemeForm(None)
    theme_form.restart = MagicMock()
    theme_form.set_background_page_values = MagicMock()
    theme_form.set_main_area_page_values = MagicMock()
    theme_form.set_footer_area_page_values = MagicMock()
    theme_form.set_alignment_page_values = MagicMock()
    theme_form.set_position_page_values = MagicMock()
    theme_form.set_preview_page_values = MagicMock()

    # WHEN: set_defaults() is called
    theme_form.set_defaults()

    # THEN: all the mocks are called
    theme_form.restart.assert_called_once()
    theme_form.set_background_page_values.assert_called_once()
    theme_form.set_main_area_page_values.assert_called_once()
    theme_form.set_footer_area_page_values.assert_called_once()
    theme_form.set_alignment_page_values.assert_called_once()
    theme_form.set_position_page_values.assert_called_once()
    theme_form.set_preview_page_values.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_calculate_lines(mocked_setup, settings):
    """
    Test the calculate_lines() method
    """
    # GIVEN: A ThemeForm instance with some mocked methods
    theme_form = ThemeForm(None)
    theme_form.theme = None
    theme_form.welcome_page = None
    theme_form.currentPage = MagicMock()
    theme_form.update_theme = MagicMock()
    mocked_theme_manager = MagicMock()
    Registry().register('theme_manager', mocked_theme_manager)

    # WHEN: calculate_lines() is called
    theme_form.calculate_lines()

    # THEN: The mocks should have been called correctly
    theme_form.currentPage.assert_called_once()
    theme_form.update_theme.assert_called_once()
    mocked_theme_manager.generate_image.assert_called_once_with(None, True)


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_update_lines_text(mocked_setup, settings):
    """
    Test the update_lines_text() method
    """
    # GIVEN: A ThemeForm instance with some mocked methods
    theme_form = ThemeForm(None)
    theme_form.main_line_count_label = MagicMock()

    # WHEN: calculate_lines() is called
    theme_form.update_lines_text(10)

    # THEN: The mocks should have been called correctly
    theme_form.main_line_count_label.setText.assert_called_once_with('(approximately 10 lines per slide)')


@patch('openlp.core.ui.themeform.QtWidgets.QWizard.resizeEvent')
@patch('openlp.core.ui.themeform.QtGui.QResizeEvent')
@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_resize_event(mocked_setup, MockResizeEvent, mocked_resizeEvent, settings):
    """
    Test that the resizeEvent method handles resizing correctly
    """
    # GIVEN: A ThemeForm instance with a number of mocked methods
    mocked_event = MagicMock()
    MockResizeEvent.return_value = mocked_event
    theme_form = ThemeForm(None)
    theme_form.size = MagicMock(return_value=1920)
    theme_form.preview_area_layout = MagicMock()
    theme_form.preview_box = MagicMock(**{'width.return_value': 300})
    mocked_renderer = MagicMock(**{'width.return_value': 1920, 'height.return_value': 1080})
    Registry().remove('renderer')
    Registry().register('renderer', mocked_renderer)

    # WHEN: resizeEvent() is called
    theme_form.resizeEvent()

    # THEN: The correct calls should have been made
    MockResizeEvent.assert_called_once_with(1920, 1920)
    mocked_resizeEvent.assert_called_once_with(theme_form, mocked_event)
    assert mocked_renderer.width.call_count == 2
    mocked_renderer.height.assert_called_once()
    theme_form.preview_area_layout.set_aspect_ratio.assert_called_once_with(16 / 9)
    theme_form.preview_box.set_scale.assert_called_once_with(float(300 / 1920))


@patch('openlp.core.ui.themeform.QtWidgets.QWizard.resizeEvent')
@patch('openlp.core.ui.themeform.QtGui.QResizeEvent')
@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_resize_event_dbze(mocked_setup, MockResizeEvent, mocked_resizeEvent, settings):
    """
    Test that the resizeEvent method handles a divide by zero exception correctly
    """
    # GIVEN: A ThemeForm instance with a number of mocked methods
    mocked_event = MagicMock()
    MockResizeEvent.return_value = mocked_event
    theme_form = ThemeForm(None)
    theme_form.size = MagicMock(return_value=1920)
    theme_form.preview_area_layout = MagicMock()
    theme_form.preview_box = MagicMock(**{'width.return_value': 300})
    mocked_renderer = MagicMock(**{'width.return_value': 1920, 'height.return_value': 0})
    Registry().remove('renderer')
    Registry().register('renderer', mocked_renderer)

    # WHEN: resizeEvent() is called
    theme_form.resizeEvent()

    # THEN: The correct calls should have been made
    MockResizeEvent.assert_called_once_with(1920, 1920)
    mocked_resizeEvent.assert_called_once_with(theme_form, mocked_event)
    assert mocked_renderer.width.call_count == 2
    mocked_renderer.height.assert_called_once()
    theme_form.preview_area_layout.set_aspect_ratio.assert_called_once_with(1)
    theme_form.preview_box.set_scale.assert_called_once_with(float(300 / 1920))


@patch('openlp.core.ui.themeform.QtWidgets.QMessageBox.critical')
@patch('openlp.core.ui.themeform.is_not_image_file')
@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_validate_current_page_with_image(mocked_setup, mocked_is_not_image_file, mocked_critical, settings):
    """
    Test the validateCurrentPage() method
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock(background_type=BackgroundType.to_string(BackgroundType.Image),
                                           image_path=Path('picture.jpg'))
    theme_form.page = MagicMock(return_value=theme_form.background_page)
    mocked_is_not_image_file.return_value = True

    # WHEN: validateCurrentPage() is called
    result = theme_form.validateCurrentPage()

    # THEN: The right methods were called, and the result is False
    mocked_critical.assert_called_once_with(theme_form, 'Background Image Empty',
                                            'You have not selected a background image. '
                                            'Please select one before continuing.')
    assert result is False


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_validate_current_page(mocked_setup, settings):
    """
    Test the validateCurrentPage() method
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.page = MagicMock()

    # WHEN: validateCurrentPage() is called
    result = theme_form.validateCurrentPage()

    # THEN: The right methods were called, and the result is False
    assert result is True


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_on_current_id_changed_preview(mocked_setup, settings):
    """
    Test the on_current_id_changed() method
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.theme = 'my fake theme'
    theme_form.area_position_page = MagicMock()
    theme_form.preview_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.preview_page)
    theme_form.update_theme = MagicMock()
    theme_form.preview_box = MagicMock(**{'width.return_value': 300})
    theme_form.preview_area_layout = MagicMock()
    theme_form.resizeEvent = MagicMock()
    mocked_renderer = MagicMock(**{'width.return_value': 1920, 'height.return_value': 0})
    Registry().remove('renderer')
    Registry().register('renderer', mocked_renderer)

    # WHEN: on_current_id_changed() is called
    theme_form.on_current_id_changed(1)

    # THEN: The right options should have been set
    theme_form.update_theme.assert_called_once()
    theme_form.resizeEvent.assert_called_once()
    theme_form.preview_box.clear_slides.assert_called_once()
    theme_form.preview_box.show.assert_called_once()
    theme_form.preview_box.generate_preview.assert_called_once_with('my fake theme', False, False)


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_on_outline_toggled(mocked_setup, settings):
    """
    Test the on_outline_toggled() method
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.can_update_theme = True
    theme_form.theme = MagicMock()
    theme_form.calculate_lines = MagicMock()

    # WHEN: on_outline_toggled is called
    theme_form.on_outline_toggled(True)

    # THEN: Everything is working right
    assert theme_form.theme.font_main_outline is True
    theme_form.calculate_lines.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_on_shadow_toggled(mocked_setup, settings):
    """
    Test the on_shadow_toggled() method
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.can_update_theme = True
    theme_form.theme = MagicMock()
    theme_form.calculate_lines = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.on_shadow_toggled(True)

    # THEN: Everything is working right
    assert theme_form.theme.font_main_shadow is True
    theme_form.calculate_lines.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_initialise_page_background(mocked_setup, settings):
    """
    Test the initializePage() method with the background page
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.background_page)
    theme_form.set_background_page_values = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.initializePage(0)

    # THEN: Everything is working right
    theme_form.set_background_page_values.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_initialise_page_main_area(mocked_setup, settings):
    """
    Test the initializePage() method with the main_area page
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.main_area_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.main_area_page)
    theme_form.set_main_area_page_values = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.initializePage(0)

    # THEN: Everything is working right
    theme_form.set_main_area_page_values.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_initialise_page_footer_area(mocked_setup, settings):
    """
    Test the initializePage() method with the footer_area page
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.main_area_page = MagicMock()
    theme_form.footer_area_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.footer_area_page)
    theme_form.set_footer_area_page_values = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.initializePage(0)

    # THEN: Everything is working right
    theme_form.set_footer_area_page_values.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_initialise_page_alignment(mocked_setup, settings):
    """
    Test the initializePage() method with the alignment page
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.main_area_page = MagicMock()
    theme_form.footer_area_page = MagicMock()
    theme_form.alignment_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.alignment_page)
    theme_form.set_alignment_page_values = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.initializePage(0)

    # THEN: Everything is working right
    theme_form.set_alignment_page_values.assert_called_once()


@patch('openlp.core.ui.themeform.ThemeForm._setup')
def test_initialise_page_area_position(mocked_setup, settings):
    """
    Test the initializePage() method with the area_position page
    """
    # GIVEN: An instance of ThemeForm with some mocks
    theme_form = ThemeForm(None)
    theme_form.background_page = MagicMock()
    theme_form.main_area_page = MagicMock()
    theme_form.footer_area_page = MagicMock()
    theme_form.alignment_page = MagicMock()
    theme_form.area_position_page = MagicMock()
    theme_form.page = MagicMock(return_value=theme_form.area_position_page)
    theme_form.set_position_page_values = MagicMock()

    # WHEN: on_shadow_toggled is called
    theme_form.initializePage(0)

    # THEN: Everything is working right
    theme_form.set_position_page_values.assert_called_once()
