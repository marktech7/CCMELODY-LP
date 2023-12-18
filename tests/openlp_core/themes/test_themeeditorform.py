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
Test the ThemeEditorForm class and related methods.
"""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from openlp.core.common.registry import Registry
from openlp.core.lib.theme import BackgroundType
from openlp.core.themes.themeeditorform import ThemeEditorForm


def _make_path(s):
    return MagicMock(**{'__str__.return_value': s, 'exists.return_value': True})


THEME_BACKGROUNDS = {
    'solid': [
        ('color', 'background_color', '#ff0')
    ],
    'gradient': [
        ('gradient_type', 'background_direction', 'horizontal'),
        ('gradient_start', 'background_start_color', '#fff'),
        ('gradient_end', 'background_end_color', '#000')
    ],
    'image': [
        ('image_color', 'background_border_color', '#f0f0f0'),
        ('image_path', 'background_source', Path('/path/to/image.png')),
        ('image_path', 'background_filename', Path('/path/to/image.png'))
    ],
    'video': [
        ('video_color', 'background_border_color', '#222'),
        ('video_path', 'background_source', Path('/path/to/video.mkv')),
        ('video_path', 'background_filename', Path('/path/to/video.mkv'))
    ],
    'stream': [
        ('stream_color', 'background_border_color', '#222'),
        ('stream_mrl', 'background_source', 'http:/127.0.0.1/stream.mkv'),
        ('stream_mrl', 'background_filename', 'http:/127.0.0.1/stream.mkv')
    ]
}


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_create_theme_editor(mocked_setup, settings):
    """
    Test creating a ThemeEditorForm instance
    """
    # GIVEN: A ThemeEditorForm class
    # WHEN: An object is created
    # THEN: There should be no problems
    ThemeEditorForm(None)


def test_setup(settings):
    """
    Test the _setup method
    """
    # GIVEN: A ThemeEditorForm instance
    with patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup'):
        theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.setup_ui = MagicMock()
    theme_editor_form.preview_area = MagicMock()

    # WHEN: _setup() is called
    theme_editor_form._setup()

    # THEN: The right calls should have been made
    theme_editor_form.setup_ui.assert_called_once_with(theme_editor_form)
    assert theme_editor_form.can_update_theme is True
    assert theme_editor_form.temp_background_filename is None
    assert theme_editor_form.use_extended_preview is False


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_connect_events(mocked_setup, settings):
    """
    Test the connect_events method
    """
    # GIVEN: A ThemeEditorForm instance and mocked signals
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.setup_ui = MagicMock()
    theme_editor_form._setup()
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.preview_area = MagicMock()
    theme_editor_form.preview_area_layout = MagicMock()
    theme_editor_form.main_toolbox = MagicMock()
    theme_editor_form.transition_widget_play_button = MagicMock()

    # WHEN: connect_events() is called
    theme_editor_form.connect_events()

    # THEN: The right events should have been connected
    theme_editor_form.background_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.alignment_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.main_area_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.footer_area_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.transition_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.area_position_widget.on_value_changed.connect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.preview_area_layout.resize.connect \
                     .assert_called_once_with(theme_editor_form._update_preview_renderer_scale)
    theme_editor_form.main_toolbox.currentChanged.connect \
                     .assert_called_once_with(theme_editor_form._on_toolbox_item_change)
    theme_editor_form.transition_widget_play_button.clicked.connect \
                     .assert_called_once_with(theme_editor_form.play_transition)
    assert theme_editor_form.preview_area.resizeEventHandler == theme_editor_form \
        ._preview_area_resize_event


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_disconnect_events(mocked_setup, settings):
    """
    Test the disconnect_events method
    """
    # GIVEN: A ThemeEditorForm instance and mocked signals
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.setup_ui = MagicMock()
    theme_editor_form._setup()
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.preview_area = MagicMock()
    theme_editor_form.preview_area_layout = MagicMock()
    theme_editor_form.main_toolbox = MagicMock()
    theme_editor_form.transition_widget_play_button = MagicMock()
    theme_editor_form.connect_events()

    # WHEN: disconnect_events() is called
    theme_editor_form.disconnect_events()

    # THEN: The right events should have been disconnected
    theme_editor_form.background_widget.disconnect_signals.assert_called_once()
    theme_editor_form.alignment_widget.disconnect_signals.assert_called_once()
    theme_editor_form.main_area_widget.disconnect_signals.assert_called_once()
    theme_editor_form.footer_area_widget.disconnect_signals.assert_called_once()
    theme_editor_form.transition_widget.disconnect_signals.assert_called_once()
    theme_editor_form.area_position_widget.disconnect_signals.assert_called_once()
    theme_editor_form.background_widget.on_value_changed.disconnect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.alignment_widget.on_value_changed.disconnect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.main_area_widget.on_value_changed.disconnect.assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.footer_area_widget.on_value_changed.disconnect \
                     .assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.transition_widget.on_value_changed.disconnect \
                     .assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.area_position_widget.on_value_changed.disconnect \
                     .assert_called_once_with(theme_editor_form.do_update)
    theme_editor_form.preview_area_layout.resize.disconnect \
                     .assert_called_once_with(theme_editor_form._update_preview_renderer_scale)
    theme_editor_form.main_toolbox.currentChanged.disconnect \
                     .assert_called_once_with(theme_editor_form._on_toolbox_item_change)
    theme_editor_form.transition_widget_play_button.clicked.disconnect \
                     .assert_called_once_with(theme_editor_form.play_transition)


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_set_defaults(mocked_setup, settings):
    """
    Test that the right methods are called by the set_defaults() method
    """
    # GIVEN: A ThemeEditorForm instance with mocked methods
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.set_background_widget_values = MagicMock()
    theme_editor_form.set_main_area_widget_values = MagicMock()
    theme_editor_form.set_footer_area_widget_values = MagicMock()
    theme_editor_form.set_alignment_widget_values = MagicMock()
    theme_editor_form.set_position_widget_values = MagicMock()
    theme_editor_form.set_transition_widget_values = MagicMock()

    # WHEN: set_defaults() is called
    theme_editor_form.set_defaults()

    # THEN: all the mocks are called
    theme_editor_form.set_background_widget_values.assert_called_once()
    theme_editor_form.set_main_area_widget_values.assert_called_once()
    theme_editor_form.set_footer_area_widget_values.assert_called_once()
    theme_editor_form.set_alignment_widget_values.assert_called_once()
    theme_editor_form.set_position_widget_values.assert_called_once()
    theme_editor_form.set_transition_widget_values.assert_called_once()


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm.setup_ui')
def test_preview_resize_event_connected(mocked_setup_ui, settings):
    """
    Test that the update_preview_renderer_scale is registered on preview_area_layout resize event
    """
    # GIVEN: A ThemeEditorForm instance with a number of mocked methods
    def init_preview_area(theme_editor_form):
        theme_editor_form.preview_area = MagicMock()
        theme_editor_form.preview_area_layout = MagicMock()

    mocked_setup_ui.side_effect = init_preview_area
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.main_toolbox = MagicMock()
    theme_editor_form.transition_widget_play_button = MagicMock()

    # WHEN: connected_events is called
    theme_editor_form.connect_events()

    # THEN: The update_preview_renderer_scale should be assigned in preview_area_layout resize event
    theme_editor_form.preview_area_layout.resize.connect \
                     .assert_called_once_with(theme_editor_form._update_preview_renderer_scale)


@patch('openlp.core.themes.themeeditorform.QtWidgets.QWidget.resizeEvent')
@patch('openlp.core.themes.themeeditorform.QtGui.QResizeEvent')
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm.setup_ui')
def test_preview_resize_event(mocked_setup_ui, MockResizeEvent, mocked_resizeEvent, settings):
    """
    Test that the preview resize method handles resizing correctly
    """
    # GIVEN: A ThemeEditorForm instance with a number of mocked methods
    def init_preview_area(theme_editor_form):
        theme_editor_form.preview_area = MagicMock()
        theme_editor_form.preview_area_layout = MagicMock()
        theme_editor_form.preview_renderer = MagicMock(**{'width.return_value': 300})

    mocked_event = MagicMock()
    MockResizeEvent.return_value = mocked_event
    mocked_setup_ui.side_effect = init_preview_area
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.size = MagicMock(return_value=1920)
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.main_toolbox = MagicMock()
    theme_editor_form.transition_widget_play_button = MagicMock()
    mocked_renderer = MagicMock(**{'width.return_value': 1920, 'height.return_value': 1200})
    Registry().remove('renderer')
    Registry().register('renderer', mocked_renderer)

    # WHEN: _preview_area_resize_event() is called
    theme_editor_form._preview_area_resize_event()

    # THEN: The correct calls should have been made
    MockResizeEvent.assert_called_once_with(1920, 1920)
    mocked_resizeEvent.assert_called_once_with(theme_editor_form.preview_area, mocked_event)
    assert mocked_renderer.width.call_count == 1
    mocked_renderer.height.assert_called_once()
    theme_editor_form.preview_area_layout.set_aspect_ratio.assert_called_once_with(16 / 10)


@patch('openlp.core.themes.themeeditorform.QtWidgets.QWidget.resizeEvent')
@patch('openlp.core.themes.themeeditorform.QtGui.QResizeEvent')
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm.setup_ui')
def test_preview_resize_event_dbze(mocked_setup_ui, MockResizeEvent, mocked_resizeEvent, settings):
    """
    Test that the preview resize method handles division by zero correctly
    """
    # GIVEN: A ThemeEditorForm instance with a number of mocked methods
    def init_preview_area(theme_editor_form):
        theme_editor_form.preview_area = MagicMock()
        theme_editor_form.preview_area_layout = MagicMock()
        theme_editor_form.preview_renderer = MagicMock(**{'width.return_value': 300})

    mocked_event = MagicMock()
    MockResizeEvent.return_value = mocked_event
    mocked_setup_ui.side_effect = init_preview_area
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.size = MagicMock(return_value=1920)
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.main_toolbox = MagicMock()
    theme_editor_form.transition_widget_play_button = MagicMock()
    mocked_renderer = MagicMock(**{'width.return_value': 1920, 'height.return_value': 0})
    Registry().remove('renderer')
    Registry().register('renderer', mocked_renderer)

    # WHEN: _preview_area_resize_event() is called
    theme_editor_form._preview_area_resize_event()

    # THEN: The correct calls should have been made
    MockResizeEvent.assert_called_once_with(1920, 1920)
    mocked_resizeEvent.assert_called_once_with(theme_editor_form.preview_area, mocked_event)
    assert mocked_renderer.width.call_count == 1
    mocked_renderer.height.assert_called_once()
    theme_editor_form.preview_area_layout.set_aspect_ratio.assert_called_once_with(1)


@patch('openlp.core.themes.themeeditorform.QtWidgets.QMessageBox.critical')
@patch('openlp.core.themes.themeeditorform.is_not_image_file')
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm.setup_ui')
def test_validate_fields_with_image(mocked_setup_ui, mocked_is_not_image_file, mocked_critical, settings):
    """
    Test if the validate_fields() method aborts if background image is empty.
    """
    # GIVEN: An instance of ThemeEditorForm with some mocks
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.theme = MagicMock()
    theme_editor_form.background_widget = MagicMock(background_type=BackgroundType.to_string(BackgroundType.Image),
                                                    image_path=Path('picture.jpg'))
    mocked_is_not_image_file.return_value = True

    # WHEN: validate_fields() is called
    result = theme_editor_form.validate_fields()

    # THEN: The right methods were called, and the result is False
    mocked_critical.assert_called_once_with(theme_editor_form, 'Background Image Empty',
                                            'You have not selected a background image. '
                                            'Please select one before continuing.')
    assert result is False


@patch('openlp.core.themes.themeeditorform.QtWidgets.QMessageBox.critical')
@patch('openlp.core.themes.themeeditorform.is_not_image_file')
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm.setup_ui')
def test_validate_fields(mocked_setup_ui, mocked_is_not_image_file, mocked_critical, settings):
    """
    Test the validate_fields() method passes with the default options
    """
    # GIVEN: An instance of ThemeEditorForm with some mocks
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.theme = MagicMock()
    theme_editor_form.background_widget = MagicMock()

    # WHEN: validate_fields() is called
    result = theme_editor_form.validate_fields()

    # THEN: The result is True
    assert result is True


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_update_theme_static(mocked_setup, settings):
    """
    Test that the update_theme() method correctly sets all the "static" theme variables
    """
    # GIVEN: An instance of a ThemeEditorForm with some mocked out widgets which return certain values
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.can_update_theme = True
    theme_editor_form.theme = MagicMock()
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock(font_name='Montserrat', font_color='#f00', font_size=50,
                                                   line_spacing=12, is_outline_enabled=True, outline_color='#00f',
                                                   outline_size=3, is_shadow_enabled=True, shadow_color='#111',
                                                   shadow_size=5, is_bold=True, is_italic=False)
    theme_editor_form.footer_area_widget = MagicMock(font_name='Oxygen', font_color='#fff', font_size=20,
                                                     is_bold=False, is_italic=True)
    theme_editor_form.alignment_widget = MagicMock(horizontal_align='left', vertical_align='top')
    theme_editor_form.transition_widget = MagicMock(is_transition_enabled=True, transition_type='fade',
                                                    transition_speed='normal', transition_direction='horizontal',
                                                    is_transition_reverse_enabled=False)
    theme_editor_form.area_position_widget = MagicMock(use_main_default_location=True,
                                                       use_footer_default_location=True)

    # WHEN: ThemeEditorForm.update_theme() is called
    theme_editor_form.update_theme()

    # THEN: The theme should be correct
    # Main area
    assert theme_editor_form.theme.font_main_name == 'Montserrat'
    assert theme_editor_form.theme.font_main_color == '#f00'
    assert theme_editor_form.theme.font_main_size == 50
    assert theme_editor_form.theme.font_main_line_adjustment == 12
    assert theme_editor_form.theme.font_main_outline is True
    assert theme_editor_form.theme.font_main_outline_color == '#00f'
    assert theme_editor_form.theme.font_main_outline_size == 3
    assert theme_editor_form.theme.font_main_shadow is True
    assert theme_editor_form.theme.font_main_shadow_color == '#111'
    assert theme_editor_form.theme.font_main_shadow_size == 5
    assert theme_editor_form.theme.font_main_bold is True
    assert theme_editor_form.theme.font_main_italics is False
    assert theme_editor_form.theme.font_main_override is False
    theme_editor_form.theme.set_default_header.assert_called_once_with()
    # Footer
    assert theme_editor_form.theme.font_footer_name == 'Oxygen'
    assert theme_editor_form.theme.font_footer_color == '#fff'
    assert theme_editor_form.theme.font_footer_size == 20
    assert theme_editor_form.theme.font_footer_bold is False
    assert theme_editor_form.theme.font_footer_italics is True
    assert theme_editor_form.theme.font_footer_override is False
    theme_editor_form.theme.set_default_footer.assert_called_once_with()
    # Alignment
    assert theme_editor_form.theme.display_horizontal_align == 'left'
    assert theme_editor_form.theme.display_vertical_align == 'top'
    # Transitions
    assert theme_editor_form.theme.display_slide_transition is True
    assert theme_editor_form.theme.display_slide_transition_type == 'fade'
    assert theme_editor_form.theme.display_slide_transition_direction == 'horizontal'
    assert theme_editor_form.theme.display_slide_transition_speed == 'normal'
    assert theme_editor_form.theme.display_slide_transition_reverse is False


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_update_theme_overridden_areas(mocked_setup, settings):
    """
    Test that the update_theme() method correctly sets all the positioning information for a custom position
    """
    # GIVEN: An instance of a ThemeEditorForm with some mocked out widgets which return certain values
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.can_update_theme = True
    theme_editor_form.theme = MagicMock()
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock(use_main_default_location=False,
                                                       use_footer_default_location=False,
                                                       main_x=20, main_y=50, main_height=900, main_width=1880,
                                                       footer_x=20, footer_y=910, footer_height=70, footer_width=1880)

    # WHEN: ThemeEditorForm.update_theme() is called
    theme_editor_form.update_theme()

    # THEN: The theme should be correct
    assert theme_editor_form.theme.font_main_override is True
    assert theme_editor_form.theme.font_main_x == 20
    assert theme_editor_form.theme.font_main_y == 50
    assert theme_editor_form.theme.font_main_height == 900
    assert theme_editor_form.theme.font_main_width == 1880
    assert theme_editor_form.theme.font_footer_override is True
    assert theme_editor_form.theme.font_footer_x == 20
    assert theme_editor_form.theme.font_footer_y == 910
    assert theme_editor_form.theme.font_footer_height == 70
    assert theme_editor_form.theme.font_footer_width == 1880


@pytest.mark.parametrize('background_type', THEME_BACKGROUNDS.keys())
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_update_theme_background(mocked_setup, background_type, settings):
    """
    Test that the update_theme() method correctly sets all the theme background variables for each background type
    """
    # GIVEN: An instance of a ThemeEditorForm with some mocked out widgets which return certain values
    page_props = {page_prop: value for page_prop, _, value in THEME_BACKGROUNDS[background_type]}
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.can_update_theme = True
    theme_editor_form.theme = MagicMock()
    theme_editor_form.background_widget = MagicMock(background_type=background_type, **page_props)
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()

    # WHEN: ThemeEditorForm.update_theme() is called
    theme_editor_form.update_theme()

    # THEN: The theme should be correct
    for _, theme_prop, value in THEME_BACKGROUNDS[background_type]:
        assert getattr(theme_editor_form.theme, theme_prop) == value, f'{theme_prop} should have been {value}'


@pytest.mark.parametrize('background_type', THEME_BACKGROUNDS.keys())
@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_set_background_widget_values(mocked_setup, background_type, settings):
    """
    Test that the set_background_widget_values() method sets the background page values correctly
    """
    # GIVEN: An instance of a ThemeEditorForm with some mocked out widgets and a mocked theme with values
    theme_props = {theme_prop: value for _, theme_prop, value in THEME_BACKGROUNDS[background_type]}
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.theme = MagicMock(background_type=background_type, **theme_props)
    theme_editor_form.background_widget = MagicMock()
    theme_editor_form.main_area_widget = MagicMock()
    theme_editor_form.footer_area_widget = MagicMock()
    theme_editor_form.alignment_widget = MagicMock()
    theme_editor_form.area_position_widget = MagicMock()
    theme_editor_form.transition_widget = MagicMock()

    # WHEN: set_background_widget_values() is called
    theme_editor_form.set_background_widget_values()

    # THEN: The correct values are set on the page
    for page_prop, _, value in THEME_BACKGROUNDS[background_type]:
        assert getattr(theme_editor_form.background_widget, page_prop) == value, (
            f'{page_prop} should have been {value} but was {getattr(theme_editor_form.background_widget, page_prop)}'
        )


@patch('openlp.core.themes.themeeditorform.ThemeEditorForm._setup')
def test_update_theme_cannot_update(mocked_setup, settings):
    """
    Test that the update_theme() method skips out early when the theme cannot be updated
    """
    # GIVEN: An instance of a ThemeEditorForm with some mocked out widgets which return certain values
    theme_editor_form = ThemeEditorForm(None)
    theme_editor_form.can_update_theme = False
    theme_editor_form.theme = None

    # WHEN: ThemeEditorForm.update_theme() is called
    result = theme_editor_form.update_theme()

    # THEN: The theme should be correct, if a NoneType is thrown this means that theme is being
    # accessed before the check is made.
    assert result is False
