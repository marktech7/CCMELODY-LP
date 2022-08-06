# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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
    # GIVEN: And instance of TransitionWidget and some mock widgets
    page = TransitionWidget()

    # WHEN: _on_transition_enabled_changed
    page._on_transition_enabled_changed(True)

    # THEN: The correct widgets should be visible
    assert page.transition_effect_label.isEnabled()
    assert page.transition_effect_combo_box.isEnabled()
    assert page.transition_speed_label.isEnabled()
    assert page.transition_speed_combo_box.isEnabled()
    assert page.transition_direction_combo_box.isEnabled()
    assert page.transition_reverse_check_box.isEnabled()


def test_get_is_transition_enabled(settings):
    """
    Test the is_transition_enabled getter
    """
    # GIVEN: A TransitionWidget instance with the transitions enabled
    page = TransitionWidget()
    page.transitions_enabled_check_box.setChecked(False)

    # WHEN: The property is accessed
    result = page.is_transition_enabled

    # THEN: The result should be correct
    assert result is False


def test_set_is_transition_enabled(settings):
    """
    Test the is_transition_enabled setter
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()
    page._on_transition_enabled_changed = MagicMock()

    # WHEN: The property is set
    page.is_transition_enabled = True

    # THEN: The result should be correct
    assert page.transitions_enabled_check_box.isChecked() is True
    page._on_transition_enabled_changed.assert_called_once_with(True)


def test_get_transition_type(settings):
    """
    Test the transition_type getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 1
    page = TransitionWidget()
    page.transition_effect_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = page.transition_type

    # THEN: The result should be correct
    assert result == TransitionType.Slide


def test_set_transition_type_int(settings):
    """
    Test the transition_type setter with an int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_type = TransitionType.Concave

    # THEN: The combobox should be correct
    assert page.transition_effect_combo_box.currentIndex() == 3


def test_set_transition_type_str(settings):
    """
    Test the transition_type setter with a str
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_type = TransitionType.to_string(TransitionType.Convex)

    # THEN: The combobox should be correct
    assert page.transition_effect_combo_box.currentIndex() == 2


def test_set_transition_type_exception(settings):
    """
    Test the transition_type setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_type must either be a string or an int'):
        page.transition_type = []


def test_get_transition_speed(settings):
    """
    Test the transition_speed getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 0
    page = TransitionWidget()
    page.transition_speed_combo_box.setCurrentIndex(0)

    # WHEN: The property is accessed
    result = page.transition_speed

    # THEN: The result should be correct
    assert result == TransitionSpeed.Normal


def test_set_transition_speed_int(settings):
    """
    Test the transition_speed setter with an int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_speed = TransitionSpeed.Fast

    # THEN: The combobox should be correct
    assert page.transition_speed_combo_box.currentIndex() == 1


def test_set_transition_speed_str(settings):
    """
    Test the transition_speed setter with a str
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_speed = TransitionSpeed.to_string(TransitionSpeed.Slow)

    # THEN: The combobox should be correct
    assert page.transition_speed_combo_box.currentIndex() == 2


def test_set_transition_speed_exception(settings):
    """
    Test the transition_speed setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_speed must either be a string or an int'):
        page.transition_speed = []


def test_get_transition_direction(settings):
    """
    Test the transition_direction getter
    """
    # GIVEN: A TransitionWidget instance with the combobox set to index 0
    page = TransitionWidget()
    page.transition_direction_combo_box.setCurrentIndex(0)

    # WHEN: The property is accessed
    result = page.transition_direction

    # THEN: The result should be correct
    assert result == TransitionDirection.Horizontal


def test_set_transition_direction_int(settings):
    """
    Test the transition_direction setter with an int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_direction = TransitionDirection.Horizontal

    # THEN: The combobox should be correct
    assert page.transition_direction_combo_box.currentIndex() == 0


def test_set_transition_direction_str(settings):
    """
    Test the transition_direction setter with a str
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    page.transition_direction = TransitionDirection.to_string(TransitionDirection.Vertical)

    # THEN: The combobox should be correct
    assert page.transition_direction_combo_box.currentIndex() == 1


def test_set_transition_direction_exception(settings):
    """
    Test the transition_direction setter with something other than a str or int
    """
    # GIVEN: A TransitionWidget instance
    page = TransitionWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='transition_direction must either be a string or an int'):
        page.transition_direction = []


def test_on_transition_reverse_getter(settings):
    """
    Test the is_transition_reverse_enabled getter
    """
    # GIVEN: And instance of TransitionWidget and transition_reverse checked
    page = TransitionWidget()
    page.transition_reverse_check_box.setChecked(True)

    # WHEN: The property is accessed
    result = page.is_transition_reverse_enabled

    # THEN: The result should be correct
    assert result is True


def test_on_transition_reverse_setter(settings):
    """
    Test the is_transition_reverse_enabled setter
    """
    # GIVEN: And instance of TransitionWidget and transition_reverse checked
    page = TransitionWidget()

    # WHEN: The property is set
    page.is_transition_reverse_enabled = True

    # THEN: The checkbox should be correct
    assert page.transition_reverse_check_box.isChecked() is True
