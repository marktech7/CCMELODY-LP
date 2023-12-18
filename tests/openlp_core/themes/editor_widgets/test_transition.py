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
Package to test the openlp.core.themes.editor_widgets.alignment package.
"""
from unittest.mock import MagicMock

import pytest

from openlp.core.lib.theme import TransitionType, TransitionSpeed, TransitionDirection
from openlp.core.themes.editor_widgets.transition import TransitionWidget


def test_init_(settings):
    """
    Test the initialisation of TransitionWidget
    """
    # GIVEN: The TransitionWidget class
    # WHEN: Initialising TransitionWidget
    # THEN: We should have an instance of the widget with no errors
    TransitionWidget()


def test_on_transition_enabled_changed(settings):
    """
    Test the _on_transition_enabled_changed() slot
    """
    # GIVEN: An instance of TransitionWidget and some mock widgets
    widget = TransitionWidget()

    # WHEN: _on_transition_enabled_changed
    widget._on_transition_enabled_changed(True)

    # THEN: The correct widgets should be visible
    assert widget.transition_effect_label.isEnabled()
    assert widget.transition_effect_combo_box.isEnabled()
    assert widget.transition_speed_label.isEnabled()
    assert widget.transition_speed_combo_box.isEnabled()
    assert widget.transition_direction_combo_box.isEnabled()
    assert widget.transition_reverse_check_box.isEnabled()


def test_get_is_transition_enabled(settings):
    """
    Test the is_transition_enabled getter
    """
    # GIVEN: A TransitionWidget instance with the transitions enabled
    widget = TransitionWidget()
    widget.transitions_enabled_check_box.setChecked(False)

    # WHEN: The property is accessed
    result = widget.is_transition_enabled

    # THEN: The result should be correct
    assert result is False


def test_set_is_transition_enabled(settings):
    """
    Test the is_transition_enabled setter
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()
    widget._on_transition_enabled_changed = MagicMock()

    # WHEN: The property is set
    widget.is_transition_enabled = True

    # THEN: The result should be correct
    assert widget.transitions_enabled_check_box.isChecked() is True
    widget._on_transition_enabled_changed.assert_called_once_with(True)


def test_get_transition_type(settings):
    """
    Test the transition_type getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 1
    widget = TransitionWidget()
    widget.transition_effect_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = widget.transition_type

    # THEN: The result should be correct
    assert result == TransitionType.Slide


def test_set_transition_type_int(settings):
    """
    Test the transition_type setter with an int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_type = TransitionType.Concave

    # THEN: The combobox should be correct
    assert widget.transition_effect_combo_box.currentIndex() == 3


def test_set_transition_type_str(settings):
    """
    Test the transition_type setter with a str
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_type = TransitionType.to_string(TransitionType.Convex)

    # THEN: The combobox should be correct
    assert widget.transition_effect_combo_box.currentIndex() == 2


def test_set_transition_type_exception(settings):
    """
    Test the transition_type setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_type must either be a string or an int'):
        widget.transition_type = []


def test_get_transition_speed(settings):
    """
    Test the transition_speed getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 0
    widget = TransitionWidget()
    widget.transition_speed_combo_box.setCurrentIndex(0)

    # WHEN: The property is accessed
    result = widget.transition_speed

    # THEN: The result should be correct
    assert result == TransitionSpeed.Normal


def test_set_transition_speed_int(settings):
    """
    Test the transition_speed setter with an int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_speed = TransitionSpeed.Fast

    # THEN: The combobox should be correct
    assert widget.transition_speed_combo_box.currentIndex() == 1


def test_set_transition_speed_str(settings):
    """
    Test the transition_speed setter with a str
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_speed = TransitionSpeed.to_string(TransitionSpeed.Slow)

    # THEN: The combobox should be correct
    assert widget.transition_speed_combo_box.currentIndex() == 2


def test_set_transition_speed_exception(settings):
    """
    Test the transition_speed setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_speed must either be a string or an int'):
        widget.transition_speed = []


def test_get_transition_direction(settings):
    """
    Test the transition_direction getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 0
    widget = TransitionWidget()
    widget.transition_direction_combo_box.setCurrentIndex(0)

    # WHEN: The property is accessed
    result = widget.transition_direction

    # THEN: The result should be correct
    assert result == TransitionDirection.Horizontal


def test_set_transition_direction_int(settings):
    """
    Test the transition_direction setter with an int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_direction = TransitionDirection.Horizontal

    # THEN: The combobox should be correct
    assert widget.transition_direction_combo_box.currentIndex() == 0


def test_set_transition_direction_str(settings):
    """
    Test the transition_direction setter with a str
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.transition_direction = TransitionDirection.to_string(TransitionDirection.Vertical)

    # THEN: The combobox should be correct
    assert widget.transition_direction_combo_box.currentIndex() == 1


def test_set_transition_direction_exception(settings):
    """
    Test the transition_direction setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    widget = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_direction must either be a string or an int'):
        widget.transition_direction = []


def test_on_transition_reverse_getter(settings):
    """
    Test the is_transition_reverse_enabled getter
    """
    # GIVEN: An instance of TransitionWidget and transition_reverse checked
    widget = TransitionWidget()
    widget.transition_reverse_check_box.setChecked(True)

    # WHEN: The property is accessed
    result = widget.is_transition_reverse_enabled

    # THEN: The result should be correct
    assert result is True


def test_on_transition_reverse_setter(settings):
    """
    Test the is_transition_reverse_enabled setter
    """
    # GIVEN: An instance of TransitionWidget and transition_reverse checked
    widget = TransitionWidget()

    # WHEN: The property is set
    widget.is_transition_reverse_enabled = True

    # THEN: The checkbox should be correct
    assert widget.transition_reverse_check_box.isChecked() is True


def test_transitions_enabled_check_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the transitions_enabled_check_box value is changed
    """
    # GIVEN: An instance of TransitionWidget
    widget = TransitionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The checkbox is checked
    widget.transitions_enabled_check_box.toggle()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_transition_effect_combo_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the transition_effect_combo_box value is changed
    """
    # GIVEN: An instance of TransitionWidget
    widget = TransitionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The combobox is changed
    widget.transition_effect_combo_box.setCurrentIndex(1)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_transition_speed_combo_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the transition_speed_combo_box value is changed
    """
    # GIVEN: An instance of TransitionWidget
    widget = TransitionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The combobox is changed
    widget.transition_speed_combo_box.setCurrentIndex(1)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_transition_direction_combo_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the transition_direction_combo_box value is changed
    """
    # GIVEN: An instance of TransitionWidget
    widget = TransitionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The combobox is changed
    widget.transition_direction_combo_box.setCurrentIndex(1)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_transition_reverse_check_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the transition_reverse_check_box value is changed
    """
    # GIVEN: An instance of TransitionWidget
    widget = TransitionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: The checkbox is changed
    widget.transition_reverse_check_box.toggle()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()
