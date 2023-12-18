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
Package to test the openlp.core.themes.editor_widgets.background package.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.lib.theme import BackgroundType, BackgroundGradientType
from openlp.core.themes.editor_widgets.background import BackgroundWidget


def test_init_(settings):
    """
    Test the initialisation of BackgroundWidget
    """
    # GIVEN: The BackgroundWidget class
    # WHEN: Initialising BackgroundWidget
    # THEN: We should have an instance of the widget with no errors
    BackgroundWidget()


def test_on_background_type_index_changed(settings):
    """
    Test the _on_background_type_index_changed() slot
    """
    # GIVEN: And instance of BackgroundWidget and some mock widgets
    widget = BackgroundWidget()
    widget.color_widgets = [MagicMock()]
    widget.gradient_widgets = [MagicMock()]

    # WHEN: _on_background_type_index_changed
    widget._on_background_type_index_changed(1)

    # THEN: The correct widgets should be visible
    widget.color_widgets[0].hide.assert_called_once()
    widget.gradient_widgets[0].hide.assert_called_once()
    widget.gradient_widgets[0].show.assert_called_once()


def test_get_background_type(settings):
    """
    Test the background_type getter
    """
    # GIVEN: A BackgroundWidget instance with the combobox set to index 1
    widget = BackgroundWidget()
    widget.background_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = widget.background_type

    # THEN: The result should be correct
    assert result == 'gradient'


def test_set_background_type_int(settings):
    """
    Test the background_type setter with an int
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.background_type = BackgroundType.Image

    # THEN: The combobox should be correct
    assert widget.background_combo_box.currentIndex() == 2


def test_set_background_type_str(settings):
    """
    Test the background_type setter with a str
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.background_type = BackgroundType.to_string(BackgroundType.Gradient)

    # THEN: The combobox should be correct
    assert widget.background_combo_box.currentIndex() == 1


def test_set_background_type_exception(settings):
    """
    Test the background_type setter with something other than a str or int
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='background_type must either be a string or an int'):
        widget.background_type = []


def test_get_color(settings):
    """
    Test the color getter
    """
    # GIVEN: A BackgroundWidget instance with the color button set to #f0f
    widget = BackgroundWidget()
    widget.color_button.color = '#f0f'

    # WHEN: The property is accessed
    result = widget.color

    # THEN: The result should be correct
    assert result == '#f0f'


def test_set_color(settings):
    """
    Test the color setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.color = '#0f0'

    # THEN: The result should be correct
    assert widget.color_button.color == '#0f0'


def test_get_gradient_type(settings):
    """
    Test the gradient_type getter
    """
    # GIVEN: A BackgroundWidget instance with the combobox set to index 1
    widget = BackgroundWidget()
    widget.gradient_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = widget.gradient_type

    # THEN: The result should be correct
    assert result == 'vertical'


def test_set_gradient_type_int(settings):
    """
    Test the gradient_type setter with an int
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.gradient_type = BackgroundGradientType.Horizontal

    # THEN: The combobox should be correct
    assert widget.gradient_combo_box.currentIndex() == 0


def test_set_gradient_type_str(settings):
    """
    Test the gradient_type setter with a str
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.gradient_type = BackgroundGradientType.to_string(BackgroundGradientType.Circular)

    # THEN: The combobox should be correct
    assert widget.gradient_combo_box.currentIndex() == 2


def test_set_gradient_type_exception(settings):
    """
    Test the gradient_type setter with something other than a str or int
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='gradient_type must either be a string or an int'):
        widget.gradient_type = []


def test_get_gradient_start(settings):
    """
    Test the gradient_start getter
    """
    # GIVEN: A BackgroundWidget instance with the gradient_start button set to #f0f
    widget = BackgroundWidget()
    widget.gradient_start_button.color = '#f0f'

    # WHEN: The property is accessed
    result = widget.gradient_start

    # THEN: The result should be correct
    assert result == '#f0f'


def test_set_gradient_start(settings):
    """
    Test the gradient_start setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.gradient_start = '#0f0'

    # THEN: The result should be correct
    assert widget.gradient_start_button.color == '#0f0'


def test_get_gradient_end(settings):
    """
    Test the gradient_end getter
    """
    # GIVEN: A BackgroundWidget instance with the gradient_end button set to #f0f
    widget = BackgroundWidget()
    widget.gradient_end_button.color = '#f0f'

    # WHEN: The property is accessed
    result = widget.gradient_end

    # THEN: The result should be correct
    assert result == '#f0f'


def test_set_gradient_end(settings):
    """
    Test the gradient_end setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.gradient_end = '#0f0'

    # THEN: The result should be correct
    assert widget.gradient_end_button.color == '#0f0'


def test_get_image_color(settings):
    """
    Test the image_color getter
    """
    # GIVEN: A BackgroundWidget instance with the image_color button set to #f0f
    widget = BackgroundWidget()
    widget.image_color_button.color = '#f0f'

    # WHEN: The property is accessed
    result = widget.image_color

    # THEN: The result should be correct
    assert result == '#f0f'


def test_set_image_color(settings):
    """
    Test the image_color setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.image_color = '#0f0'

    # THEN: The result should be correct
    assert widget.image_color_button.color == '#0f0'


def test_get_image_path(settings):
    """
    Test the image_path getter
    """
    # GIVEN: A BackgroundWidget instance with the image_path edit set to a path
    widget = BackgroundWidget()
    widget.image_path_edit.path = Path('.')

    # WHEN: The property is accessed
    result = widget.image_path

    # THEN: The result should be correct
    assert result == Path('.')


def test_set_image_path(settings):
    """
    Test the image_path setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.image_path = Path('openlp')

    # THEN: The result should be correct
    assert widget.image_path_edit.path == Path('openlp')


def test_get_video_color(settings):
    """
    Test the video_color getter
    """
    # GIVEN: A BackgroundWidget instance with the video_color button set to #f0f
    widget = BackgroundWidget()
    widget.video_color_button.color = '#f0f'

    # WHEN: The property is accessed
    result = widget.video_color

    # THEN: The result should be correct
    assert result == '#f0f'


def test_set_video_color(settings):
    """
    Test the video_color setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.video_color = '#0f0'

    # THEN: The result should be correct
    assert widget.video_color_button.color == '#0f0'


def test_get_video_path(settings):
    """
    Test the video_path getter
    """
    # GIVEN: A BackgroundWidget instance with the video_path edit set to a path
    widget = BackgroundWidget()
    widget.video_path_edit.path = Path('.')

    # WHEN: The property is accessed
    result = widget.video_path

    # THEN: The result should be correct
    assert result == Path('.')


def test_set_video_path(settings):
    """
    Test the video_path setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.video_path = Path('openlp')

    # THEN: The result should be correct
    assert widget.video_path_edit.path == Path('openlp')


def test_get_stream_color(settings):
    """
    Test the stream_color getter
    """
    # GIVEN: A BackgroundWidget instance with the stream_color edit set to a path
    widget = BackgroundWidget()
    widget.stream_color_button.color = '#000'

    # WHEN: The property is accessed
    result = widget.stream_color

    # THEN: The result should be correct
    assert result == '#000'


def test_set_stream_color(settings):
    """
    Test the stream_color setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.stream_color = '#fff'

    # THEN: The result should be correct
    assert widget.stream_color_button.color == '#fff'


def test_get_stream_mrl(settings):
    """
    Test the stream_mrl getter
    """
    # GIVEN: A BackgroundWidget instance with the stream_mrl edit set to a path
    widget = BackgroundWidget()
    widget.stream_lineedit.setText('devicestream:/dev/vid2')

    # WHEN: The property is accessed
    result = widget.stream_mrl

    # THEN: The result should be correct
    assert result == 'devicestream:/dev/vid2'


def test_set_stream_mrl(settings):
    """
    Test the stream_mrl setter
    """
    # GIVEN: A BackgroundWidget instance
    widget = BackgroundWidget()

    # WHEN: The property is set
    widget.stream_mrl = 'devicestream:/dev/vid3'

    # THEN: The result should be correct
    assert widget.stream_lineedit.text() == 'devicestream:/dev/vid3'


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.plugins.media.forms.streamselectorform.StreamSelectorForm')
def test_on_device_stream_select_button_triggered(MockStreamSelectorForm, mocked_get_vlc, settings):
    """Test the device streaming selection

    NOTE: Due to the inline import statement, the source of the form needs to be mocked, not the imported object
    """
    # GIVEN: A BackgroundWidget object and some mocks
    mocked_get_vlc.return_value = True
    mocked_stream_selector_form = MagicMock()
    MockStreamSelectorForm.return_value = mocked_stream_selector_form
    widget = BackgroundWidget()
    widget.stream_lineedit = MagicMock(**{'text.return_value': 'devicestream:/dev/vid0'})

    # WHEN: _on_device_stream_select_button_triggered() is called
    widget._on_device_stream_select_button_triggered()

    # THEN: The error should have been shown
    # Using WidgetProxy internal property until Theme Wizard is entirely migrated to Theme Editor
    MockStreamSelectorForm.assert_called_once_with(widget, widget.set_stream, True)
    mocked_stream_selector_form.set_mrl.assert_called_once_with('devicestream:/dev/vid0')
    mocked_stream_selector_form.exec.assert_called_once_with()


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.core.themes.editor_widgets.background.critical_error_message_box')
def test_on_device_stream_select_button_triggered_no_vlc(mocked_critical_box, mocked_get_vlc, settings):
    """Test that if VLC is not available, an error message is shown"""
    # GIVEN: A BackgroundWidget object and some mocks
    mocked_get_vlc.return_value = None
    widget = BackgroundWidget()

    # WHEN: _on_device_stream_select_button_triggered() is called
    widget._on_device_stream_select_button_triggered()

    # THEN: The error should have been shown
    mocked_critical_box.assert_called_once_with('VLC is not available', 'Device streaming support requires VLC.')


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.plugins.media.forms.networkstreamselectorform.NetworkStreamSelectorForm')
def test_on_network_stream_select_button_triggered(MockStreamSelectorForm, mocked_get_vlc, settings):
    """Test the network streaming selection

    NOTE: Due to the inline import statement, the source of the form needs to be mocked, not the imported object
    """
    # GIVEN: A BackgroundWidget object and some mocks
    mocked_get_vlc.return_value = True
    mocked_stream_selector_form = MagicMock()
    MockStreamSelectorForm.return_value = mocked_stream_selector_form
    widget = BackgroundWidget()
    widget.stream_lineedit = MagicMock(**{'text.return_value': 'networkstream:/dev/vid0'})

    # WHEN: _on_network_stream_select_button_triggered() is called
    widget._on_network_stream_select_button_triggered()

    # THEN: The error should have been shown
    # Using WidgetProxy internal property until Theme Wizard is entirely migrated to Theme Editor
    MockStreamSelectorForm.assert_called_once_with(widget, widget.set_stream, True)
    mocked_stream_selector_form.set_mrl.assert_called_once_with('networkstream:/dev/vid0')
    mocked_stream_selector_form.exec.assert_called_once_with()


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.core.themes.editor_widgets.background.critical_error_message_box')
def test_on_network_stream_select_button_triggered_no_vlc(mocked_critical_box, mocked_get_vlc, settings):
    """Test that if VLC is not available, an error message is shown"""
    # GIVEN: A BackgroundWidget object and some mocks
    mocked_get_vlc.return_value = None
    widget = BackgroundWidget()

    # WHEN: _on_network_stream_select_button_triggered() is called
    widget._on_network_stream_select_button_triggered()

    # THEN: The error should have been shown
    mocked_critical_box.assert_called_once_with('VLC is not available', 'Network streaming support requires VLC.')


def test_set_stream(settings):
    """Test the set_stream() method"""
    # GIVEN: A BackgroundWidget object with a mocked stream_lineedit object
    widget = BackgroundWidget()
    widget.stream_lineedit = MagicMock()

    # WHEN: set_stream is called
    widget.set_stream('devicestream:/dev/vid1')

    # THEN: The line edit should have been updated
    widget.stream_lineedit.setText.assert_called_once_with('devicestream:/dev/vid1')


def test_background_combo_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the background_combo_box value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.background_combo_box.setCurrentIndex(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.plugins.media.forms.streamselectorform.StreamSelectorForm')
def test_device_stream_select_button_triggers_on_value_changed(MockStreamSelectorForm, mocked_get_vlc, settings):
    """
    Test if on_value_changed signal is triggered when the device_stream_select_button value is changed

    NOTE: Due to the inline import statement, the source of the form needs to be mocked, not the imported object
    """
    # GIVEN: An instance of BackgroundWidget, a mocked get_vlc, a mocked StreamSelectorForm
    mocked_get_vlc.return_value = True
    mocked_stream_selector_form = MagicMock()
    MockStreamSelectorForm.return_value = mocked_stream_selector_form
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.device_stream_select_button.click()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


@patch('openlp.core.themes.editor_widgets.background.get_vlc')
@patch('openlp.plugins.media.forms.networkstreamselectorform.NetworkStreamSelectorForm')
def test_network_stream_select_button_triggers_on_value_changed(MockNetworkStreamSelectorForm, mocked_get_vlc,
                                                                settings):
    """
    Test if on_value_changed signal is triggered when the network_stream_select_button value is changed

    NOTE: Due to the inline import statement, the source of the form needs to be mocked, not the imported object
    """
    # GIVEN: An instance of BackgroundWidget, a mocked get_vlc, a mocked StreamSelectorForm
    mocked_get_vlc.return_value = True
    mocked_stream_selector_form = MagicMock()
    MockNetworkStreamSelectorForm.return_value = mocked_stream_selector_form
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.network_stream_select_button.click()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_gradient_combo_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the gradient_combo_box value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.gradient_combo_box.setCurrentIndex(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_color_button_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the color_button value is changed
    """
    # GIVEN: An instance of BackgroundWidget and a mocked pick_color
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()
    widget.color_button.pick_color = MagicMock()
    widget.color_button.pick_color.return_value = MagicMock(
        **{'isValid.return_value': True, 'name.return_value': '#ab0123'})

    # WHEN: The value is changed
    widget.color_button.on_clicked()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_image_color_button_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the image_color_button value is changed
    """
    # GIVEN: An instance of BackgroundWidget and a mocked pick_color
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()
    widget.image_color_button.pick_color = MagicMock()
    widget.image_color_button.pick_color.return_value = MagicMock(
        **{'isValid.return_value': True, 'name.return_value': '#ab0123'})

    # WHEN: The value is changed
    widget.image_color_button.on_clicked()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_gradient_start_button_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the gradient_start_button value is changed
    """
    # GIVEN: An instance of BackgroundWidget and a mocked pick_color
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()
    widget.gradient_start_button.pick_color = MagicMock()
    widget.gradient_start_button.pick_color.return_value = MagicMock(
        **{'isValid.return_value': True, 'name.return_value': '#ab0123'})

    # WHEN: The value is changed
    widget.gradient_start_button.on_clicked()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_gradient_end_button_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the gradient_end_button value is changed
    """
    # GIVEN: An instance of BackgroundWidget and a mocked pick_color
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()
    widget.gradient_end_button.pick_color = MagicMock()
    widget.gradient_end_button.pick_color.return_value = MagicMock(
        **{'isValid.return_value': True, 'name.return_value': '#ab0123'})

    # WHEN: The value is changed
    widget.gradient_end_button.on_clicked()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


@patch('openlp.core.widgets.buttons.QtWidgets.QColorDialog')
def test_video_color_button_triggers_on_value_changed(MockQColorDialog, settings):
    """
    Test if on_value_changed signal is triggered when the video_color_button value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()
    widget.video_color_button.pick_color = MagicMock()
    widget.video_color_button.pick_color.return_value = MagicMock(
        **{'isValid.return_value': True, 'name.return_value': '#ab0123'})

    # WHEN: The value is changed
    widget.video_color_button.on_clicked()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_stream_lineedit_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the stream_lineedit value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.stream_lineedit.setText('devicestream:/dev/vid1')

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_image_path_edit_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the image_path_edit value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.image_path_edit.on_new_path(Path('/opt/test.png'))

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_video_path_edit_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the video_path_edit value is changed
    """
    # GIVEN: An instance of BackgroundWidget
    widget = BackgroundWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The value is changed
    widget.video_path_edit.on_new_path(Path('/opt/test.png'))

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()
